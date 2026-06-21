"""
Auto-aggregation pipeline for AssamVacancies.

Hard rules (do not relax):
1. Sources must be official/authoritative only — state/central government
   bodies, recruitment boards, PSUs, universities. NEVER aggregator or
   competitor listing sites.
2. We extract STRUCTURED FACTS ONLY: title, department, vacancy_count,
   qualification, last_date, application_fee, official_notification_link.
   We never copy paragraph-level text from the source.
3. Every ingested item is auto-summarised from a template using only
   those extracted fields. The source's own prose is never reused.
4. Every item is saved as `status='draft'`. Nothing auto-publishes.
5. Fuzzy duplicate detection (title + organization + posting date)
   against existing Notices to prevent re-ingesting the same item.

This module is import-safe: it must not connect on import.
"""
from __future__ import annotations

import hashlib
import logging
import re
import uuid
import urllib3
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

USER_AGENT = (
    'Mozilla/5.0 (compatible; AssamVacanciesBot/1.0; '
    '+https://assamvacancies.com/about) requests/python'
)
FETCH_TIMEOUT_SEC = 25
DETAIL_FETCH_MAX_BYTES = 600_000  # don't pull huge HTML pages
FUZZY_RATIO_THRESHOLD = 88        # title+org similarity for dup
DUP_DATE_WINDOW_DAYS = 21

# Heuristic patterns marking a link as a recruitment-related notification
HREF_HINTS = ('.pdf', 'recruit', 'advt', 'notification', 'notice',
              'vacancy', 'circular', 'employment')
TEXT_HINTS = ('recruit', 'vacancy', 'notification', 'advt', 'post',
              'admit', 'result', 'answer', 'apply')

# Things that almost certainly aren't a notification
HREF_NEGATIVE = ('mailto:', 'javascript:', 'tel:', '#',
                 '/static/', '/css/', '/js/', '.jpg', '.png', '.gif',
                 '.css', '.svg')

DATE_PATTERNS = [
    re.compile(
        r'(\d{1,2}[\s\-/.](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
        r'|January|February|March|April|May|June|July|August|September|October|November|December)'
        r'[\s\-/.]?\d{2,4})',
        re.IGNORECASE,
    ),
    re.compile(r'(\d{4}[\-/]\d{1,2}[\-/]\d{1,2})'),
    re.compile(r'(\d{1,2}[\-/.]\d{1,2}[\-/.]\d{2,4})'),
]

VACANCY_RE = re.compile(
    r'(\d{1,5})\s*(?:nos?\.?\s*of\s*)?(?:posts?|vacanc(?:y|ies)|positions?|seats?)',
    re.IGNORECASE,
)
FEE_RE = re.compile(
    r'(?:application\s*fee|fee)[\s:\-]*?(?:rs\.?|₹|inr)?\s*([0-9][0-9,]{1,6})',
    re.IGNORECASE,
)
LAST_DATE_RE = re.compile(
    r'(?:last\s*date|closing\s*date|apply\s*by|submission\s*deadline)'
    r'[\s\w]*?[:\-]?\s*([0-9]{1,2}[\sA-Za-z\-/.]{2,15}[0-9]{2,4})',
    re.IGNORECASE,
)
QUAL_KEYWORDS = (
    'graduate', 'graduation', 'post graduate', 'postgraduate',
    'bachelor', 'master', 'diploma', 'matric', 'matriculation',
    '10+2', 'hslc', 'hsslc', 'b.tech', 'b.sc', 'b.a', 'b.com',
    'm.tech', 'm.sc', 'm.a', 'm.com', 'phd', 'ph.d', 'iti',
    'ca/cma', 'ca ', 'cma', 'ssc', 'class 8', 'class 10',
    'class 12', 'mbbs', 'bds', 'llb', 'mba',
)
DEPT_KEYWORDS_RE = re.compile(
    r'(department\s+of\s+[A-Z][A-Za-z &]{3,60}|board\s+of\s+[A-Z][A-Za-z &]{3,60}'
    r'|directorate\s+of\s+[A-Z][A-Za-z &]{3,60}|ministry\s+of\s+[A-Z][A-Za-z &]{3,60})'
)


# -------------------- HELPERS --------------------
def _is_candidate_link(href: str, text: str) -> bool:
    if not href or not text or len(text) < 12:
        return False
    hl, tl = href.lower(), text.lower()
    if any(neg in hl for neg in HREF_NEGATIVE):
        return False
    return any(h in hl for h in HREF_HINTS) or any(t in tl for t in TEXT_HINTS)


def _first_date(text: str) -> str:
    if not text:
        return ''
    for pat in DATE_PATTERNS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return ''


def _nearby_text(node) -> str:
    """Aggregate text from the node's parent + immediate siblings."""
    bits: List[str] = []
    if node.parent:
        bits.append(node.parent.get_text(' ', strip=True))
    for sib in (node.previous_sibling, node.next_sibling):
        if sib is None:
            continue
        if hasattr(sib, 'get_text'):
            bits.append(sib.get_text(' ', strip=True))
        else:
            bits.append(str(sib).strip())
    return ' | '.join(b for b in bits if b)


def _dedup_key(source_url: str) -> str:
    return hashlib.sha256(source_url.encode('utf-8')).hexdigest()


def fetch_html(url: str) -> str:
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8',
        'Accept-Language': 'en-IN,en;q=0.9',
    }
    resp = requests.get(url, headers=headers, timeout=FETCH_TIMEOUT_SEC, verify=False)
    resp.raise_for_status()
    # Limit size so we never pull massive HTML
    return resp.text[:DETAIL_FETCH_MAX_BYTES]


# -------------------- PARSER --------------------
def parse_candidates(html: str, base_url: str) -> List[Dict[str, Any]]:
    """
    Generic resilient parser that scans for likely recruitment links.
    Returns up to 50 candidates with (title, source_url, near_text, candidate_date).
    """
    soup = BeautifulSoup(html, 'html.parser')
    seen: set = set()
    out: List[Dict[str, Any]] = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(' ', strip=True)
        if not _is_candidate_link(href, text):
            continue
        absolute = urljoin(base_url, href)
        if absolute in seen:
            continue
        seen.add(absolute)
        near = _nearby_text(a)
        out.append({
            'title': re.sub(r'\s+', ' ', text)[:240],
            'source_url': absolute,
            'near_text': near[:400],
            'candidate_date': _first_date(near) or _first_date(text),
        })
        if len(out) >= 50:
            break
    return out


def _extract_structured_facts(candidate: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract structured facts from the candidate's TITLE + NEAR_TEXT only.
    We deliberately stay shallow — we don't try to summarise paragraphs
    from the source. Empty fields are returned as ''.
    """
    blob = f"{candidate.get('title', '')} | {candidate.get('near_text', '')}"

    vacancy = ''
    m = VACANCY_RE.search(blob)
    if m:
        vacancy = m.group(1)

    fee = ''
    m = FEE_RE.search(blob)
    if m:
        fee = f"Rs. {m.group(1)}"

    last_date = ''
    m = LAST_DATE_RE.search(blob)
    if m:
        last_date = m.group(1).strip()
    if not last_date:
        last_date = candidate.get('candidate_date') or ''

    qualification = ''
    low = blob.lower()
    hits = [k for k in QUAL_KEYWORDS if k in low]
    if hits:
        # Title-case nice display
        qualification = ', '.join(sorted({h.strip().title() for h in hits}))[:140]

    department = ''
    m = DEPT_KEYWORDS_RE.search(blob)
    if m:
        department = m.group(0).strip()[:140]

    return {
        'vacancy_count': vacancy,
        'application_fee': fee,
        'last_date': last_date,
        'qualification': qualification,
        'department': department,
    }


def _build_summary(title: str, source_name: str, facts: Dict[str, str]) -> str:
    """
    Build a wholly-original summary from the structured facts only.
    No source paragraphs are ever reused. Empty fields are omitted.
    """
    parts: List[str] = [f"{source_name} has released an official notification: {title}."]
    if facts.get('department'):
        parts.append(f"Issuing authority: {facts['department']}.")
    if facts.get('vacancy_count'):
        parts.append(f"Total vacancies advertised: {facts['vacancy_count']}.")
    if facts.get('qualification'):
        parts.append(f"Indicative eligibility: {facts['qualification']}.")
    if facts.get('application_fee'):
        parts.append(f"Application fee mentioned: {facts['application_fee']}.")
    if facts.get('last_date'):
        parts.append(f"Last date to apply (as parsed): {facts['last_date']}.")
    parts.append(
        "Candidates must verify all details — eligibility, exam pattern, "
        "fees and important dates — directly on the official notification "
        "before applying. AssamVacancies provides this listing for "
        "informational purposes only."
    )
    return ' '.join(parts)


# -------------------- FUZZY DEDUP --------------------
async def _is_fuzzy_duplicate(db, title: str, organization: str,
                              candidate_date_str: str) -> bool:
    """
    Returns True if a recent existing notice (any status) closely matches
    by (title + organization) within ±DUP_DATE_WINDOW_DAYS of the candidate's
    date (falling back to a wider window when the date is missing).
    """
    norm_title = (title or '').strip().lower()
    norm_org = (organization or '').strip().lower()
    if not norm_title:
        return False

    # Window: ±21 days around candidate date; fallback last 60 days if absent
    window_start = datetime.utcnow() - timedelta(days=60)
    window_end = datetime.utcnow() + timedelta(days=1)
    cursor = db.notices.find(
        {'posted_date': {'$gte': window_start, '$lte': window_end}},
        {'title': 1, 'organization': 1},
    ).limit(500)
    async for n in cursor:
        et = (n.get('title') or '').strip().lower()
        eo = (n.get('organization') or '').strip().lower()
        if not et:
            continue
        title_score = fuzz.token_set_ratio(norm_title, et)
        org_score = fuzz.token_set_ratio(norm_org, eo) if norm_org and eo else 100
        if title_score >= FUZZY_RATIO_THRESHOLD and org_score >= 70:
            return True
    return False


# -------------------- RUN --------------------
def should_auto_publish(source: Dict[str, Any]) -> bool:
    """Per-source graduated-trust decision (used by candidate_to_notice).

    Modes:
      - 'always'  : publish immediately, regardless of trust.
      - 'never'   : always queue as draft for admin review.
      - 'auto'    : publish only if trust_score >= trust_threshold AND at
                    least TRUST_MIN_DECISIONS decisions have been made.
    """
    mode = (source or {}).get('auto_publish_mode', 'auto')
    if mode == 'always':
        return True
    if mode == 'never':
        return False
    approvals = source.get('approvals', 0) or 0
    rejections = source.get('rejections', 0) or 0
    total = approvals + rejections
    if total < TRUST_MIN_DECISIONS:
        return False
    score = round(100 * approvals / total) if total else 0
    return score >= int(source.get('trust_threshold', 85) or 85)


TRUST_MIN_DECISIONS = 5


def candidate_to_notice(candidate: Dict[str, Any],
                        source: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
    """Map a candidate into a Notice document + return facts used.
    Status is `published` only when the source's graduated-trust rules allow it,
    otherwise `draft` (default — admin must review)."""
    facts = _extract_structured_facts(candidate)
    title = candidate['title']
    source_url = candidate['source_url']
    summary = _build_summary(title, source.get('name', 'Source'), facts)

    auto = should_auto_publish(source)
    status = 'published' if auto else 'draft'

    notice = {
        'id': str(uuid.uuid4()),
        'slug': re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '', title.lower()).strip())[:100],
        'title': title,
        'organization': source.get('name', 'Unknown'),
        'type': source.get('default_type', 'job'),
        'category': source.get('default_category', 'govt'),
        'district': source.get('default_district', 'Kamrup Metropolitan'),
        'description': summary,
        'location': 'Assam',
        'thumbnail': '',
        'is_featured': False,
        # Job-specific
        'vacancy_count': facts['vacancy_count'],
        'eligibility': facts['qualification'],
        'age_limit': '',
        'application_fee': facts['application_fee'],
        'salary': '',
        'start_date': '',
        'last_date': facts['last_date'],
        'selection_process': '',
        'how_to_apply': '',
        'apply_link': source_url,
        'notification_link': source_url,
        'official_website': source.get('base_url', ''),
        # Other-type blanks
        'notice_date': facts['last_date'],
        'linked_job_id': None,
        'download_link': source_url if source.get('default_type', 'job') != 'job' else '',
        # Aggregator metadata
        'status': status,
        'source_id': source['id'],
        'source_url': source_url,
        'source_name': source.get('name', ''),
        'dedup_key': _dedup_key(source_url),
        'extracted_facts': facts,    # snapshot for audit
        'department': facts['department'],
        'posted_date': datetime.utcnow(),
        'views': 0,
    }
    return notice, facts


async def run_source(db, source: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch, parse and ingest one source. Returns a structured run summary."""
    started = datetime.utcnow()
    summary: Dict[str, Any] = {
        'source_id': source['id'],
        'name': source.get('name'),
        'list_url': source.get('list_url'),
        'started_at': started.isoformat(),
        'fetched': 0,
        'new_drafts': 0,
        'new_published': 0,
        'skipped_url_dup': 0,
        'skipped_fuzzy_dup': 0,
        'errors': [],
        'parse_failed': False,
        'sample_titles': [],
    }
    try:
        html = fetch_html(source['list_url'])
    except Exception as e:
        summary['errors'].append(f"fetch_error: {str(e)[:200]}")
        summary['parse_failed'] = True
        return await _finalize(db, source, summary, started)

    try:
        candidates = parse_candidates(html, source.get('base_url') or source['list_url'])
        summary['fetched'] = len(candidates)
        summary['sample_titles'] = [c['title'][:120] for c in candidates[:5]]
    except Exception as e:
        summary['errors'].append(f"parse_error: {str(e)[:200]}")
        summary['parse_failed'] = True
        return await _finalize(db, source, summary, started)

    for cand in candidates:
        try:
            # URL-level exact dedup
            existing = await db.notices.find_one({'dedup_key': _dedup_key(cand['source_url'])})
            if existing:
                summary['skipped_url_dup'] += 1
                continue
            # Fuzzy dedup (title + organization within recent window)
            if await _is_fuzzy_duplicate(db, cand['title'], source.get('name', ''),
                                         cand.get('candidate_date', '')):
                summary['skipped_fuzzy_dup'] += 1
                continue
            doc, _ = candidate_to_notice(cand, source)
            await db.notices.insert_one(doc)
            if doc['status'] == 'published':
                summary['new_published'] += 1
            else:
                summary['new_drafts'] += 1
        except Exception as e:
            summary['errors'].append(f"item_error: {str(e)[:200]}")

    return await _finalize(db, source, summary, started)


async def _finalize(db, source: Dict[str, Any], summary: Dict[str, Any],
                    started: datetime) -> Dict[str, Any]:
    summary['finished_at'] = datetime.utcnow().isoformat()
    summary['duration_sec'] = round((datetime.utcnow() - started).total_seconds(), 2)
    # Persist the run log
    run_doc = {'id': str(uuid.uuid4()), 'run_at': started, **summary}
    await db.aggregator_runs.insert_one(run_doc)
    # Snapshot last status on source
    await db.aggregator_sources.update_one(
        {'id': source['id']},
        {'$set': {
            'last_run_at': started,
            'last_run_summary': {k: summary[k] for k in
                                 ('fetched', 'new_drafts', 'new_published',
                                  'skipped_url_dup', 'skipped_fuzzy_dup',
                                  'errors', 'parse_failed')},
        }},
    )
    return summary


async def run_all_enabled(db) -> Dict[str, Any]:
    """Run every source flagged enabled=True. Returns summary."""
    cursor = db.aggregator_sources.find({'enabled': True})
    sources = [s async for s in cursor]
    runs: List[Dict[str, Any]] = []
    for s in sources:
        runs.append(await run_source(db, s))
    return {
        'started_at': datetime.utcnow().isoformat(),
        'sources_checked': len(sources),
        'runs': runs,
    }

"""
Auto-aggregation pipeline for AssamVacancies.

Pulls notification links from official recruitment-board pages, normalises
them into the Notice schema, dedupes against existing notices and writes
them either to the pending-review queue or directly to published, based on
the source's graduated trust score.
"""
from __future__ import annotations

import hashlib
import logging
import re
import uuid
import urllib3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 AssamVacanciesBot/1.0 (+https://assamvacancies.com)'
FETCH_TIMEOUT_SEC = 25

# Heuristic patterns that mark a link as a recruitment-related notification
HREF_HINTS = ('.pdf', 'recruit', 'advt', 'notification', 'notice', 'vacancy', 'circular')
TEXT_HINTS = ('recruit', 'vacancy', 'notification', 'advt', 'post', 'admit', 'result', 'answer')

# Things that almost certainly aren't a notification
HREF_NEGATIVE = ('mailto:', 'javascript:', 'tel:', '#', '/static/', '/css/', '/js/', '.jpg', '.png', '.gif')

# Common date formats found on Indian government pages
DATE_RE = re.compile(
    r'(?:(\d{1,2})[\s\-/](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec'
    r'|January|February|March|April|May|June|July|August|September|October|November|December)'
    r'[\s\-/]?(\d{4})|(\d{4})[\-/](\d{2})[\-/](\d{2})|(\d{2})[\-/](\d{2})[\-/](\d{4}))',
    re.IGNORECASE,
)


def _is_candidate_link(href: str, text: str) -> bool:
    if not href or not text or len(text) < 12:
        return False
    hl, tl = href.lower(), text.lower()
    if any(neg in hl for neg in HREF_NEGATIVE):
        return False
    return any(h in hl for h in HREF_HINTS) or any(t in tl for t in TEXT_HINTS)


def _nearby_date(a_tag) -> str:
    """Best-effort extraction of a date string near the link (parent text, prev/next sibling)."""
    bag = []
    parent = a_tag.parent
    if parent:
        bag.append(parent.get_text(' ', strip=True))
    for sib in (a_tag.previous_sibling, a_tag.next_sibling):
        if sib and hasattr(sib, 'get_text'):
            bag.append(sib.get_text(' ', strip=True))
        elif isinstance(sib, str):
            bag.append(sib.strip())
    for chunk in bag:
        m = DATE_RE.search(chunk or '')
        if m:
            return m.group(0).strip()
    return ''


def fetch_html(url: str) -> str:
    headers = {'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml'}
    resp = requests.get(url, headers=headers, timeout=FETCH_TIMEOUT_SEC, verify=False)
    resp.raise_for_status()
    return resp.text


def parse_candidates(html: str, base_url: str) -> List[Dict[str, Any]]:
    """Generic resilient parser: returns up to 50 candidate notifications."""
    soup = BeautifulSoup(html, 'html.parser')
    seen_hrefs: set = set()
    candidates: List[Dict[str, Any]] = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        text = a.get_text(' ', strip=True)
        if not _is_candidate_link(href, text):
            continue
        absolute = urljoin(base_url, href)
        if absolute in seen_hrefs:
            continue
        seen_hrefs.add(absolute)
        candidates.append({
            'title': text[:240],
            'source_url': absolute,
            'candidate_date': _nearby_date(a),
        })
        if len(candidates) >= 50:
            break
    return candidates


def dedup_key(source_url: str) -> str:
    return hashlib.sha256(source_url.encode('utf-8')).hexdigest()


def candidate_to_notice(candidate: Dict[str, Any], source: Dict[str, Any]) -> Dict[str, Any]:
    """Map a raw parser candidate into a Notice document."""
    title = candidate['title']
    source_url = candidate['source_url']
    return {
        'id': str(uuid.uuid4()),
        'slug': re.sub(r'\s+', '-', re.sub(r'[^a-z0-9\s-]', '', title.lower()).strip())[:100],
        'title': title,
        'organization': source.get('name', 'Unknown'),
        'type': source.get('default_type', 'job'),
        'category': source.get('default_category', 'govt'),
        'district': source.get('default_district', 'Kamrup Metropolitan'),
        'description': f"Notification published by {source.get('name', 'source')}. Verify all details on the official website before applying.",
        'location': 'Assam',
        'thumbnail': '',
        'is_featured': False,
        # Job-specific blanks
        'vacancy_count': '',
        'eligibility': '',
        'age_limit': '',
        'application_fee': '',
        'salary': '',
        'start_date': '',
        'last_date': candidate.get('candidate_date', ''),
        'selection_process': '',
        'how_to_apply': '',
        'apply_link': source_url,
        'notification_link': source_url,
        'official_website': source.get('base_url', ''),
        # Other-type blanks
        'notice_date': candidate.get('candidate_date', ''),
        'linked_job_id': None,
        'download_link': source_url if source.get('default_type', 'job') != 'job' else '',
        # Aggregator metadata
        'source_id': source['id'],
        'source_url': source_url,
        'dedup_key': dedup_key(source_url),
        'posted_date': datetime.utcnow(),
        'views': 0,
    }


async def run_source(db, source: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch, parse and ingest one source. Returns a result summary."""
    started = datetime.utcnow()
    summary = {'source_id': source['id'], 'name': source.get('name'),
               'fetched': 0, 'new': 0, 'skipped_dup': 0, 'auto_published': 0,
               'queued_for_review': 0, 'error': None, 'started_at': started.isoformat()}
    try:
        html = fetch_html(source['list_url'])
        candidates = parse_candidates(html, source.get('base_url') or source['list_url'])
        summary['fetched'] = len(candidates)
        trust = source.get('trust_score', 0) or 0
        threshold = source.get('trust_threshold', 80) or 80
        auto_publish = threshold > 0 and trust >= threshold
        for cand in candidates:
            key = dedup_key(cand['source_url'])
            existing = await db.notices.find_one({'dedup_key': key})
            if existing:
                summary['skipped_dup'] += 1
                continue
            doc = candidate_to_notice(cand, source)
            doc['status'] = 'published' if auto_publish else 'pending_review'
            await db.notices.insert_one(doc)
            summary['new'] += 1
            if auto_publish:
                summary['auto_published'] += 1
            else:
                summary['queued_for_review'] += 1
    except Exception as e:  # pragma: no cover
        logger.exception("source run failed")
        summary['error'] = str(e)[:300]
    finally:
        summary['finished_at'] = datetime.utcnow().isoformat()
        await db.sources.update_one(
            {'id': source['id']},
            {'$set': {
                'last_run': datetime.utcnow(),
                'last_status': summary,
            }},
        )
    return summary

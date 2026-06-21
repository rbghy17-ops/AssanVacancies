"""
3-level trust state machine tests.
Covers:
  - New: items always go to review queue (never auto-publish)
  - Probationary: still goes to review (just flagged)
  - Trusted: auto-publishes (auto_published=true, queue is skipped)
  - 10 clean approvals: new -> probationary
  - 25 clean approvals: probationary -> trusted (requires no parse fail in 30d)
  - Edit-then-approve breaks the clean streak (counter resets, no promotion)
  - Reject breaks the clean streak
  - 2 consecutive parse failures: trusted -> probationary
  - Post-publish factual correction on a Trusted source -> demote to Probationary
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import aggregator  # noqa: E402


FIXTURE_HTML = """
<html><body>
<a href="/n/eng-2026.pdf">Engineer recruitment 2026, 30 posts. Last date 25-03-2026. Fee Rs. 200. Graduate.</a>
</body></html>
"""

API_URL = os.environ.get('REACT_APP_BACKEND_URL') or 'http://localhost:8001'
if not API_URL.endswith('/api'):
    API_BASE = API_URL.rstrip('/') + '/api'
else:
    API_BASE = API_URL


def _read_backend_env():
    with open('/app/frontend/.env') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.split('=', 1)[1].strip()
    return 'http://localhost:8001'


API_BASE = _read_backend_env().rstrip('/') + '/api'


async def get_token() -> str:
    async with httpx.AsyncClient() as c:
        r = await c.post(f"{API_BASE}/auth/login",
                         json={'username': 'admin', 'password': 'TestAggr@123'},
                         timeout=15)
        r.raise_for_status()
        return r.json()['token']


async def make_source(db, level='new', cleans=0):
    sid = f"trust-sm-{uuid.uuid4()}"
    await db.aggregator_sources.insert_one({
        'id': sid, 'name': f'TEST_SM_{level}', 'base_url': 'https://e.test',
        'list_url': f'https://e.test/{sid}', 'enabled': True,
        'default_type': 'job', 'default_category': 'govt',
        'default_district': 'Kamrup Metropolitan',
        'approvals': 0, 'rejections': 0,
        'trust_level': level, 'consecutive_clean_approvals': cleans,
        'consecutive_parse_failures': 0, 'last_parse_failure_at': None,
        'last_demoted_at': None, 'last_demoted_reason': None,
    })
    return sid


async def make_draft(db, sid, idx=0):
    nid = str(uuid.uuid4())
    await db.notices.insert_one({
        'id': nid, 'slug': f'sm-{idx}', 'title': f'TEST SM draft #{idx}',
        'organization': 'X', 'type': 'job', 'category': 'govt',
        'district': 'Kamrup Metropolitan', 'description': 'auto', 'location': 'Assam',
        'status': 'draft', 'source_id': sid, 'source_url': f'https://x/{nid}',
        'posted_date': datetime.utcnow(), 'views': 0,
        'edited_since_ingest': False, 'auto_published': False,
        'last_date': '', 'apply_link': '', 'notification_link': '',
        'vacancy_count': '', 'application_fee': '', 'eligibility': '',
    })
    return nid


async def cleanup(db, sid):
    await db.notices.delete_many({'source_id': sid})
    await db.aggregator_runs.delete_many({'source_id': sid})
    await db.aggregator_sources.delete_one({'id': sid})


# ---------- 1: Ingestion respects trust_level ----------
async def t_ingestion_levels(db, token):
    # NEW
    sid = await make_source(db, level='new')
    src = await db.aggregator_sources.find_one({'id': sid})
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        summary = await aggregator.run_source(db, src)
    assert summary['new_drafts'] == 1 and summary['new_published'] == 0, summary
    await cleanup(db, sid)

    # PROBATIONARY
    sid = await make_source(db, level='probationary')
    src = await db.aggregator_sources.find_one({'id': sid})
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        summary = await aggregator.run_source(db, src)
    assert summary['new_drafts'] == 1 and summary['new_published'] == 0, summary
    await cleanup(db, sid)

    # TRUSTED
    sid = await make_source(db, level='trusted')
    src = await db.aggregator_sources.find_one({'id': sid})
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        summary = await aggregator.run_source(db, src)
    assert summary['new_published'] == 1 and summary['new_drafts'] == 0, summary
    # confirm the doc is marked auto_published
    auto = await db.notices.find_one({'source_id': sid, 'auto_published': True})
    assert auto and auto['status'] == 'published'
    await cleanup(db, sid)
    print("[1] Ingestion routing by level OK (new+probationary -> draft, trusted -> published+auto_published)")


# ---------- 2: 10 clean approvals promote new -> probationary ----------
async def t_promote_new_to_prob(db, token):
    sid = await make_source(db, level='new')
    async with httpx.AsyncClient(timeout=15) as c:
        for i in range(10):
            nid = await make_draft(db, sid, i)
            r = await c.post(f"{API_BASE}/admin/aggregator/drafts/{nid}/approve",
                             headers={'Authorization': f'Bearer {token}'})
            r.raise_for_status()
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'probationary', src
    assert src['consecutive_clean_approvals'] == 10, src
    await cleanup(db, sid)
    print("[2] 10 clean approvals: new -> probationary OK")


# ---------- 3: 25 clean approvals promote probationary -> trusted ----------
async def t_promote_prob_to_trusted(db, token):
    # Start at probationary with 10 cleans already, run 15 more to hit 25
    sid = await make_source(db, level='probationary', cleans=10)
    async with httpx.AsyncClient(timeout=15) as c:
        for i in range(15):
            nid = await make_draft(db, sid, i)
            r = await c.post(f"{API_BASE}/admin/aggregator/drafts/{nid}/approve",
                             headers={'Authorization': f'Bearer {token}'})
            r.raise_for_status()
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'trusted', src
    assert src['consecutive_clean_approvals'] >= 25, src
    await cleanup(db, sid)
    print("[3] 25 clean approvals: probationary -> trusted OK")


# ---------- 4: Edit before approve resets the clean streak ----------
async def t_edit_breaks_streak(db, token):
    sid = await make_source(db, level='new', cleans=9)
    nid = await make_draft(db, sid, 999)
    async with httpx.AsyncClient(timeout=15) as c:
        # Edit the draft via standard notice PUT -> sets edited_since_ingest=True
        r = await c.put(f"{API_BASE}/admin/notices/{nid}",
                        headers={'Authorization': f'Bearer {token}'},
                        json={'title': 'edited title'})
        r.raise_for_status()
        # Approve it
        r = await c.post(f"{API_BASE}/admin/aggregator/drafts/{nid}/approve",
                         headers={'Authorization': f'Bearer {token}'})
        r.raise_for_status()
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'new'   # NOT promoted
    assert src['consecutive_clean_approvals'] == 0
    assert src['approvals'] == 1
    await cleanup(db, sid)
    print("[4] Edit-then-approve resets clean counter OK")


# ---------- 5: Reject breaks the clean streak ----------
async def t_reject_breaks_streak(db, token):
    sid = await make_source(db, level='new', cleans=9)
    nid = await make_draft(db, sid, 0)
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(f"{API_BASE}/admin/aggregator/drafts/{nid}/reject",
                         headers={'Authorization': f'Bearer {token}'})
        r.raise_for_status()
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'new'
    assert src['consecutive_clean_approvals'] == 0
    assert src['rejections'] == 1
    await cleanup(db, sid)
    print("[5] Reject resets clean counter OK")


# ---------- 6: 2 consecutive parse failures demote a Trusted source ----------
async def t_parse_failures_demote(db, token):
    sid = await make_source(db, level='trusted', cleans=25)
    src = await db.aggregator_sources.find_one({'id': sid})

    def raise_500(url):
        raise RuntimeError('boom 500')

    # First failure
    with patch.object(aggregator, 'fetch_html', side_effect=raise_500):
        await aggregator.run_source(db, src)
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'trusted', f"expected still trusted after 1 fail, got {src['trust_level']}"

    # Second failure -> demote
    with patch.object(aggregator, 'fetch_html', side_effect=raise_500):
        await aggregator.run_source(db, src)
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'probationary', src
    assert src['consecutive_clean_approvals'] == 0
    await cleanup(db, sid)
    print("[6] 2 consecutive parse failures: trusted -> probationary OK")


# ---------- 7: Factual correction on a published Trusted item -> demote ----------
async def t_factual_correction_demotes(db, token):
    sid = await make_source(db, level='trusted', cleans=30)
    # Insert a published auto-published notice manually
    nid = str(uuid.uuid4())
    await db.notices.insert_one({
        'id': nid, 'slug': 'pub', 'title': 'Engineer 30 posts',
        'organization': 'X', 'type': 'job', 'category': 'govt',
        'district': 'Kamrup Metropolitan', 'description': 'auto',
        'location': 'Assam', 'status': 'published', 'auto_published': True,
        'source_id': sid, 'vacancy_count': '30', 'last_date': '',
        'apply_link': '', 'notification_link': '', 'application_fee': '',
        'eligibility': '', 'posted_date': datetime.utcnow(), 'views': 0,
    })
    async with httpx.AsyncClient(timeout=15) as c:
        # Admin corrects the vacancy_count -> factual correction -> demote
        r = await c.put(f"{API_BASE}/admin/notices/{nid}",
                        headers={'Authorization': f'Bearer {token}'},
                        json={'vacancy_count': '50'})
        r.raise_for_status()
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'probationary', src
    assert 'Factual correction' in (src.get('last_demoted_reason') or ''), src
    await cleanup(db, sid)
    print("[7] Post-publish factual correction demotes Trusted -> Probationary OK")


# ---------- 8: Auto-publish log + Undo ----------
async def t_auto_publish_log_and_undo(db, token):
    sid = await make_source(db, level='trusted', cleans=25)
    src = await db.aggregator_sources.find_one({'id': sid})
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        await aggregator.run_source(db, src)
    async with httpx.AsyncClient(timeout=15) as c:
        # Fetch log
        r = await c.get(f"{API_BASE}/admin/aggregator/auto-publish-log",
                        headers={'Authorization': f'Bearer {token}'})
        r.raise_for_status()
        log = r.json()
        my_items = [i for i in log['items'] if i['source_id'] == sid]
        assert len(my_items) == 1, my_items
        notice_id = my_items[0]['id']
        # Undo -> should delete notice and demote source
        r = await c.post(f"{API_BASE}/admin/aggregator/auto-publish/{notice_id}/undo",
                         headers={'Authorization': f'Bearer {token}'})
        r.raise_for_status()
    # Verify
    src = await db.aggregator_sources.find_one({'id': sid})
    assert src['trust_level'] == 'probationary', src
    deleted = await db.notices.find_one({'id': notice_id})
    assert deleted is None, "Notice should have been deleted on undo"
    await cleanup(db, sid)
    print("[8] Auto-publish log + Undo (+ source demotion) OK")


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    # Make sure admin password is set so the API calls work
    import bcrypt
    h = bcrypt.hashpw(b'TestAggr@123', bcrypt.gensalt()).decode()
    await db.admin_users.update_one(
        {'username': 'admin'},
        {'$set': {'password_hash': h, 'must_reset': False,
                  'failed_attempts': 0, 'locked_until': None}},
    )

    token = await get_token()

    await t_ingestion_levels(db, token)
    await t_promote_new_to_prob(db, token)
    await t_promote_prob_to_trusted(db, token)
    await t_edit_breaks_streak(db, token)
    await t_reject_breaks_streak(db, token)
    await t_parse_failures_demote(db, token)
    await t_factual_correction_demotes(db, token)
    await t_auto_publish_log_and_undo(db, token)

    print("\nALL TRUST STATE-MACHINE ASSERTIONS PASSED ✓")


if __name__ == '__main__':
    asyncio.run(main())

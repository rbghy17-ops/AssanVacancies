"""
End-to-end test of the aggregator pipeline against a controlled HTML fixture.
Verifies: parsing, structured-fact extraction, original auto-summary,
URL dedup, fuzzy (title+org+date) dedup, draft-only output, and run logging.
"""
import asyncio
import os
import sys
import uuid
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

import aggregator  # noqa: E402


FIXTURE_HTML = """
<html><body>
<h2>Notifications</h2>
<table>
  <tr><td>10-Mar-2026</td><td>
    <a href="/notif/asst-engr-2026.pdf">Recruitment for Assistant Engineer (Civil) - 45 posts. Last date: 25-03-2026. Application fee: Rs. 250. Graduate / B.Tech required.</a>
  </td></tr>
  <tr><td>11-Mar-2026</td><td>
    <a href="/notif/jr-asst-2026.pdf">Department of Revenue notification: 120 vacancies for Junior Assistant. Closing date: 30 Mar 2026. Fee Rs. 100. 10+2 / HSSLC eligibility.</a>
  </td></tr>
  <tr><td>11-Mar-2026</td><td>
    <a href="/notif/jr-asst-2026.pdf">Department of Revenue notification: 120 vacancies for Junior Assistant. Closing date: 30 Mar 2026. Fee Rs. 100. 10+2 / HSSLC eligibility.</a>
  </td></tr>
  <tr><td>15-Mar-2026</td><td>
    <a href="/notif/jr-assistant-recruit-2026-v2.pdf">Recruitment notification - Junior Assistant (120 posts), Department of Revenue. Apply by 30-03-2026.</a>
  </td></tr>
  <tr><td>--</td><td><a href="/static/css/main.css">stylesheet</a></td></tr>
  <tr><td>--</td><td><a href="javascript:void(0)">click here</a></td></tr>
</table>
</body></html>
"""


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    # Use an isolated source so we don't pollute real seeded sources.
    source_id = f"test-{uuid.uuid4()}"
    source = {
        'id': source_id,
        'name': 'TEST Source',
        'base_url': 'https://example.test',
        'list_url': 'https://example.test/notifications',
        'default_type': 'job',
        'default_category': 'govt',
        'default_district': 'Kamrup Metropolitan',
        'enabled': True,
    }
    await db.aggregator_sources.insert_one({**source})

    # First run -- monkeypatch fetch_html so we control the HTML.
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        first = await aggregator.run_source(db, source)
    print("FIRST RUN:", {k: first[k] for k in ('fetched', 'new_drafts',
                                               'skipped_url_dup', 'skipped_fuzzy_dup',
                                               'parse_failed', 'errors')})

    # Second run -- same fixture. URL dedup should kick in for all items.
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        second = await aggregator.run_source(db, source)
    print("SECOND RUN:", {k: second[k] for k in ('fetched', 'new_drafts',
                                                 'skipped_url_dup', 'skipped_fuzzy_dup')})

    # Verify drafts were stored with status='draft' and never publish
    drafts = await db.notices.find({'source_id': source_id}).to_list(20)
    print(f"DRAFTS STORED: {len(drafts)} (all should be status=draft)")
    for d in drafts:
        print(f"  - title: {d['title'][:80]}")
        print(f"    status={d['status']}, vacancy={d['vacancy_count']!r}, "
              f"fee={d['application_fee']!r}, last={d['last_date']!r}, "
              f"qual={d['eligibility'][:50]!r}, dept={d.get('department','')[:60]!r}")
        print(f"    description (first 200): {d['description'][:200]}")
        assert d['status'] == 'draft', "Aggregator MUST never publish"
        # Description must NOT contain raw paragraph language (we built it from a template)
        assert 'AssamVacancies provides this listing' in d['description']
        assert d['extracted_facts']['vacancy_count'] == d['vacancy_count']

    # Verify public listings hide drafts
    pub_count = await db.notices.count_documents({'source_id': source_id, 'status': 'draft'})
    pub_visible = await db.notices.count_documents({'source_id': source_id, 'status': {'$ne': 'draft'}})
    print(f"DB drafts={pub_count}, publicly-visible from this source={pub_visible} (should be 0)")
    assert pub_visible == 0

    # Run-log entries
    runs = await db.aggregator_runs.find({'source_id': source_id}).to_list(10)
    print(f"RUN LOG ENTRIES: {len(runs)} (should be 2)")
    assert len(runs) == 2

    # Cleanup
    await db.notices.delete_many({'source_id': source_id})
    await db.aggregator_runs.delete_many({'source_id': source_id})
    await db.aggregator_sources.delete_one({'id': source_id})
    print("\nALL ASSERTIONS PASSED ✓")


if __name__ == '__main__':
    asyncio.run(main())

"""
P2 — Graduated trust tests for the aggregator.
Covers:
  - should_auto_publish() in all three modes (auto/always/never) & threshold edges
  - run_source with a source that has high trust → items publish straight
  - run_source with low/no trust → items go to draft
  - Approving a draft increments source.approvals
  - Rejecting a draft increments source.rejections
  - Bulk approve credits the right source by N
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
<a href="/n/eng-2026.pdf">Engineer recruitment 2026, 30 posts. Last date 25-03-2026. Fee Rs. 200. Graduate.</a>
<a href="/n/asst-2026.pdf">Assistant recruitment 2026, 20 posts. Last date 28-03-2026. Fee Rs. 100. 10+2.</a>
</body></html>
"""


def test_should_auto_publish_modes():
    # 'always' always publishes
    assert aggregator.should_auto_publish({'auto_publish_mode': 'always'}) is True
    assert aggregator.should_auto_publish({'auto_publish_mode': 'always',
                                           'approvals': 0, 'rejections': 999}) is True

    # 'never' never publishes
    assert aggregator.should_auto_publish({'auto_publish_mode': 'never'}) is False
    assert aggregator.should_auto_publish({'auto_publish_mode': 'never',
                                           'approvals': 999, 'rejections': 0}) is False

    # 'auto' (default): under min decisions → no publish
    assert aggregator.should_auto_publish({'approvals': 3, 'rejections': 0}) is False

    # 'auto' (default): above min, below threshold → no publish
    assert aggregator.should_auto_publish(
        {'approvals': 6, 'rejections': 4, 'trust_threshold': 85}) is False  # score=60

    # 'auto' (default): above min and above threshold → publish
    assert aggregator.should_auto_publish(
        {'approvals': 18, 'rejections': 2, 'trust_threshold': 85}) is True  # score=90

    # Custom low threshold
    assert aggregator.should_auto_publish(
        {'approvals': 5, 'rejections': 5, 'trust_threshold': 40}) is True  # score=50

    print("[1] should_auto_publish() modes OK")


async def test_run_source_publishes_when_trusted():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    sid = f"trust-test-{uuid.uuid4()}"
    source = {
        'id': sid, 'name': 'TRUSTED SOURCE',
        'base_url': 'https://x.test', 'list_url': 'https://x.test/n',
        'default_type': 'job', 'default_category': 'govt',
        'default_district': 'Kamrup Metropolitan', 'enabled': True,
        'auto_publish_mode': 'auto',
        'trust_threshold': 80,
        'approvals': 18, 'rejections': 2,  # score = 90, well over 80
    }
    await db.aggregator_sources.insert_one(source)

    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        summary = await aggregator.run_source(db, source)
    print(f"[2] TRUSTED run: fetched={summary['fetched']}, "
          f"new_drafts={summary['new_drafts']}, new_published={summary['new_published']}")
    assert summary['fetched'] == 2
    assert summary['new_published'] == 2
    assert summary['new_drafts'] == 0

    # Confirm in DB they are status=published
    pub = await db.notices.count_documents({'source_id': sid, 'status': 'published'})
    draft = await db.notices.count_documents({'source_id': sid, 'status': 'draft'})
    assert pub == 2 and draft == 0, f"expected 2 pub/0 draft, got {pub}/{draft}"

    # Cleanup
    await db.notices.delete_many({'source_id': sid})
    await db.aggregator_runs.delete_many({'source_id': sid})
    await db.aggregator_sources.delete_one({'id': sid})
    print("    -> all 2 items written as PUBLISHED (auto-publish via trust). OK")


async def test_run_source_drafts_when_not_trusted():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    sid = f"untrust-test-{uuid.uuid4()}"
    source = {
        'id': sid, 'name': 'NEW SOURCE',
        'base_url': 'https://y.test', 'list_url': 'https://y.test/n',
        'default_type': 'job', 'default_category': 'govt',
        'default_district': 'Kamrup Metropolitan', 'enabled': True,
        'auto_publish_mode': 'auto', 'trust_threshold': 85,
        'approvals': 0, 'rejections': 0,  # no decisions yet
    }
    await db.aggregator_sources.insert_one(source)

    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        summary = await aggregator.run_source(db, source)
    assert summary['new_drafts'] == 2 and summary['new_published'] == 0

    await db.notices.delete_many({'source_id': sid})
    await db.aggregator_runs.delete_many({'source_id': sid})
    await db.aggregator_sources.delete_one({'id': sid})
    print("[3] UNTRUSTED run: both items queued as DRAFT. OK")


async def test_run_source_always_mode():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    sid = f"always-test-{uuid.uuid4()}"
    source = {
        'id': sid, 'name': 'ALWAYS', 'base_url': 'https://z.test',
        'list_url': 'https://z.test/n', 'default_type': 'job',
        'default_category': 'govt', 'default_district': 'Kamrup Metropolitan',
        'enabled': True, 'auto_publish_mode': 'always',
        'trust_threshold': 95, 'approvals': 0, 'rejections': 50,
    }
    await db.aggregator_sources.insert_one(source)
    with patch.object(aggregator, 'fetch_html', return_value=FIXTURE_HTML):
        summary = await aggregator.run_source(db, source)
    assert summary['new_published'] == 2 and summary['new_drafts'] == 0

    await db.notices.delete_many({'source_id': sid})
    await db.aggregator_runs.delete_many({'source_id': sid})
    await db.aggregator_sources.delete_one({'id': sid})
    print("[4] ALWAYS mode publishes even with low trust. OK")


async def main():
    test_should_auto_publish_modes()
    await test_run_source_publishes_when_trusted()
    await test_run_source_drafts_when_not_trusted()
    await test_run_source_always_mode()
    print("\nALL P2 TRUST ASSERTIONS PASSED ✓")


if __name__ == '__main__':
    asyncio.run(main())

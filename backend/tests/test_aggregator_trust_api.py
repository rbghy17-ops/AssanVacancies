"""
P2 — Graduated Trust ADMIN API tests.
Covers:
  - GET /admin/aggregator/sources returns: approvals, rejections,
    auto_publish_mode, trust_threshold, trust_score (None when <5 decisions),
    will_auto_publish.
  - POST /admin/aggregator/sources validates auto_publish_mode + trust_threshold.
  - PUT /admin/aggregator/sources/{id} validates the same.
  - POST /admin/aggregator/sources/{id}/reset-trust zeroes counters.
  - Approve increments approvals; reject increments rejections.
  - Bulk approve / reject credits the right source by N and splits across sources.
"""
import os
import sys
import uuid
import asyncio
import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', '.env'))

from motor.motor_asyncio import AsyncIOMotorClient

BASE_URL = os.environ['REACT_APP_BACKEND_URL'].rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_USER = "admin"
ADMIN_PASS = "TestAggr@123"


@pytest.fixture(scope="session")
def token():
    r = requests.post(f"{API}/auth/login",
                      json={"username": ADMIN_USER, "password": ADMIN_PASS},
                      timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="session")
def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def mongo():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    return client[os.environ["DB_NAME"]]


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_source(auth, name_suffix, mode="auto", threshold=85):
    payload = {
        "name": f"TEST_TrustSrc_{name_suffix}_{uuid.uuid4().hex[:6]}",
        "base_url": "https://t.test",
        "list_url": f"https://t.test/{uuid.uuid4().hex[:6]}",
        "enabled": True,
        "default_type": "job",
        "default_category": "govt",
        "default_district": "Kamrup Metropolitan",
        "notes": "trust api test",
        "auto_publish_mode": mode,
        "trust_threshold": threshold,
    }
    r = requests.post(f"{API}/admin/aggregator/sources",
                      headers=auth, json=payload, timeout=20)
    assert r.status_code == 200, r.text
    return r.json()


def _seed_draft(mongo, source_id, source_name, idx=0):
    import datetime
    nid = str(uuid.uuid4())
    doc = {
        "id": nid, "slug": f"trustseed-{nid[:8]}",
        "title": f"TEST_TrustSeed {idx}",
        "organization": source_name, "type": "job", "category": "govt",
        "district": "Kamrup Metropolitan",
        "description": "TEST trust seed", "location": "Assam",
        "thumbnail": "", "is_featured": False, "vacancy_count": "5",
        "eligibility": "Graduate", "age_limit": "", "application_fee": "Rs.100",
        "salary": "", "start_date": "", "last_date": "30-03-2026",
        "selection_process": "", "how_to_apply": "",
        "apply_link": "", "notification_link": "", "official_website": "",
        "notice_date": "30-03-2026", "linked_job_id": None, "download_link": "",
        "status": "draft", "source_id": source_id, "source_url": f"https://t.test/n-{nid[:6]}",
        "source_name": source_name, "dedup_key": f"d-{nid}",
        "extracted_facts": {}, "department": "",
        "posted_date": datetime.datetime.utcnow(), "views": 0,
    }
    _run(mongo.notices.insert_one(doc))
    return nid


# -------------------------------------------------------------------
class TestSourceListTrustFields:
    def test_sources_expose_trust_fields(self, auth):
        r = requests.get(f"{API}/admin/aggregator/sources",
                         headers=auth, timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list) and data
        for s in data:
            for k in ("approvals", "rejections", "auto_publish_mode",
                      "trust_threshold", "trust_score", "will_auto_publish"):
                assert k in s, f"missing {k} in source {s.get('name')}"
            assert s["auto_publish_mode"] in {"auto", "always", "never"}
            assert 0 <= s["trust_threshold"] <= 100
            assert isinstance(s["will_auto_publish"], bool)

    def test_trust_score_is_none_when_lt_5_decisions(self, auth, mongo):
        src = _make_source(auth, "noscore")
        try:
            r = requests.get(f"{API}/admin/aggregator/sources",
                             headers=auth, timeout=20)
            s = next(x for x in r.json() if x["id"] == src["id"])
            assert s["approvals"] == 0 and s["rejections"] == 0
            assert s["trust_score"] is None
            assert s["will_auto_publish"] is False
        finally:
            requests.delete(f"{API}/admin/aggregator/sources/{src['id']}",
                            headers=auth, timeout=10)


class TestValidation:
    def test_create_rejects_bad_mode(self, auth):
        payload = {
            "name": f"TEST_bad_{uuid.uuid4().hex[:6]}",
            "base_url": "https://x.test",
            "list_url": f"https://x.test/{uuid.uuid4().hex[:6]}",
            "enabled": True, "default_type": "job",
            "default_category": "govt",
            "default_district": "Kamrup Metropolitan",
            "auto_publish_mode": "bogus", "trust_threshold": 85,
        }
        r = requests.post(f"{API}/admin/aggregator/sources",
                          headers=auth, json=payload, timeout=20)
        assert r.status_code == 400

    def test_create_rejects_bad_threshold(self, auth):
        payload = {
            "name": f"TEST_bt_{uuid.uuid4().hex[:6]}",
            "base_url": "https://x.test",
            "list_url": f"https://x.test/{uuid.uuid4().hex[:6]}",
            "enabled": True, "default_type": "job",
            "default_category": "govt",
            "default_district": "Kamrup Metropolitan",
            "auto_publish_mode": "auto", "trust_threshold": 150,
        }
        r = requests.post(f"{API}/admin/aggregator/sources",
                          headers=auth, json=payload, timeout=20)
        assert r.status_code == 400

    def test_update_rejects_bad_values(self, auth):
        src = _make_source(auth, "upd")
        try:
            r = requests.put(f"{API}/admin/aggregator/sources/{src['id']}",
                             headers=auth, json={"auto_publish_mode": "x"},
                             timeout=20)
            assert r.status_code == 400
            r = requests.put(f"{API}/admin/aggregator/sources/{src['id']}",
                             headers=auth, json={"trust_threshold": -5},
                             timeout=20)
            assert r.status_code == 400
            # Valid update persists
            r = requests.put(f"{API}/admin/aggregator/sources/{src['id']}",
                             headers=auth,
                             json={"auto_publish_mode": "always",
                                   "trust_threshold": 50}, timeout=20)
            assert r.status_code == 200
            body = r.json()
            assert body["auto_publish_mode"] == "always"
            assert body["trust_threshold"] == 50
        finally:
            requests.delete(f"{API}/admin/aggregator/sources/{src['id']}",
                            headers=auth, timeout=10)


class TestApproveRejectCounters:
    def test_approve_increments_approvals(self, auth, mongo):
        src = _make_source(auth, "appcnt")
        try:
            nid = _seed_draft(mongo, src["id"], src["name"], 0)
            r = requests.post(f"{API}/admin/aggregator/drafts/{nid}/approve",
                              headers=auth, timeout=20)
            assert r.status_code == 200
            doc = _run(mongo.aggregator_sources.find_one({"id": src["id"]}))
            assert doc["approvals"] == 1
            assert doc.get("rejections", 0) == 0
            _run(mongo.notices.delete_one({"id": nid}))
        finally:
            requests.delete(f"{API}/admin/aggregator/sources/{src['id']}",
                            headers=auth, timeout=10)

    def test_reject_increments_rejections(self, auth, mongo):
        src = _make_source(auth, "rejcnt")
        try:
            nid = _seed_draft(mongo, src["id"], src["name"], 0)
            r = requests.post(f"{API}/admin/aggregator/drafts/{nid}/reject",
                              headers=auth, timeout=20)
            assert r.status_code == 200
            doc = _run(mongo.aggregator_sources.find_one({"id": src["id"]}))
            assert doc.get("approvals", 0) == 0
            assert doc["rejections"] == 1
        finally:
            requests.delete(f"{API}/admin/aggregator/sources/{src['id']}",
                            headers=auth, timeout=10)

    def test_reset_trust_zeroes_counters(self, auth, mongo):
        src = _make_source(auth, "rst")
        try:
            # seed direct counters
            _run(mongo.aggregator_sources.update_one(
                {"id": src["id"]},
                {"$set": {"approvals": 7, "rejections": 3}}))
            r = requests.post(
                f"{API}/admin/aggregator/sources/{src['id']}/reset-trust",
                headers=auth, timeout=20)
            assert r.status_code == 200
            doc = _run(mongo.aggregator_sources.find_one({"id": src["id"]}))
            assert doc["approvals"] == 0
            assert doc["rejections"] == 0
        finally:
            requests.delete(f"{API}/admin/aggregator/sources/{src['id']}",
                            headers=auth, timeout=10)


class TestBulkCounters:
    def test_bulk_approve_credits_per_source(self, auth, mongo):
        s1 = _make_source(auth, "bulkA")
        s2 = _make_source(auth, "bulkB")
        seeded = []
        try:
            ids_s1 = [_seed_draft(mongo, s1["id"], s1["name"], i) for i in range(3)]
            ids_s2 = [_seed_draft(mongo, s2["id"], s2["name"], i) for i in range(2)]
            seeded = ids_s1 + ids_s2

            r = requests.post(f"{API}/admin/aggregator/drafts/bulk",
                              headers=auth,
                              json={"ids": seeded, "action": "approve"},
                              timeout=30)
            assert r.status_code == 200, r.text
            assert r.json()["affected"] == 5

            d1 = _run(mongo.aggregator_sources.find_one({"id": s1["id"]}))
            d2 = _run(mongo.aggregator_sources.find_one({"id": s2["id"]}))
            assert d1["approvals"] == 3, d1
            assert d2["approvals"] == 2, d2
            assert d1.get("rejections", 0) == 0
            assert d2.get("rejections", 0) == 0
        finally:
            _run(mongo.notices.delete_many({"id": {"$in": seeded}}))
            requests.delete(f"{API}/admin/aggregator/sources/{s1['id']}",
                            headers=auth, timeout=10)
            requests.delete(f"{API}/admin/aggregator/sources/{s2['id']}",
                            headers=auth, timeout=10)

    def test_bulk_reject_credits_per_source(self, auth, mongo):
        s1 = _make_source(auth, "bulkRA")
        s2 = _make_source(auth, "bulkRB")
        seeded = []
        try:
            ids_s1 = [_seed_draft(mongo, s1["id"], s1["name"], i) for i in range(2)]
            ids_s2 = [_seed_draft(mongo, s2["id"], s2["name"], i) for i in range(4)]
            seeded = ids_s1 + ids_s2

            r = requests.post(f"{API}/admin/aggregator/drafts/bulk",
                              headers=auth,
                              json={"ids": seeded, "action": "reject"},
                              timeout=30)
            assert r.status_code == 200
            assert r.json()["affected"] == 6

            d1 = _run(mongo.aggregator_sources.find_one({"id": s1["id"]}))
            d2 = _run(mongo.aggregator_sources.find_one({"id": s2["id"]}))
            assert d1["rejections"] == 2
            assert d2["rejections"] == 4
        finally:
            # already hard-deleted by reject, but be safe
            _run(mongo.notices.delete_many({"id": {"$in": seeded}}))
            requests.delete(f"{API}/admin/aggregator/sources/{s1['id']}",
                            headers=auth, timeout=10)
            requests.delete(f"{API}/admin/aggregator/sources/{s2['id']}",
                            headers=auth, timeout=10)


class TestPublicHidesDrafts:
    def test_public_notices_only_published(self):
        r = requests.get(f"{API}/notices?limit=200", timeout=20)
        assert r.status_code == 200
        data = r.json()
        items = data if isinstance(data, list) else data.get("notices") or data.get("items") or []
        for it in items:
            if isinstance(it, dict) and "status" in it:
                assert it["status"] != "draft"

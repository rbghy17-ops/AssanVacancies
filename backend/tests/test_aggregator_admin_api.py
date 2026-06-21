"""
Backend API tests for the Aggregator admin endpoints + Review Queue flow.
Covers: sources CRUD, run, run-all, runs, drafts (filter), approve, reject,
bulk action, settings round-trip + validation, public hiding of drafts, auth.
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

from motor.motor_asyncio import AsyncIOMotorClient

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://assam-careers-2.preview.emergentagent.com').rstrip('/')
API = f"{BASE_URL}/api"

ADMIN_USER = "admin"
ADMIN_PASS = "TestAggr@123"


@pytest.fixture(scope="session")
def token():
    r = requests.post(f"{API}/auth/login", json={"username": ADMIN_USER, "password": ADMIN_PASS}, timeout=30)
    assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
    return r.json()["token"]


@pytest.fixture(scope="session")
def auth(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def mongo():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]
    return db


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------- AUTH GUARD ----------
class TestAuth:
    def test_sources_requires_auth(self):
        r = requests.get(f"{API}/admin/aggregator/sources", timeout=20)
        assert r.status_code in (401, 403)

    def test_drafts_requires_auth(self):
        r = requests.get(f"{API}/admin/aggregator/drafts", timeout=20)
        assert r.status_code in (401, 403)

    def test_settings_requires_auth(self):
        r = requests.get(f"{API}/admin/aggregator/settings", timeout=20)
        assert r.status_code in (401, 403)


# ---------- SOURCES ----------
class TestSources:
    def test_list_sources_has_seeded_two(self, auth):
        r = requests.get(f"{API}/admin/aggregator/sources", headers=auth, timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        names = {s["name"] for s in data}
        # APSC + SLPRB must be seeded
        assert any("APSC" in n for n in names), f"APSC not found in {names}"
        assert any("SLPRB" in n for n in names), f"SLPRB not found in {names}"

    def test_full_crud_on_source(self, auth):
        # CREATE
        payload = {
            "name": f"TEST_Source_{uuid.uuid4().hex[:6]}",
            "base_url": "https://example.test",
            "list_url": f"https://example.test/list-{uuid.uuid4().hex[:6]}",
            "enabled": True,
            "default_type": "job",
            "default_category": "govt",
            "default_district": "Kamrup Metropolitan",
            "notes": "test"
        }
        r = requests.post(f"{API}/admin/aggregator/sources", headers=auth, json=payload, timeout=20)
        assert r.status_code == 200, r.text
        created = r.json()
        sid = created["id"]
        assert created["name"] == payload["name"]

        # UPDATE
        r = requests.put(f"{API}/admin/aggregator/sources/{sid}", headers=auth,
                         json={"notes": "updated", "enabled": False}, timeout=20)
        assert r.status_code == 200
        assert r.json()["notes"] == "updated"
        assert r.json()["enabled"] is False

        # DELETE
        r = requests.delete(f"{API}/admin/aggregator/sources/{sid}", headers=auth, timeout=20)
        assert r.status_code == 200
        # GET delete again
        r = requests.delete(f"{API}/admin/aggregator/sources/{sid}", headers=auth, timeout=20)
        assert r.status_code == 404

    def test_run_single_source_returns_summary(self, auth):
        # Run on first seeded source — may fail to fetch, but response shape must be intact.
        r = requests.get(f"{API}/admin/aggregator/sources", headers=auth, timeout=20)
        srcs = r.json()
        assert len(srcs) >= 1
        sid = srcs[0]["id"]
        r = requests.post(f"{API}/admin/aggregator/sources/{sid}/run", headers=auth, timeout=90)
        assert r.status_code == 200, r.text
        body = r.json()
        for key in ("fetched", "new_drafts", "skipped_url_dup", "skipped_fuzzy_dup", "errors"):
            assert key in body, f"missing key {key} in {body}"

    def test_run_all(self, auth):
        r = requests.post(f"{API}/admin/aggregator/run-all", headers=auth, timeout=180)
        assert r.status_code == 200
        body = r.json()
        assert "sources_checked" in body
        assert "runs" in body and isinstance(body["runs"], list)


# ---------- RUNS LOG ----------
class TestRuns:
    def test_runs_returned_with_run_at(self, auth):
        r = requests.get(f"{API}/admin/aggregator/runs?limit=10", headers=auth, timeout=20)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # We just ran in previous test class, so should be >=1
        if data:
            assert "run_at" in data[0]
            assert "parse_failed" in data[0]


# ---------- DRAFTS + APPROVE/REJECT/BULK ----------
class TestDraftsFlow:
    """Seed mock drafts directly in MongoDB and exercise the full UI flow."""

    @pytest.fixture(scope="class")
    def seeded(self, auth, mongo):
        # Use a real seeded source id
        r = requests.get(f"{API}/admin/aggregator/sources", headers=auth, timeout=20)
        sources = r.json()
        assert sources, "no seeded sources found"
        sid = sources[0]["id"]
        sname = sources[0]["name"]

        ids = []
        for i in range(4):
            nid = str(uuid.uuid4())
            ids.append(nid)
            doc = {
                "id": nid,
                "slug": f"test-draft-{i}-{nid[:6]}",
                "title": f"TEST_Draft Notification {i} for QA",
                "organization": sname,
                "type": "job",
                "category": "govt",
                "district": "Kamrup Metropolitan",
                "description": "TEST draft used for review queue QA. AssamVacancies provides this listing.",
                "location": "Assam",
                "thumbnail": "",
                "is_featured": False,
                "vacancy_count": str(10 + i),
                "eligibility": "Graduate",
                "age_limit": "",
                "application_fee": "Rs. 100",
                "salary": "",
                "start_date": "",
                "last_date": "30-03-2026",
                "selection_process": "",
                "how_to_apply": "",
                "apply_link": f"https://example.test/apply-{i}",
                "notification_link": f"https://example.test/notif-{i}",
                "official_website": "",
                "notice_date": "30-03-2026",
                "linked_job_id": None,
                "download_link": "",
                "status": "draft",
                "source_id": sid,
                "source_url": f"https://example.test/notif-{i}-{nid[:6]}",
                "source_name": sname,
                "dedup_key": f"test-dedup-{nid}",
                "extracted_facts": {"vacancy_count": str(10 + i)},
                "department": "Department of Testing",
                "posted_date": __import__("datetime").datetime.utcnow(),
                "views": 0,
            }
            _run(mongo.notices.insert_one(doc))

        yield {"source_id": sid, "ids": ids}

        # cleanup any leftovers
        _run(mongo.notices.delete_many({"id": {"$in": ids}}))

    def test_drafts_listing_and_filter(self, auth, seeded):
        # No filter
        r = requests.get(f"{API}/admin/aggregator/drafts?limit=100", headers=auth, timeout=20)
        assert r.status_code == 200
        body = r.json()
        assert "drafts" in body and "total" in body
        found_ids = {d["id"] for d in body["drafts"]}
        for nid in seeded["ids"]:
            assert nid in found_ids

        # Filter by source_id
        r = requests.get(f"{API}/admin/aggregator/drafts?limit=100&source_id={seeded['source_id']}",
                         headers=auth, timeout=20)
        assert r.status_code == 200
        body = r.json()
        for d in body["drafts"]:
            assert d["source_id"] == seeded["source_id"]

    def test_drafts_hidden_from_public_list(self, seeded):
        r = requests.get(f"{API}/notices?limit=200", timeout=20)
        assert r.status_code == 200
        data = r.json()
        items = data if isinstance(data, list) else data.get("notices") or data.get("items") or []
        item_ids = {i["id"] for i in items if isinstance(i, dict)}
        for nid in seeded["ids"]:
            assert nid not in item_ids, f"draft {nid} leaked into public list"

    def test_draft_404_on_public_detail(self, seeded):
        nid = seeded["ids"][0]
        r = requests.get(f"{API}/notices/{nid}", timeout=20)
        assert r.status_code == 404

    def test_approve_single_draft(self, auth, seeded, mongo):
        nid = seeded["ids"][0]
        r = requests.post(f"{API}/admin/aggregator/drafts/{nid}/approve", headers=auth, timeout=20)
        assert r.status_code == 200
        # verify status
        doc = _run(mongo.notices.find_one({"id": nid}))
        assert doc["status"] == "published"
        assert doc.get("approved_by") == "admin"
        # public detail should now return 200
        r = requests.get(f"{API}/notices/{nid}", timeout=20)
        assert r.status_code == 200
        # cleanup: remove
        _run(mongo.notices.delete_one({"id": nid}))

    def test_reject_single_draft(self, auth, seeded, mongo):
        nid = seeded["ids"][1]
        r = requests.post(f"{API}/admin/aggregator/drafts/{nid}/reject", headers=auth, timeout=20)
        assert r.status_code == 200
        doc = _run(mongo.notices.find_one({"id": nid}))
        assert doc is None  # hard delete

    def test_bulk_approve_and_reject(self, auth, seeded, mongo):
        # remaining ids[2], ids[3]
        a, b = seeded["ids"][2], seeded["ids"][3]
        r = requests.post(f"{API}/admin/aggregator/drafts/bulk", headers=auth,
                          json={"ids": [a], "action": "approve"}, timeout=20)
        assert r.status_code == 200
        body = r.json()
        assert body["success"] is True
        assert body["affected"] == 1
        doc = _run(mongo.notices.find_one({"id": a}))
        assert doc["status"] == "published"

        r = requests.post(f"{API}/admin/aggregator/drafts/bulk", headers=auth,
                          json={"ids": [b], "action": "reject"}, timeout=20)
        assert r.status_code == 200
        assert r.json()["affected"] == 1
        assert _run(mongo.notices.find_one({"id": b})) is None

        # invalid action
        r = requests.post(f"{API}/admin/aggregator/drafts/bulk", headers=auth,
                          json={"ids": [a], "action": "burn"}, timeout=20)
        assert r.status_code == 400

        # cleanup published one
        _run(mongo.notices.delete_one({"id": a}))


# ---------- SETTINGS ----------
class TestSettings:
    def test_round_trip_settings(self, auth):
        # Get current
        r = requests.get(f"{API}/admin/aggregator/settings", headers=auth, timeout=20)
        assert r.status_code == 200
        original = r.json()

        # Set new
        r = requests.put(f"{API}/admin/aggregator/settings", headers=auth,
                        json={"enabled": False, "interval_hours": 6}, timeout=20)
        assert r.status_code == 200
        body = r.json()
        assert body["enabled"] is False
        assert body["interval_hours"] == 6

        # Get back
        r = requests.get(f"{API}/admin/aggregator/settings", headers=auth, timeout=20)
        assert r.json()["interval_hours"] == 6

        # Validation: outside 1..168
        r = requests.put(f"{API}/admin/aggregator/settings", headers=auth,
                        json={"enabled": False, "interval_hours": 0}, timeout=20)
        assert r.status_code == 400
        r = requests.put(f"{API}/admin/aggregator/settings", headers=auth,
                        json={"enabled": False, "interval_hours": 200}, timeout=20)
        assert r.status_code == 400

        # Restore (best-effort)
        requests.put(f"{API}/admin/aggregator/settings", headers=auth,
                    json={"enabled": original.get("enabled", False),
                          "interval_hours": original.get("interval_hours", 24)}, timeout=20)

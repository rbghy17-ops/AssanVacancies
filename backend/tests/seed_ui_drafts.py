"""Seed 3 mock drafts directly in MongoDB for UI testing."""
import asyncio
import os
import sys
import uuid
from datetime import datetime
sys.path.insert(0, '/app/backend')
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
from motor.motor_asyncio import AsyncIOMotorClient


async def main():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]

    # cleanup previous test drafts
    res = await db.notices.delete_many({"slug": {"$regex": "^uitest-draft-"}})
    print(f"cleaned previous test drafts: {res.deleted_count}")

    sources = await db.aggregator_sources.find({}).to_list(10)
    if not sources:
        print("NO SOURCES SEEDED")
        return
    s = sources[0]
    sid, sname = s['id'], s['name']
    print(f"using source: {sname} ({sid})")

    ids = []
    for i in range(3):
        nid = str(uuid.uuid4())
        ids.append(nid)
        doc = {
            "id": nid,
            "slug": f"uitest-draft-{i}-{nid[:6]}",
            "title": f"UITEST_Draft Notification {i} for QA Review",
            "organization": sname,
            "type": "job", "category": "govt", "district": "Kamrup Metropolitan",
            "description": "UI TEST draft. AssamVacancies provides this listing.",
            "location": "Assam", "thumbnail": "", "is_featured": False,
            "vacancy_count": str(50 + i), "eligibility": "Graduate",
            "age_limit": "", "application_fee": "Rs. 250",
            "salary": "", "start_date": "", "last_date": "31-03-2026",
            "selection_process": "", "how_to_apply": "",
            "apply_link": f"https://example.test/apply-{i}",
            "notification_link": f"https://example.test/notif-{i}",
            "official_website": "",
            "notice_date": "31-03-2026", "linked_job_id": None, "download_link": "",
            "status": "draft", "source_id": sid,
            "source_url": f"https://example.test/notif-{i}-{nid[:6]}",
            "source_name": sname,
            "dedup_key": f"uitest-dedup-{nid}",
            "extracted_facts": {"vacancy_count": str(50 + i)},
            "department": "Department of Testing",
            "posted_date": datetime.utcnow(), "views": 0,
        }
        await db.notices.insert_one(doc)
    print(f"seeded {len(ids)} drafts")
    print("IDS:", ids)


asyncio.run(main())

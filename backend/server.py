from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import jwt
import hashlib
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'assamvacancies-secret-key-2025')
JWT_ALGO = 'HS256'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = hashlib.sha256('admin'.encode()).hexdigest()

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# -------------------- MODELS --------------------
class JobBase(BaseModel):
    title: str
    organization: str
    category: str  # govt, private, defence, banking, railway, teaching, police
    job_type: str = "recruitment"  # recruitment, admit_card, result, answer_key, admission, scholarship
    description: str
    qualification: str = ""
    age_limit: str = ""
    application_fee: str = ""
    vacancy_count: str = ""
    salary: str = ""
    location: str = "Assam"
    last_date: str = ""
    start_date: str = ""
    apply_link: str = ""
    notification_link: str = ""
    official_website: str = ""
    thumbnail: str = ""
    important_dates: Optional[dict] = None
    how_to_apply: str = ""
    selection_process: str = ""

class Job(JobBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str = ""
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    views: int = 0
    is_featured: bool = False

class JobCreate(JobBase):
    is_featured: bool = False

class JobUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    category: Optional[str] = None
    job_type: Optional[str] = None
    description: Optional[str] = None
    qualification: Optional[str] = None
    age_limit: Optional[str] = None
    application_fee: Optional[str] = None
    vacancy_count: Optional[str] = None
    salary: Optional[str] = None
    location: Optional[str] = None
    last_date: Optional[str] = None
    start_date: Optional[str] = None
    apply_link: Optional[str] = None
    notification_link: Optional[str] = None
    official_website: Optional[str] = None
    thumbnail: Optional[str] = None
    how_to_apply: Optional[str] = None
    selection_process: Optional[str] = None
    is_featured: Optional[bool] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class ContactMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    subject: str = ""
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContactCreate(BaseModel):
    name: str
    email: str
    subject: str = ""
    message: str

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    description: str = ""

# -------------------- HELPERS --------------------
def create_slug(title: str) -> str:
    import re
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    return s[:100]

def serialize_job(job: dict) -> dict:
    if not job:
        return job
    job.pop('_id', None)
    if 'posted_date' in job and isinstance(job['posted_date'], datetime):
        job['posted_date'] = job['posted_date'].isoformat()
    return job

def create_jwt(username: str) -> str:
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
        if payload.get('username') != ADMIN_USERNAME:
            raise HTTPException(status_code=401, detail="Invalid token")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# -------------------- AUTH --------------------
@api_router.post("/auth/login")
async def login(req: LoginRequest):
    pwd_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if req.username == ADMIN_USERNAME and pwd_hash == ADMIN_PASSWORD_HASH:
        token = create_jwt(req.username)
        return {"token": token, "username": req.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@api_router.get("/auth/verify")
async def verify(admin=Depends(verify_admin)):
    return {"username": admin['username']}

# -------------------- PUBLIC JOBS --------------------
@api_router.get("/jobs")
async def list_jobs(
    category: Optional[str] = None,
    job_type: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0
):
    query = {}
    if category:
        query['category'] = category
    if job_type:
        query['job_type'] = job_type
    if featured is not None:
        query['is_featured'] = featured
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'organization': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}}
        ]
    cursor = db.jobs.find(query).sort('posted_date', -1).skip(skip).limit(limit)
    jobs = [serialize_job(j) async for j in cursor]
    total = await db.jobs.count_documents(query)
    return {"jobs": jobs, "total": total}

@api_router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = await db.jobs.find_one({'id': job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.jobs.update_one({'id': job_id}, {'$inc': {'views': 1}})
    return serialize_job(job)

@api_router.get("/stats")
async def get_stats():
    total = await db.jobs.count_documents({})
    by_category = {}
    for cat in ['govt', 'private', 'defence', 'banking', 'railway', 'teaching', 'police']:
        by_category[cat] = await db.jobs.count_documents({'category': cat})
    by_type = {}
    for t in ['recruitment', 'admit_card', 'result', 'answer_key', 'admission', 'scholarship']:
        by_type[t] = await db.jobs.count_documents({'job_type': t})
    messages_count = await db.contacts.count_documents({})
    return {
        "total_jobs": total,
        "by_category": by_category,
        "by_type": by_type,
        "messages": messages_count
    }

# -------------------- ADMIN JOBS CRUD --------------------
@api_router.post("/admin/jobs")
async def create_job(job: JobCreate, admin=Depends(verify_admin)):
    job_obj = Job(**job.dict())
    job_obj.slug = create_slug(job.title)
    doc = job_obj.dict()
    await db.jobs.insert_one(doc)
    return serialize_job(doc)

@api_router.put("/admin/jobs/{job_id}")
async def update_job(job_id: str, job: JobUpdate, admin=Depends(verify_admin)):
    updates = {k: v for k, v in job.dict().items() if v is not None}
    if 'title' in updates:
        updates['slug'] = create_slug(updates['title'])
    result = await db.jobs.update_one({'id': job_id}, {'$set': updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    updated = await db.jobs.find_one({'id': job_id})
    return serialize_job(updated)

@api_router.delete("/admin/jobs/{job_id}")
async def delete_job(job_id: str, admin=Depends(verify_admin)):
    result = await db.jobs.delete_one({'id': job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"success": True}

# -------------------- CONTACT --------------------
@api_router.post("/contact")
async def submit_contact(msg: ContactCreate):
    obj = ContactMessage(**msg.dict())
    await db.contacts.insert_one(obj.dict())
    return {"success": True, "id": obj.id}

@api_router.get("/admin/contacts")
async def list_contacts(admin=Depends(verify_admin)):
    cursor = db.contacts.find().sort('created_at', -1)
    out = []
    async for c in cursor:
        c.pop('_id', None)
        if 'created_at' in c and isinstance(c['created_at'], datetime):
            c['created_at'] = c['created_at'].isoformat()
        out.append(c)
    return out

@api_router.delete("/admin/contacts/{contact_id}")
async def delete_contact(contact_id: str, admin=Depends(verify_admin)):
    await db.contacts.delete_one({'id': contact_id})
    return {"success": True}

@api_router.get("/")
async def root():
    return {"message": "AssamVacancies API"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

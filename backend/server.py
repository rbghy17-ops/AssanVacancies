from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import jwt
import bcrypt
import re
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

JWT_SECRET = os.environ.get('JWT_SECRET', 'assamvacancies-secret-key-2025-change-me')
JWT_ALGO = 'HS256'
TOKEN_TTL_MIN = 30  # 30-minute idle timeout
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MIN = 15
BOOTSTRAP_USERNAME = 'admin'
BOOTSTRAP_PASSWORD = 'admin'  # one-time bootstrap; force-reset on first login

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()
logger = logging.getLogger(__name__)


# -------------------- HTTPS / Security Headers --------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Backend is served via TLS-terminating ingress; we honor X-Forwarded-Proto
        # and set HSTS so browsers refuse plain HTTP for one year.
        response = await call_next(request)
        # HSTS - browser will only use HTTPS for 1 year
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response


# -------------------- MODELS --------------------
class JobBase(BaseModel):
    title: str
    organization: str
    category: str
    job_type: str = "recruitment"
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


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str


class ContactCreate(BaseModel):
    name: str
    email: str
    subject: str = ""
    message: str


# -------------------- HELPERS --------------------
def create_slug(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    return s[:100]


def serialize(doc: dict) -> dict:
    if not doc:
        return doc
    doc.pop('_id', None)
    for k, v in list(doc.items()):
        if isinstance(v, datetime):
            doc[k] = v.isoformat()
    return doc


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def create_jwt(username: str, must_reset: bool = False) -> str:
    now = datetime.utcnow()
    payload = {
        'username': username,
        'must_reset': must_reset,
        'iat': now,
        'exp': now + timedelta(minutes=TOKEN_TTL_MIN),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])


def client_ip(request: Request) -> str:
    fwd = request.headers.get('x-forwarded-for', '')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


async def log_login_attempt(username: str, ip: str, success: bool, user_agent: str, reason: str = ""):
    await db.login_logs.insert_one({
        'id': str(uuid.uuid4()),
        'username': username,
        'ip': ip,
        'success': success,
        'reason': reason,
        'user_agent': user_agent[:200],
        'timestamp': datetime.utcnow(),
    })


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = decode_jwt(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db.admin_users.find_one({'username': payload.get('username')})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {'username': user['username'], 'must_reset': user.get('must_reset', False), 'payload': payload}


async def require_full_admin(admin=Depends(get_current_admin)) -> dict:
    """For admin actions: must NOT be in must_reset mode."""
    if admin['must_reset']:
        raise HTTPException(status_code=403, detail="Password reset required before performing admin actions")
    return admin


# -------------------- STARTUP --------------------
@app.on_event("startup")
async def on_startup():
    # Indexes
    await db.admin_users.create_index('username', unique=True)
    await db.jobs.create_index('id', unique=True)
    await db.login_logs.create_index([('timestamp', -1)])
    # Bootstrap admin user if not exists
    existing = await db.admin_users.find_one({'username': BOOTSTRAP_USERNAME})
    if not existing:
        await db.admin_users.insert_one({
            'username': BOOTSTRAP_USERNAME,
            'password_hash': hash_password(BOOTSTRAP_PASSWORD),
            'must_reset': True,  # force password change on first login
            'failed_attempts': 0,
            'locked_until': None,
            'last_login': None,
            'created_at': datetime.utcnow(),
        })
        logger.info("Bootstrap admin user created (must reset on first login)")


# -------------------- AUTH --------------------
@api_router.post("/auth/login")
async def login(req: LoginRequest, request: Request):
    ip = client_ip(request)
    ua = request.headers.get('user-agent', '')

    user = await db.admin_users.find_one({'username': req.username})
    if not user:
        await log_login_attempt(req.username, ip, False, ua, 'user_not_found')
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Check lock
    locked_until = user.get('locked_until')
    if locked_until and locked_until > datetime.utcnow():
        remaining = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        await log_login_attempt(req.username, ip, False, ua, 'account_locked')
        raise HTTPException(status_code=423, detail=f"Account locked. Try again in {remaining} minute(s).")

    # Verify password
    if not verify_password(req.password, user['password_hash']):
        new_attempts = user.get('failed_attempts', 0) + 1
        update = {'failed_attempts': new_attempts}
        reason = 'wrong_password'
        if new_attempts >= MAX_FAILED_ATTEMPTS:
            update['locked_until'] = datetime.utcnow() + timedelta(minutes=LOCKOUT_MIN)
            update['failed_attempts'] = 0  # reset counter, lock takes effect
            reason = 'wrong_password_locked'
        await db.admin_users.update_one({'username': req.username}, {'$set': update})
        await log_login_attempt(req.username, ip, False, ua, reason)
        if reason == 'wrong_password_locked':
            raise HTTPException(status_code=423, detail=f"Too many failed attempts. Account locked for {LOCKOUT_MIN} minutes.")
        attempts_left = MAX_FAILED_ATTEMPTS - new_attempts
        raise HTTPException(status_code=401, detail=f"Invalid credentials. {attempts_left} attempt(s) left.")

    # Success
    await db.admin_users.update_one(
        {'username': req.username},
        {'$set': {'failed_attempts': 0, 'locked_until': None, 'last_login': datetime.utcnow()}},
    )
    await log_login_attempt(req.username, ip, True, ua, 'success')
    must_reset = user.get('must_reset', False)
    token = create_jwt(req.username, must_reset)
    return {'token': token, 'username': req.username, 'must_reset': must_reset, 'ttl_min': TOKEN_TTL_MIN}


@api_router.get("/auth/verify")
async def verify(admin=Depends(get_current_admin)):
    return {'username': admin['username'], 'must_reset': admin['must_reset']}


@api_router.post("/auth/refresh")
async def refresh(admin=Depends(get_current_admin)):
    """Refresh token to extend the 30-min idle timeout."""
    token = create_jwt(admin['username'], admin['must_reset'])
    return {'token': token, 'ttl_min': TOKEN_TTL_MIN}


@api_router.post("/auth/change-password")
async def change_password(req: PasswordChangeRequest, admin=Depends(get_current_admin)):
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    if req.old_password == req.new_password:
        raise HTTPException(status_code=400, detail="New password must differ from old password")
    user = await db.admin_users.find_one({'username': admin['username']})
    if not verify_password(req.old_password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Old password incorrect")
    await db.admin_users.update_one(
        {'username': admin['username']},
        {'$set': {
            'password_hash': hash_password(req.new_password),
            'must_reset': False,
            'password_changed_at': datetime.utcnow(),
        }},
    )
    token = create_jwt(admin['username'], False)
    return {'success': True, 'token': token, 'ttl_min': TOKEN_TTL_MIN}


# -------------------- PUBLIC JOBS --------------------
@api_router.get("/jobs")
async def list_jobs(
    category: Optional[str] = None,
    job_type: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0,
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
            {'description': {'$regex': search, '$options': 'i'}},
        ]
    cursor = db.jobs.find(query).sort('posted_date', -1).skip(skip).limit(limit)
    jobs = [serialize(j) async for j in cursor]
    total = await db.jobs.count_documents(query)
    return {"jobs": jobs, "total": total}


@api_router.get("/jobs/{job_id}")
async def get_job(job_id: str):
    job = await db.jobs.find_one({'id': job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    await db.jobs.update_one({'id': job_id}, {'$inc': {'views': 1}})
    return serialize(job)


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
        'total_jobs': total,
        'by_category': by_category,
        'by_type': by_type,
        'messages': messages_count,
    }


# -------------------- ADMIN JOBS CRUD --------------------
@api_router.post("/admin/jobs")
async def create_job(job: JobCreate, admin=Depends(require_full_admin)):
    job_obj = Job(**job.dict())
    job_obj.slug = create_slug(job.title)
    doc = job_obj.dict()
    await db.jobs.insert_one(doc)
    return serialize(doc)


@api_router.put("/admin/jobs/{job_id}")
async def update_job_endpoint(job_id: str, job: JobUpdate, admin=Depends(require_full_admin)):
    updates = {k: v for k, v in job.dict().items() if v is not None}
    if 'title' in updates:
        updates['slug'] = create_slug(updates['title'])
    result = await db.jobs.update_one({'id': job_id}, {'$set': updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    updated = await db.jobs.find_one({'id': job_id})
    return serialize(updated)


@api_router.delete("/admin/jobs/{job_id}")
async def delete_job_endpoint(job_id: str, admin=Depends(require_full_admin)):
    result = await db.jobs.delete_one({'id': job_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {'success': True}


# -------------------- CONTACT --------------------
@api_router.post("/contact")
async def submit_contact(msg: ContactCreate):
    doc = {
        'id': str(uuid.uuid4()),
        'name': msg.name,
        'email': msg.email,
        'subject': msg.subject,
        'message': msg.message,
        'created_at': datetime.utcnow(),
    }
    await db.contacts.insert_one(doc)
    return {'success': True, 'id': doc['id']}


@api_router.get("/admin/contacts")
async def list_contacts(admin=Depends(require_full_admin)):
    cursor = db.contacts.find().sort('created_at', -1)
    return [serialize(c) async for c in cursor]


@api_router.delete("/admin/contacts/{contact_id}")
async def delete_contact_endpoint(contact_id: str, admin=Depends(require_full_admin)):
    await db.contacts.delete_one({'id': contact_id})
    return {'success': True}


# -------------------- ADMIN ACTIVITY LOG --------------------
@api_router.get("/admin/activity")
async def get_activity(limit: int = 100, admin=Depends(require_full_admin)):
    cursor = db.login_logs.find().sort('timestamp', -1).limit(limit)
    return [serialize(log) async for log in cursor]


@api_router.get("/")
async def root():
    return {'message': 'AssamVacancies API'}


app.include_router(api_router)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request, Response
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
from datetime import datetime, timedelta, date

# Optional dateutil for flexible date parsing
try:
    from dateutil import parser as _date_parser  # type: ignore
    _HAS_DATEUTIL = True
except ImportError:  # pragma: no cover
    _HAS_DATEUTIL = False

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ.get('JWT_SECRET', 'assamvacancies-secret-key-2025-change-me')
JWT_ALGO = 'HS256'
TOKEN_TTL_MIN = 30
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MIN = 15
BOOTSTRAP_USERNAME = 'admin'
BOOTSTRAP_PASSWORD = 'admin'

# Assam districts (35 total as of 2025)
DISTRICTS = [
    "Bajali", "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar",
    "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh",
    "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat",
    "Kamrup", "Kamrup Metropolitan", "Karbi Anglong", "Karimganj",
    "Kokrajhar", "Lakhimpur", "Majuli", "Morigaon", "Nagaon", "Nalbari",
    "Sivasagar", "Sonitpur", "South Salmara-Mankachar", "Tamulpur",
    "Tinsukia", "Udalguri", "West Karbi Anglong",
]
VALID_TYPES = {"job", "admit_card", "result", "answer_key"}
VALID_CATEGORIES = {"govt", "private", "defence", "banking", "railway", "teaching", "police"}

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()
logger = logging.getLogger(__name__)


# -------------------- SECURITY HEADERS --------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response


# -------------------- MODELS --------------------
class NoticeBase(BaseModel):
    title: str
    organization: str
    type: str = "job"  # job | admit_card | result | answer_key
    category: str = "govt"
    district: str = "Kamrup Metropolitan"
    description: str
    location: str = "Assam"
    thumbnail: str = ""
    is_featured: bool = False
    # Job-specific
    vacancy_count: str = ""
    eligibility: str = ""
    age_limit: str = ""
    application_fee: str = ""
    salary: str = ""
    start_date: str = ""
    last_date: str = ""
    selection_process: str = ""
    how_to_apply: str = ""
    apply_link: str = ""
    notification_link: str = ""  # official notification link
    official_website: str = ""
    # Admit card / result / answer_key-specific
    notice_date: str = ""
    linked_job_id: Optional[str] = None
    download_link: str = ""


class Notice(NoticeBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slug: str = ""
    posted_date: datetime = Field(default_factory=datetime.utcnow)
    views: int = 0


class NoticeCreate(NoticeBase):
    pass


class NoticeUpdate(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    district: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    thumbnail: Optional[str] = None
    is_featured: Optional[bool] = None
    vacancy_count: Optional[str] = None
    eligibility: Optional[str] = None
    age_limit: Optional[str] = None
    application_fee: Optional[str] = None
    salary: Optional[str] = None
    start_date: Optional[str] = None
    last_date: Optional[str] = None
    selection_process: Optional[str] = None
    how_to_apply: Optional[str] = None
    apply_link: Optional[str] = None
    notification_link: Optional[str] = None
    official_website: Optional[str] = None
    notice_date: Optional[str] = None
    linked_job_id: Optional[str] = None
    download_link: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AdSettings(BaseModel):
    ads_enabled: bool = True
    disabled_paths: List[str] = []


class SiteVerification(BaseModel):
    google_site_verification: str = ""


DEFAULT_DISABLED_AD_PATHS = ['/privacy', '/terms', '/disclaimer', '/contact']

# GA4 Data API configuration
GA4_PROPERTY_ID = os.environ.get('GA4_PROPERTY_ID', '')
GA4_CREDENTIALS_PATH = os.environ.get('GA4_CREDENTIALS_PATH', '')

_ga4_client = None
def get_ga4_client():
    """Lazy GA4 client init so the rest of the API works even without GA4 creds."""
    global _ga4_client
    if _ga4_client is not None:
        return _ga4_client
    if not GA4_PROPERTY_ID or not GA4_CREDENTIALS_PATH or not os.path.exists(GA4_CREDENTIALS_PATH):
        return None
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient  # noqa: WPS433
        from google.oauth2 import service_account  # noqa: WPS433
        creds = service_account.Credentials.from_service_account_file(
            GA4_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/analytics.readonly'],
        )
        _ga4_client = BetaAnalyticsDataClient(credentials=creds)
        return _ga4_client
    except Exception as e:  # pragma: no cover
        logging.getLogger(__name__).warning(f"GA4 client init failed: {e}")
        return None


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


# -------------------- LIFECYCLE STATUS --------------------
_DATE_FORMATS = (
    '%d %B %Y', '%d %b %Y', '%B %d, %Y', '%b %d, %Y',
    '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y',
)


def parse_notice_date(s: Optional[str]) -> Optional[date]:
    """Parse free-form date strings entered by admins. Returns date or None."""
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    if _HAS_DATEUTIL:
        try:
            return _date_parser.parse(s, dayfirst=True, fuzzy=True).date()
        except (ValueError, TypeError, OverflowError):
            pass
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def compute_status(doc: dict) -> dict:
    """
    Single source of truth for notice lifecycle status on the backend.
    Adds `is_closed` and `days_left` fields. Mirrored by frontend
    `computeNoticeStatus` for badge rendering.
    """
    today = date.today()
    last_d = parse_notice_date(doc.get('last_date'))
    is_closed = bool(last_d and last_d < today)
    days_left = (last_d - today).days if (last_d and not is_closed) else None
    doc['is_closed'] = is_closed
    doc['days_left'] = days_left
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
    return jwt.encode(
        {'username': username, 'must_reset': must_reset, 'iat': now,
         'exp': now + timedelta(minutes=TOKEN_TTL_MIN)},
        JWT_SECRET, algorithm=JWT_ALGO,
    )


def client_ip(request: Request) -> str:
    fwd = request.headers.get('x-forwarded-for', '')
    if fwd:
        return fwd.split(',')[0].strip()
    return request.client.host if request.client else 'unknown'


async def log_login_attempt(username: str, ip: str, success: bool, user_agent: str, reason: str = ""):
    await db.login_logs.insert_one({
        'id': str(uuid.uuid4()),
        'username': username, 'ip': ip,
        'success': success, 'reason': reason,
        'user_agent': user_agent[:200],
        'timestamp': datetime.utcnow(),
    })


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please login again.")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db.admin_users.find_one({'username': payload.get('username')})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {'username': user['username'], 'must_reset': user.get('must_reset', False)}


async def require_full_admin(admin=Depends(get_current_admin)) -> dict:
    if admin['must_reset']:
        raise HTTPException(status_code=403, detail="Password reset required before performing admin actions")
    return admin


def validate_notice_type(t: str) -> str:
    if t not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {sorted(VALID_TYPES)}")
    return t


# -------------------- STARTUP / MIGRATION --------------------
@app.on_event("startup")
async def on_startup():
    await db.admin_users.create_index('username', unique=True)
    await db.notices.create_index('id', unique=True)
    await db.notices.create_index([('type', 1), ('category', 1), ('district', 1)])
    await db.login_logs.create_index([('timestamp', -1)])

    # Bootstrap admin
    existing = await db.admin_users.find_one({'username': BOOTSTRAP_USERNAME})
    if not existing:
        await db.admin_users.insert_one({
            'username': BOOTSTRAP_USERNAME,
            'password_hash': hash_password(BOOTSTRAP_PASSWORD),
            'must_reset': True,
            'failed_attempts': 0,
            'locked_until': None,
            'last_login': None,
            'created_at': datetime.utcnow(),
        })
        logger.info("Bootstrap admin user created (must reset on first login)")

    # Migrate jobs -> notices (one-time)
    notices_count = await db.notices.count_documents({})
    if notices_count == 0:
        jobs_count = await db.jobs.count_documents({})
        if jobs_count > 0:
            logger.info(f"Migrating {jobs_count} jobs -> notices...")
            cursor = db.jobs.find()
            migrated = 0
            async for d in cursor:
                d.pop('_id', None)
                # Rename job_type -> type
                t = d.pop('job_type', 'recruitment')
                # Map old types to new 4-type system
                type_map = {
                    'recruitment': 'job',
                    'admission': 'job',
                    'scholarship': 'job',
                    'admit_card': 'admit_card',
                    'result': 'result',
                    'answer_key': 'answer_key',
                }
                d['type'] = type_map.get(t, 'job')
                # Rename qualification -> eligibility
                if 'qualification' in d and 'eligibility' not in d:
                    d['eligibility'] = d.pop('qualification')
                else:
                    d.setdefault('eligibility', '')
                    d.pop('qualification', None)
                # New fields
                d.setdefault('district', 'Kamrup Metropolitan')
                d.setdefault('notice_date', '')
                d.setdefault('linked_job_id', None)
                d.setdefault('download_link', d.get('apply_link', '') if d['type'] != 'job' else '')
                await db.notices.insert_one(d)
                migrated += 1
            logger.info(f"Migrated {migrated} notices.")


# -------------------- AUTH --------------------
@api_router.post("/auth/login")
async def login(req: LoginRequest, request: Request):
    ip = client_ip(request)
    ua = request.headers.get('user-agent', '')

    user = await db.admin_users.find_one({'username': req.username})
    if not user:
        await log_login_attempt(req.username, ip, False, ua, 'user_not_found')
        raise HTTPException(status_code=401, detail="Invalid credentials")

    locked_until = user.get('locked_until')
    if locked_until and locked_until > datetime.utcnow():
        remaining = int((locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        await log_login_attempt(req.username, ip, False, ua, 'account_locked')
        raise HTTPException(status_code=423, detail=f"Account locked. Try again in {remaining} minute(s).")

    if not verify_password(req.password, user['password_hash']):
        new_attempts = user.get('failed_attempts', 0) + 1
        update = {'failed_attempts': new_attempts}
        reason = 'wrong_password'
        if new_attempts >= MAX_FAILED_ATTEMPTS:
            update['locked_until'] = datetime.utcnow() + timedelta(minutes=LOCKOUT_MIN)
            update['failed_attempts'] = 0
            reason = 'wrong_password_locked'
        await db.admin_users.update_one({'username': req.username}, {'$set': update})
        await log_login_attempt(req.username, ip, False, ua, reason)
        if reason == 'wrong_password_locked':
            raise HTTPException(status_code=423, detail=f"Too many failed attempts. Account locked for {LOCKOUT_MIN} minutes.")
        raise HTTPException(status_code=401, detail=f"Invalid credentials. {MAX_FAILED_ATTEMPTS - new_attempts} attempt(s) left.")

    await db.admin_users.update_one(
        {'username': req.username},
        {'$set': {'failed_attempts': 0, 'locked_until': None, 'last_login': datetime.utcnow()}},
    )
    await log_login_attempt(req.username, ip, True, ua, 'success')
    must_reset = user.get('must_reset', False)
    return {'token': create_jwt(req.username, must_reset), 'username': req.username,
            'must_reset': must_reset, 'ttl_min': TOKEN_TTL_MIN}


@api_router.get("/auth/verify")
async def verify(admin=Depends(get_current_admin)):
    return {'username': admin['username'], 'must_reset': admin['must_reset']}


@api_router.post("/auth/refresh")
async def refresh(admin=Depends(get_current_admin)):
    return {'token': create_jwt(admin['username'], admin['must_reset']), 'ttl_min': TOKEN_TTL_MIN}


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
    return {'success': True, 'token': create_jwt(admin['username'], False), 'ttl_min': TOKEN_TTL_MIN}


# -------------------- PUBLIC: META --------------------
@api_router.get("/districts")
async def get_districts():
    return {'districts': DISTRICTS}


@api_router.get("/stats")
async def get_stats():
    total = await db.notices.count_documents({})
    by_type = {t: await db.notices.count_documents({'type': t}) for t in VALID_TYPES}
    by_category = {c: await db.notices.count_documents({'category': c}) for c in VALID_CATEGORIES}
    messages_count = await db.contacts.count_documents({})
    return {
        'total_notices': total,
        'total_jobs': total,  # backward-compat alias for legacy frontend cache
        'by_type': by_type,
        'by_category': by_category,
        'messages': messages_count,
    }


# -------------------- PUBLIC: NOTICES --------------------
@api_router.get("/notices")
async def list_notices(
    type: Optional[str] = None,
    category: Optional[str] = None,
    district: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    include_closed: bool = False,
    limit: int = 50,
    skip: int = 0,
):
    query = {}
    if type:
        if type not in VALID_TYPES:
            raise HTTPException(status_code=400, detail="Invalid type")
        query['type'] = type
    if category:
        query['category'] = category
    if district:
        query['district'] = district
    if featured is not None:
        query['is_featured'] = featured
    if search:
        query['$or'] = [
            {'title': {'$regex': search, '$options': 'i'}},
            {'organization': {'$regex': search, '$options': 'i'}},
            {'description': {'$regex': search, '$options': 'i'}},
        ]
    # Fetch all matching, then filter closed in Python (last_date is free-form string)
    cursor = db.notices.find(query).sort('posted_date', -1)
    all_results = [compute_status(serialize(n)) async for n in cursor]
    if not include_closed:
        all_results = [n for n in all_results if not n.get('is_closed')]
    total = len(all_results)
    paged = all_results[skip: skip + limit]
    return {"notices": paged, "total": total}


@api_router.get("/notices/{notice_id}")
async def get_notice(notice_id: str):
    """Always returns the notice regardless of status (closed notices stay live for SEO/archival)."""
    notice = await db.notices.find_one({'id': notice_id})
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    await db.notices.update_one({'id': notice_id}, {'$inc': {'views': 1}})
    serialized = compute_status(serialize(notice))
    # Resolve linked job for non-job notices
    if serialized.get('linked_job_id'):
        linked = await db.notices.find_one({'id': serialized['linked_job_id']})
        if linked:
            serialized['linked_job'] = {
                'id': linked['id'],
                'title': linked.get('title', ''),
                'organization': linked.get('organization', ''),
            }
    return serialized


# -------------------- ADMIN: NOTICES CRUD --------------------
@api_router.post("/admin/notices")
async def create_notice(notice: NoticeCreate, admin=Depends(require_full_admin)):
    validate_notice_type(notice.type)
    obj = Notice(**notice.dict())
    obj.slug = create_slug(notice.title)
    doc = obj.dict()
    await db.notices.insert_one(doc)
    return compute_status(serialize(doc))


@api_router.put("/admin/notices/{notice_id}")
async def update_notice(notice_id: str, notice: NoticeUpdate, admin=Depends(require_full_admin)):
    updates = {k: v for k, v in notice.dict().items() if v is not None}
    if 'type' in updates:
        validate_notice_type(updates['type'])
    if 'title' in updates:
        updates['slug'] = create_slug(updates['title'])
    result = await db.notices.update_one({'id': notice_id}, {'$set': updates})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notice not found")
    updated = await db.notices.find_one({'id': notice_id})
    return compute_status(serialize(updated))


@api_router.delete("/admin/notices/{notice_id}")
async def delete_notice(notice_id: str, admin=Depends(require_full_admin)):
    result = await db.notices.delete_one({'id': notice_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notice not found")
    return {'success': True}


# -------------------- CONTACT --------------------
@api_router.post("/contact")
async def submit_contact(msg: ContactCreate):
    doc = {
        'id': str(uuid.uuid4()),
        'name': msg.name, 'email': msg.email,
        'subject': msg.subject, 'message': msg.message,
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


# -------------------- ADMIN: ACTIVITY LOG --------------------
@api_router.get("/admin/activity")
async def get_activity(limit: int = 100, admin=Depends(require_full_admin)):
    cursor = db.login_logs.find().sort('timestamp', -1).limit(limit)
    return [serialize(log) async for log in cursor]


@api_router.get("/")
async def root():
    return {'message': 'AssamVacancies API'}


# -------------------- ADS: SETTINGS + ads.txt --------------------
@api_router.get("/ads/settings")
async def get_ad_settings():
    """Public: lets frontend decide whether to render AdSlot placeholders."""
    doc = await db.site_settings.find_one({'_key': 'ads'})
    if not doc:
        return {'ads_enabled': True, 'disabled_paths': list(DEFAULT_DISABLED_AD_PATHS)}
    return {
        'ads_enabled': doc.get('ads_enabled', True),
        'disabled_paths': doc.get('disabled_paths', list(DEFAULT_DISABLED_AD_PATHS)),
    }


@api_router.put("/admin/ads/settings")
async def update_ad_settings(settings: AdSettings, admin=Depends(require_full_admin)):
    # Normalise paths: strip whitespace, ensure leading slash, drop empties
    paths = []
    for p in settings.disabled_paths:
        p = (p or '').strip()
        if not p:
            continue
        if not p.startswith('/'):
            p = '/' + p
        paths.append(p)
    payload = {'ads_enabled': settings.ads_enabled, 'disabled_paths': paths}
    await db.site_settings.update_one(
        {'_key': 'ads'}, {'$set': {'_key': 'ads', **payload}}, upsert=True,
    )
    return payload


@api_router.get("/ads.txt", response_class=Response)
async def ads_txt():
    """Served from /api/ads.txt; the canonical /ads.txt is also served as a static file by the frontend."""
    body = (
        "# AssamVacancies.com ads.txt\n"
        "# Replace the placeholder publisher ID below with your real Google AdSense publisher ID\n"
        "# once the AdSense account has been approved.\n"
        "# Format: <domain>, <publisher-id>, <account-type>, <certification-authority-id>\n"
        "google.com, pub-XXXXXXXXXXXXXXXX, DIRECT, f08c47fec0942fa0\n"
    )
    return Response(body, media_type='text/plain')


# -------------------- SITE VERIFICATION (Search Console) --------------------
@api_router.get("/site/verification")
async def get_site_verification():
    """Public: lets the frontend render the <meta name=\"google-site-verification\"> tag."""
    doc = await db.site_settings.find_one({'_key': 'verification'})
    return {
        'google_site_verification': (doc or {}).get('google_site_verification', ''),
    }


@api_router.put("/admin/site/verification")
async def update_site_verification(payload: SiteVerification, admin=Depends(require_full_admin)):
    token = (payload.google_site_verification or '').strip()
    await db.site_settings.update_one(
        {'_key': 'verification'},
        {'$set': {'_key': 'verification', 'google_site_verification': token}},
        upsert=True,
    )
    return {'google_site_verification': token}


# -------------------- ADMIN: GA4 ANALYTICS WIDGETS --------------------
@api_router.get("/admin/analytics/dashboard")
async def analytics_dashboard(admin=Depends(require_full_admin)):
    """
    Single combined GA4 Data API call returning data for both admin widgets:
      - top_notices: top viewed /notice/<id> pages, last 7 and last 30 days
      - traffic_sources: session breakdown by default channel group, last 30 days

    Uses batchRunReports so all three reports come back in one round trip.
    """
    client = get_ga4_client()
    if not client:
        raise HTTPException(
            status_code=503,
            detail="GA4 Data API is not configured. Set GA4_PROPERTY_ID and GA4_CREDENTIALS_PATH.",
        )

    try:
        from google.analytics.data_v1beta.types import (  # noqa: WPS433
            BatchRunReportsRequest, RunReportRequest, DateRange,
            Dimension, Metric, Filter, FilterExpression, OrderBy,
        )
    except ImportError as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"GA4 SDK not available: {e}")

    property_path = f"properties/{GA4_PROPERTY_ID}"

    # Filter for notice detail pages only (pagePath begins with /notice/)
    notice_filter = FilterExpression(
        filter=Filter(
            field_name='pagePath',
            string_filter=Filter.StringFilter(
                value='/notice/', match_type=Filter.StringFilter.MatchType.BEGINS_WITH,
            ),
        ),
    )
    page_views_metric = [Metric(name='screenPageViews')]
    page_dims = [Dimension(name='pagePath'), Dimension(name='pageTitle')]
    order_by_views_desc = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name='screenPageViews'), desc=True)]

    def build_top_notices_req(days: int) -> RunReportRequest:
        return RunReportRequest(
            property=property_path,
            date_ranges=[DateRange(start_date=f'{days}daysAgo', end_date='today')],
            dimensions=page_dims,
            metrics=page_views_metric,
            dimension_filter=notice_filter,
            order_bys=order_by_views_desc,
            limit=10,
        )

    traffic_req = RunReportRequest(
        property=property_path,
        date_ranges=[DateRange(start_date='30daysAgo', end_date='today')],
        dimensions=[Dimension(name='sessionDefaultChannelGroup')],
        metrics=[Metric(name='sessions')],
        order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
        limit=10,
    )

    batch_req = BatchRunReportsRequest(
        property=property_path,
        requests=[
            build_top_notices_req(7),
            build_top_notices_req(30),
            traffic_req,
        ],
    )

    try:
        batch_resp = client.batch_run_reports(batch_req)
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=502, detail=f"GA4 API call failed: {e}")

    def rows_to_pages(report):
        out = []
        for row in report.rows:
            page_path = row.dimension_values[0].value
            page_title = row.dimension_values[1].value if len(row.dimension_values) > 1 else ''
            views = int(row.metric_values[0].value) if row.metric_values else 0
            # Extract notice id from /notice/<id>
            notice_id = page_path.split('/notice/', 1)[-1].split('/')[0].split('?')[0]
            out.append({
                'page_path': page_path,
                'page_title': page_title,
                'notice_id': notice_id,
                'views': views,
            })
        return out

    def rows_to_channels(report):
        out = []
        for row in report.rows:
            channel = row.dimension_values[0].value or '(unset)'
            sessions = int(row.metric_values[0].value) if row.metric_values else 0
            out.append({'channel': channel, 'sessions': sessions})
        return out

    top_7d = rows_to_pages(batch_resp.reports[0])
    top_30d = rows_to_pages(batch_resp.reports[1])
    channels = rows_to_channels(batch_resp.reports[2])

    # Enrich with notice titles from our own DB (GA pageTitle is often the SEO title which is fine,
    # but DB title is the canonical short label).
    all_ids = list({n['notice_id'] for n in (top_7d + top_30d) if n['notice_id']})
    titles = {}
    if all_ids:
        async for n in db.notices.find({'id': {'$in': all_ids}}, {'id': 1, 'title': 1, 'organization': 1}):
            titles[n['id']] = {'title': n.get('title', ''), 'organization': n.get('organization', '')}
    for row in top_7d + top_30d:
        meta = titles.get(row['notice_id'])
        if meta:
            row['title'] = meta['title']
            row['organization'] = meta['organization']

    return {
        'property_id': GA4_PROPERTY_ID,
        'top_notices_7d': top_7d,
        'top_notices_30d': top_30d,
        'traffic_sources_30d': channels,
        'totals': {
            'sessions_30d': sum(c['sessions'] for c in channels),
            'views_7d': sum(r['views'] for r in top_7d),
            'views_30d': sum(r['views'] for r in top_30d),
        },
    }


# -------------------- SEO: SITEMAP + ROBOTS --------------------
def _public_origin(request: Request) -> str:
    """Resolve the public-facing origin from forwarded headers (set by ingress)."""
    proto = request.headers.get('x-forwarded-proto', 'https')
    host = (request.headers.get('x-forwarded-host')
            or request.headers.get('host')
            or 'assam-careers-2.preview.emergentagent.com')
    return f"{proto}://{host}"


@api_router.get("/sitemap.xml")
async def sitemap_xml(request: Request):
    """
    Dynamic XML sitemap. Auto-reflects current state of db.notices on every
    request, so publishing/unpublishing a notice is instantly visible to crawlers
    without any cache invalidation step.
    """
    origin = _public_origin(request)
    now_iso = datetime.utcnow().strftime('%Y-%m-%d')

    static_pages = [
        ('/', 'daily', '1.0'),
        ('/jobs', 'daily', '0.9'),
        ('/admit-card', 'daily', '0.9'),
        ('/result', 'daily', '0.9'),
        ('/answer-key', 'daily', '0.9'),
        ('/about', 'monthly', '0.5'),
        ('/contact', 'monthly', '0.5'),
        ('/privacy', 'yearly', '0.3'),
        ('/terms', 'yearly', '0.3'),
        ('/disclaimer', 'yearly', '0.3'),
    ]

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, freq, prio in static_pages:
        lines.append(
            f"  <url><loc>{origin}{path}</loc>"
            f"<lastmod>{now_iso}</lastmod>"
            f"<changefreq>{freq}</changefreq>"
            f"<priority>{prio}</priority></url>"
        )

    cursor = db.notices.find({}, {'id': 1, 'posted_date': 1, 'type': 1}).sort('posted_date', -1)
    async for n in cursor:
        pd = n.get('posted_date')
        lastmod = pd.strftime('%Y-%m-%d') if isinstance(pd, datetime) else now_iso
        lines.append(
            f"  <url><loc>{origin}/notice/{n['id']}</loc>"
            f"<lastmod>{lastmod}</lastmod>"
            f"<changefreq>weekly</changefreq>"
            f"<priority>0.7</priority></url>"
        )
    lines.append('</urlset>')

    return Response('\n'.join(lines), media_type='application/xml')


@api_router.get("/robots.txt")
async def robots_txt(request: Request):
    """Backend-served robots.txt (frontend also serves a static copy at /robots.txt)."""
    origin = _public_origin(request)
    body = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /admin\n"
        "Allow: /\n\n"
        f"Sitemap: {origin}/api/sitemap.xml\n"
    )
    return Response(body, media_type='text/plain')


app.include_router(api_router)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"], expose_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

#!/usr/bin/env python3
"""
Comprehensive testing for AssamVacancies backend after Notice refactor
Tests: districts, notices listing with filters, notice detail, stats, auth, admin CRUD, regression
"""
import requests
import time
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import bcrypt
from datetime import datetime

# Read base URL from frontend/.env
BASE_URL = None
with open('/app/frontend/.env', 'r') as f:
    for line in f:
        if line.startswith('REACT_APP_BACKEND_URL='):
            BASE_URL = line.split('=')[1].strip() + '/api'
            break

if not BASE_URL:
    raise Exception("REACT_APP_BACKEND_URL not found in /app/frontend/.env")

print(f"Testing backend at: {BASE_URL}")

# MongoDB connection for cleanup
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

# Test results tracking
tests_passed = 0
tests_failed = 0
failed_tests = []

def test(name, condition, error_msg=""):
    global tests_passed, tests_failed, failed_tests
    if condition:
        print(f"✅ {name}")
        tests_passed += 1
    else:
        print(f"❌ {name}")
        if error_msg:
            print(f"   Error: {error_msg}")
        tests_failed += 1
        failed_tests.append(name)

async def unlock_admin_in_db():
    """Unlock admin account in MongoDB"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.admin_users.update_one(
        {'username': 'admin'},
        {'$set': {'locked_until': None, 'failed_attempts': 0}}
    )
    client.close()
    print("🔓 Admin account unlocked in database")

async def reset_admin_password():
    """Reset admin password back to 'admin' with must_reset=true"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    password_hash = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    await db.admin_users.update_one(
        {'username': 'admin'},
        {'$set': {
            'password_hash': password_hash,
            'must_reset': True,
            'failed_attempts': 0,
            'locked_until': None
        }}
    )
    client.close()
    print("🔄 Admin password reset to 'admin' with must_reset=true")

async def cleanup_test_notices():
    """Remove test notices created during testing"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    # Delete notices with "Test" in title
    result = await db.notices.delete_many({'title': {'$regex': 'Test', '$options': 'i'}})
    print(f"🧹 Cleaned up {result.deleted_count} test notices")
    client.close()

def run_tests():
    global tests_passed, tests_failed
    
    print("\n" + "="*80)
    print("NOTICE REFACTOR TESTING - AssamVacancies Backend")
    print("="*80 + "\n")
    
    # ========== TEST 1: Districts endpoint ==========
    print("\n[TEST 1] Districts endpoint")
    print("-" * 60)
    
    resp = requests.get(f"{BASE_URL}/districts")
    test("1.1: GET /api/districts returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        test("1.2: Response contains 'districts' key", 'districts' in data, f"Got keys: {data.keys()}")
        if 'districts' in data:
            districts = data['districts']
            test("1.3: Districts is a list", isinstance(districts, list), f"Got type: {type(districts)}")
            test("1.4: Districts list has exactly 35 items", len(districts) == 35, f"Got {len(districts)} districts")
            test("1.5: Districts includes 'Kamrup Metropolitan'", 'Kamrup Metropolitan' in districts, f"Got: {districts}")
    
    # ========== TEST 2: Public notices listing ==========
    print("\n[TEST 2] Public notices listing (no auth)")
    print("-" * 60)
    
    # 2.1: GET /api/notices returns list
    resp = requests.get(f"{BASE_URL}/notices")
    test("2.1: GET /api/notices returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    
    all_notices = []
    total_count = 0
    if resp.status_code == 200:
        data = resp.json()
        test("2.2: Response contains 'notices' key", 'notices' in data, f"Got keys: {data.keys()}")
        test("2.3: Response contains 'total' key", 'total' in data, f"Got keys: {data.keys()}")
        if 'notices' in data:
            all_notices = data['notices']
            total_count = data.get('total', 0)
            test("2.4: Total count is 19 (migrated)", total_count == 19, f"Got {total_count} notices")
            test("2.5: Notices list is not empty", len(all_notices) > 0, f"Got {len(all_notices)} notices")
            
            # Check first notice has required fields
            if len(all_notices) > 0:
                first = all_notices[0]
                test("2.6: Notice has 'type' field", 'type' in first, f"Got keys: {first.keys()}")
                test("2.7: Notice has 'category' field", 'category' in first, f"Got keys: {first.keys()}")
                test("2.8: Notice has 'district' field", 'district' in first, f"Got keys: {first.keys()}")
    
    # 2.9: Filter by type=job
    resp = requests.get(f"{BASE_URL}/notices?type=job")
    test("2.9: GET /api/notices?type=job returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    job_notices = []
    if resp.status_code == 200:
        data = resp.json()
        job_notices = data.get('notices', [])
        test("2.10: Job notices count is ~14", len(job_notices) >= 10, f"Got {len(job_notices)} job notices")
        if len(job_notices) > 0:
            test("2.11: All returned notices have type='job'", all(n.get('type') == 'job' for n in job_notices), f"Got types: {[n.get('type') for n in job_notices[:3]]}")
    
    # 2.12: Filter by type=admit_card
    resp = requests.get(f"{BASE_URL}/notices?type=admit_card")
    test("2.12: GET /api/notices?type=admit_card returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        admit_notices = data.get('notices', [])
        test("2.13: Admit card notices count is 2", len(admit_notices) == 2, f"Got {len(admit_notices)} admit_card notices")
    
    # 2.14: Filter by type=result
    resp = requests.get(f"{BASE_URL}/notices?type=result")
    test("2.14: GET /api/notices?type=result returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        result_notices = data.get('notices', [])
        test("2.15: Result notices count is 2", len(result_notices) == 2, f"Got {len(result_notices)} result notices")
    
    # 2.16: Filter by type=answer_key
    resp = requests.get(f"{BASE_URL}/notices?type=answer_key")
    test("2.16: GET /api/notices?type=answer_key returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        answer_notices = data.get('notices', [])
        test("2.17: Answer key notices count is 1", len(answer_notices) == 1, f"Got {len(answer_notices)} answer_key notices")
    
    # 2.18: Invalid type should return 400
    resp = requests.get(f"{BASE_URL}/notices?type=invalid_value")
    test("2.18: GET /api/notices?type=invalid_value returns 400", resp.status_code == 400, f"Got {resp.status_code}")
    
    # 2.19: Filter by category=govt
    resp = requests.get(f"{BASE_URL}/notices?category=govt")
    test("2.19: GET /api/notices?category=govt returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        govt_notices = data.get('notices', [])
        test("2.20: Govt notices list is not empty", len(govt_notices) > 0, f"Got {len(govt_notices)} govt notices")
        if len(govt_notices) > 0:
            test("2.21: All returned notices have category='govt'", all(n.get('category') == 'govt' for n in govt_notices), f"Got categories: {[n.get('category') for n in govt_notices[:3]]}")
    
    # 2.22: Filter by district
    resp = requests.get(f"{BASE_URL}/notices?district=Kamrup%20Metropolitan")
    test("2.22: GET /api/notices?district=Kamrup Metropolitan returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        district_notices = data.get('notices', [])
        test("2.23: District notices list is not empty", len(district_notices) > 0, f"Got {len(district_notices)} notices")
        if len(district_notices) > 0:
            test("2.24: All returned notices have district='Kamrup Metropolitan'", all(n.get('district') == 'Kamrup Metropolitan' for n in district_notices), f"Got districts: {[n.get('district') for n in district_notices[:3]]}")
    
    # 2.25: Search filter
    resp = requests.get(f"{BASE_URL}/notices?search=police")
    test("2.25: GET /api/notices?search=police returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        search_notices = data.get('notices', [])
        test("2.26: Search returns at least 1 result", len(search_notices) >= 1, f"Got {len(search_notices)} results")
    
    # 2.27: Featured filter
    resp = requests.get(f"{BASE_URL}/notices?featured=true")
    test("2.27: GET /api/notices?featured=true returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        featured_notices = data.get('notices', [])
        if len(featured_notices) > 0:
            test("2.28: All returned notices have is_featured=true", all(n.get('is_featured') == True for n in featured_notices), f"Got is_featured: {[n.get('is_featured') for n in featured_notices[:3]]}")
    
    # 2.29: Pagination
    resp = requests.get(f"{BASE_URL}/notices?limit=5&skip=0")
    test("2.29: GET /api/notices?limit=5&skip=0 returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        paginated_notices = data.get('notices', [])
        test("2.30: Pagination returns at most 5 results", len(paginated_notices) <= 5, f"Got {len(paginated_notices)} results")
    
    # ========== TEST 3: Notice detail ==========
    print("\n[TEST 3] Notice detail")
    print("-" * 60)
    
    # Get a job-type notice
    job_notice_id = None
    if len(job_notices) > 0:
        job_notice_id = job_notices[0]['id']
    
    if job_notice_id:
        resp = requests.get(f"{BASE_URL}/notices/{job_notice_id}")
        test("3.1: GET /api/notices/{id} for job returns 200", resp.status_code == 200, f"Got {resp.status_code}")
        
        if resp.status_code == 200:
            notice = resp.json()
            test("3.2: Notice has type='job'", notice.get('type') == 'job', f"Got type: {notice.get('type')}")
            test("3.3: Notice has 'eligibility' field", 'eligibility' in notice, f"Got keys: {notice.keys()}")
            test("3.4: Notice has 'vacancy_count' field", 'vacancy_count' in notice, f"Got keys: {notice.keys()}")
            test("3.5: Notice has 'last_date' field", 'last_date' in notice, f"Got keys: {notice.keys()}")
            test("3.6: Notice has 'views' field", 'views' in notice, f"Got keys: {notice.keys()}")
            
            # Check views counter increments
            initial_views = notice.get('views', 0)
            resp2 = requests.get(f"{BASE_URL}/notices/{job_notice_id}")
            if resp2.status_code == 200:
                notice2 = resp2.json()
                new_views = notice2.get('views', 0)
                test("3.7: Views counter increments", new_views > initial_views, f"Initial: {initial_views}, New: {new_views}")
    
    # 3.8: Non-existent notice returns 404
    resp = requests.get(f"{BASE_URL}/notices/nonexistent-id-12345")
    test("3.8: GET /api/notices/nonexistent-id returns 404", resp.status_code == 404, f"Got {resp.status_code}")
    
    # ========== TEST 4: Stats ==========
    print("\n[TEST 4] Stats")
    print("-" * 60)
    
    resp = requests.get(f"{BASE_URL}/stats")
    test("4.1: GET /api/stats returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        stats = resp.json()
        test("4.2: Stats contains 'total_notices'", 'total_notices' in stats, f"Got keys: {stats.keys()}")
        test("4.3: Stats contains 'total_jobs' (legacy)", 'total_jobs' in stats, f"Got keys: {stats.keys()}")
        test("4.4: Stats contains 'by_type'", 'by_type' in stats, f"Got keys: {stats.keys()}")
        test("4.5: Stats contains 'by_category'", 'by_category' in stats, f"Got keys: {stats.keys()}")
        test("4.6: Stats contains 'messages'", 'messages' in stats, f"Got keys: {stats.keys()}")
        
        if 'by_type' in stats:
            by_type = stats['by_type']
            required_types = {'job', 'admit_card', 'result', 'answer_key'}
            test("4.7: by_type has exactly 4 keys (job, admit_card, result, answer_key)", set(by_type.keys()) == required_types, f"Got keys: {by_type.keys()}")
            test("4.8: by_type values are integers", all(isinstance(v, int) for v in by_type.values()), f"Got values: {by_type.values()}")
        
        if 'by_category' in stats:
            by_category = stats['by_category']
            required_categories = {'govt', 'private', 'defence', 'banking', 'railway', 'teaching', 'police'}
            test("4.9: by_category has exactly 7 keys", set(by_category.keys()) == required_categories, f"Got keys: {by_category.keys()}")
    
    # ========== TEST 5: Authentication setup ==========
    print("\n[TEST 5] Authentication setup")
    print("-" * 60)
    
    # Try to unlock admin first in case it's locked from previous tests
    asyncio.run(unlock_admin_in_db())
    
    # 5.1: Login with admin/admin
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    test("5.1: POST /api/auth/login with admin/admin returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    
    bootstrap_token = None
    must_reset = False
    if resp.status_code == 200:
        data = resp.json()
        bootstrap_token = data.get('token', '')
        must_reset = data.get('must_reset', False)
        test("5.2: Login response contains 'token'", 'token' in data, f"Got keys: {data.keys()}")
        test("5.3: Login response contains 'must_reset'", 'must_reset' in data, f"Got keys: {data.keys()}")
        
        # If must_reset=true, change password
        if must_reset:
            print("   → Admin requires password reset, changing password...")
            resp_change = requests.post(
                f"{BASE_URL}/auth/change-password",
                json={"old_password": "admin", "new_password": "NewStrongPwd123!"},
                headers={"Authorization": f"Bearer {bootstrap_token}"}
            )
            test("5.4: POST /api/auth/change-password returns 200", resp_change.status_code == 200, f"Got {resp_change.status_code}: {resp_change.text}")
            
            if resp_change.status_code == 200:
                change_data = resp_change.json()
                test("5.5: Password change returns new token", 'token' in change_data, f"Got keys: {change_data.keys()}")
                bootstrap_token = change_data.get('token', '')
                must_reset = False
    elif resp.status_code == 401:
        # Password was already changed, try with NewStrongPwd123!
        print("   → Admin password already changed, trying NewStrongPwd123!...")
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "NewStrongPwd123!"})
        if resp.status_code == 200:
            data = resp.json()
            bootstrap_token = data.get('token', '')
            must_reset = data.get('must_reset', False)
            test("5.6: Login with NewStrongPwd123! successful", True, "")
        else:
            # Need to reset via MongoDB
            print("   → Resetting admin password via MongoDB...")
            asyncio.run(reset_admin_password())
            resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
            if resp.status_code == 200:
                data = resp.json()
                bootstrap_token = data.get('token', '')
                must_reset = data.get('must_reset', False)
                # Change password
                resp_change = requests.post(
                    f"{BASE_URL}/auth/change-password",
                    json={"old_password": "admin", "new_password": "NewStrongPwd123!"},
                    headers={"Authorization": f"Bearer {bootstrap_token}"}
                )
                if resp_change.status_code == 200:
                    bootstrap_token = resp_change.json().get('token', '')
                    must_reset = False
    
    # ========== TEST 6: Admin Notice CRUD ==========
    print("\n[TEST 6] Admin Notice CRUD (with valid full-admin token)")
    print("-" * 60)
    
    created_notice_ids = []
    
    if bootstrap_token and not must_reset:
        # 6.1: Create a job notice
        job_data = {
            "title": "Test Job Notice",
            "organization": "Test Organization",
            "type": "job",
            "category": "govt",
            "district": "Jorhat",
            "description": "Test job description for testing purposes",
            "vacancy_count": "50",
            "eligibility": "Graduation",
            "last_date": "31 Aug 2025"
        }
        resp = requests.post(f"{BASE_URL}/admin/notices", json=job_data, headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("6.1: POST /api/admin/notices with type='job' returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
        
        created_job_id = None
        if resp.status_code == 200:
            created = resp.json()
            created_job_id = created.get('id')
            created_notice_ids.append(created_job_id)
            test("6.2: Created notice has 'id'", 'id' in created, f"Got keys: {created.keys()}")
            test("6.3: Created notice has auto-generated 'slug'", 'slug' in created and created['slug'] != '', f"Got slug: {created.get('slug')}")
            test("6.4: Created notice has 'posted_date'", 'posted_date' in created, f"Got keys: {created.keys()}")
        
        # 6.5: Update the notice
        if created_job_id:
            update_data = {
                "district": "Dibrugarh",
                "vacancy_count": "100"
            }
            resp = requests.put(f"{BASE_URL}/admin/notices/{created_job_id}", json=update_data, headers={"Authorization": f"Bearer {bootstrap_token}"})
            test("6.5: PUT /api/admin/notices/{id} returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
            
            if resp.status_code == 200:
                updated = resp.json()
                test("6.6: Updated notice has district='Dibrugarh'", updated.get('district') == 'Dibrugarh', f"Got district: {updated.get('district')}")
                test("6.7: Updated notice has vacancy_count='100'", updated.get('vacancy_count') == '100', f"Got vacancy_count: {updated.get('vacancy_count')}")
        
        # 6.8: Create admit_card notice with linked_job_id
        if created_job_id:
            admit_data = {
                "title": "Test Admit Card",
                "organization": "Test Organization",
                "type": "admit_card",
                "category": "govt",
                "district": "Jorhat",
                "description": "Test admit card",
                "notice_date": "15 Aug 2025",
                "linked_job_id": created_job_id,
                "download_link": "https://example.com/admit-card.pdf"
            }
            resp = requests.post(f"{BASE_URL}/admin/notices", json=admit_data, headers={"Authorization": f"Bearer {bootstrap_token}"})
            test("6.8: POST /api/admin/notices with type='admit_card' returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
            
            created_admit_id = None
            if resp.status_code == 200:
                created_admit = resp.json()
                created_admit_id = created_admit.get('id')
                created_notice_ids.append(created_admit_id)
                
                # 6.9: Get the admit card notice and check linked_job is resolved
                resp_detail = requests.get(f"{BASE_URL}/notices/{created_admit_id}")
                test("6.9: GET /api/notices/{admit_card_id} returns 200", resp_detail.status_code == 200, f"Got {resp_detail.status_code}")
                
                if resp_detail.status_code == 200:
                    admit_detail = resp_detail.json()
                    test("6.10: Admit card has 'linked_job' object", 'linked_job' in admit_detail, f"Got keys: {admit_detail.keys()}")
                    if 'linked_job' in admit_detail:
                        linked_job = admit_detail['linked_job']
                        test("6.11: linked_job has 'id'", 'id' in linked_job, f"Got keys: {linked_job.keys()}")
                        test("6.12: linked_job has 'title'", 'title' in linked_job, f"Got keys: {linked_job.keys()}")
                        test("6.13: linked_job has 'organization'", 'organization' in linked_job, f"Got keys: {linked_job.keys()}")
        
        # 6.14: Try to create notice with invalid type
        invalid_data = {
            "title": "Invalid Notice",
            "organization": "Test Org",
            "type": "invalid",
            "category": "govt",
            "district": "Jorhat",
            "description": "This should fail"
        }
        resp = requests.post(f"{BASE_URL}/admin/notices", json=invalid_data, headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("6.14: POST /api/admin/notices with type='invalid' returns 400", resp.status_code == 400, f"Got {resp.status_code}")
        
        # 6.15: Delete created notices
        for notice_id in created_notice_ids:
            resp = requests.delete(f"{BASE_URL}/admin/notices/{notice_id}", headers={"Authorization": f"Bearer {bootstrap_token}"})
            test(f"6.15: DELETE /api/admin/notices/{notice_id[:8]}... returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    # 6.16: Try admin endpoint without auth
    resp = requests.post(f"{BASE_URL}/admin/notices", json=job_data)
    test("6.16: POST /api/admin/notices without token returns 401/403", resp.status_code in [401, 403], f"Got {resp.status_code}")
    
    # 6.17: Try admin endpoint with invalid token
    resp = requests.post(f"{BASE_URL}/admin/notices", json=job_data, headers={"Authorization": "Bearer invalid-token-12345"})
    test("6.17: POST /api/admin/notices with invalid token returns 401", resp.status_code == 401, f"Got {resp.status_code}")
    
    # ========== TEST 7: Regression - contact, auth-refresh, activity log ==========
    print("\n[TEST 7] Regression - contact, auth-refresh, activity log")
    print("-" * 60)
    
    # 7.1: POST /api/contact
    contact_data = {
        "name": "Test User",
        "email": "test@example.com",
        "subject": "Test Subject",
        "message": "Test message for regression testing"
    }
    resp = requests.post(f"{BASE_URL}/contact", json=contact_data)
    test("7.1: POST /api/contact returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    contact_id = None
    if resp.status_code == 200:
        contact_resp = resp.json()
        test("7.2: Contact response contains 'success: true'", contact_resp.get('success') == True, f"Got {contact_resp}")
        contact_id = contact_resp.get('id')
    
    # 7.3: GET /api/admin/contacts
    if bootstrap_token and not must_reset:
        resp = requests.get(f"{BASE_URL}/admin/contacts", headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("7.3: GET /api/admin/contacts returns 200", resp.status_code == 200, f"Got {resp.status_code}")
        
        if resp.status_code == 200:
            contacts = resp.json()
            test("7.4: Contacts response is a list", isinstance(contacts, list), f"Got type: {type(contacts)}")
        
        # 7.5: POST /api/auth/refresh
        resp = requests.post(f"{BASE_URL}/auth/refresh", headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("7.5: POST /api/auth/refresh returns 200", resp.status_code == 200, f"Got {resp.status_code}")
        
        if resp.status_code == 200:
            refresh_data = resp.json()
            test("7.6: Refresh response contains 'token'", 'token' in refresh_data, f"Got keys: {refresh_data.keys()}")
            test("7.7: Refresh response contains 'ttl_min=30'", refresh_data.get('ttl_min') == 30, f"Got ttl_min: {refresh_data.get('ttl_min')}")
        
        # 7.8: GET /api/admin/activity
        resp = requests.get(f"{BASE_URL}/admin/activity", headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("7.8: GET /api/admin/activity returns 200", resp.status_code == 200, f"Got {resp.status_code}")
        
        if resp.status_code == 200:
            activity = resp.json()
            test("7.9: Activity response is a list", isinstance(activity, list), f"Got type: {type(activity)}")
            if isinstance(activity, list) and len(activity) > 0:
                first_log = activity[0]
                required_fields = ['username', 'ip', 'success', 'timestamp', 'reason', 'user_agent']
                has_all = all(field in first_log for field in required_fields)
                test("7.10: Activity log has required fields", has_all, f"Got keys: {first_log.keys()}")
        
        # 7.11: Delete test contact
        if contact_id:
            resp = requests.delete(f"{BASE_URL}/admin/contacts/{contact_id}", headers={"Authorization": f"Bearer {bootstrap_token}"})
            test("7.11: DELETE /api/admin/contacts/{id} returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    # 7.12: Check security headers
    resp = requests.get(f"{BASE_URL}/notices")
    test("7.12: GET /api/notices returns 200", resp.status_code == 200, f"Got {resp.status_code}")
    
    if resp.status_code == 200:
        headers = resp.headers
        test("7.13: Response includes 'Strict-Transport-Security' header", 'Strict-Transport-Security' in headers, f"Headers: {list(headers.keys())}")
        test("7.14: Response includes 'X-Content-Type-Options' header", 'X-Content-Type-Options' in headers, f"Headers: {list(headers.keys())}")
        test("7.15: Response includes 'X-Frame-Options' header", 'X-Frame-Options' in headers, f"Headers: {list(headers.keys())}")
        test("7.16: Response includes 'Referrer-Policy' header", 'Referrer-Policy' in headers, f"Headers: {list(headers.keys())}")
    
    # ========== TEST 8: Cleanup ==========
    print("\n[TEST 8] Cleanup")
    print("-" * 60)
    
    # Reset admin password
    asyncio.run(reset_admin_password())
    
    # Verify reset worked
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    test("8.1: Admin password reset successful (login with admin/admin works)", resp.status_code == 200, f"Got {resp.status_code}")
    if resp.status_code == 200:
        test("8.2: Reset admin has must_reset=true", resp.json().get('must_reset') == True, f"Got {resp.json()}")
    
    # Clean up test notices
    asyncio.run(cleanup_test_notices())
    
    # ========== SUMMARY ==========
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    
    if tests_failed > 0:
        print("\nFailed tests:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    
    print("\n" + "="*80)
    
    return tests_failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

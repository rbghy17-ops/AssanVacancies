#!/usr/bin/env python3
"""
Comprehensive security testing for AssamVacancies backend
Tests: bootstrap, password change, rate limiting, activity log, token refresh, security headers, regression
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
    """Unlock admin account in MongoDB after rate-limit testing"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.admin_users.update_one(
        {'username': 'admin'},
        {'$set': {'locked_until': None, 'failed_attempts': 0}}
    )
    client.close()
    print("🔓 Admin account unlocked in database")

async def reset_admin_password():
    """Reset admin password back to 'admin' with must_reset=true for user testing"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    # Hash 'admin' password
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

def run_tests():
    global tests_passed, tests_failed
    
    print("\n" + "="*80)
    print("SECURITY TESTING - AssamVacancies Backend")
    print("="*80 + "\n")
    
    # ========== TEST 1: First-login bootstrap & must_reset flow ==========
    print("\n[TEST 1] First-login bootstrap & must_reset flow")
    print("-" * 60)
    
    # 1.1: Login with admin/admin should succeed with must_reset=true
    resp = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    test("1.1: POST /api/auth/login with admin/admin returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        test("1.2: Response contains 'token'", 'token' in data, f"Response: {data}")
        test("1.3: Response contains 'must_reset: true'", data.get('must_reset') == True, f"must_reset={data.get('must_reset')}")
        bootstrap_token = data.get('token', '')
        
        # 1.4: Verify token with GET /api/auth/verify
        resp_verify = requests.get(f"{BASE_URL}/auth/verify", headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("1.4: GET /api/auth/verify with bootstrap token returns 200", resp_verify.status_code == 200, f"Got {resp_verify.status_code}")
        
        if resp_verify.status_code == 200:
            verify_data = resp_verify.json()
            test("1.5: Verify response shows username='admin'", verify_data.get('username') == 'admin', f"Got {verify_data}")
            test("1.6: Verify response shows must_reset=true", verify_data.get('must_reset') == True, f"Got {verify_data}")
        
        # 1.7: Try to POST /api/admin/jobs with must_reset token - should return 403
        sample_job = {
            "title": "Test Security Job",
            "organization": "Test Org",
            "category": "govt",
            "job_type": "recruitment",
            "description": "Test job for security testing",
            "location": "Assam"
        }
        resp_admin = requests.post(f"{BASE_URL}/admin/jobs", json=sample_job, headers={"Authorization": f"Bearer {bootstrap_token}"})
        test("1.7: POST /api/admin/jobs with must_reset token returns 403", resp_admin.status_code == 403, f"Got {resp_admin.status_code}: {resp_admin.text}")
    
    # ========== TEST 2: Password change flow ==========
    print("\n[TEST 2] Password change flow")
    print("-" * 60)
    
    # 2.1: Change password from admin to NewStrongPwd123
    if bootstrap_token:
        resp_change = requests.post(
            f"{BASE_URL}/auth/change-password",
            json={"old_password": "admin", "new_password": "NewStrongPwd123"},
            headers={"Authorization": f"Bearer {bootstrap_token}"}
        )
        test("2.1: POST /api/auth/change-password returns 200", resp_change.status_code == 200, f"Got {resp_change.status_code}: {resp_change.text}")
        
        if resp_change.status_code == 200:
            change_data = resp_change.json()
            test("2.2: Password change response contains 'success: true'", change_data.get('success') == True, f"Got {change_data}")
            test("2.3: Password change response contains new 'token'", 'token' in change_data, f"Got {change_data}")
            new_token = change_data.get('token', '')
            
            # 2.4: Verify new token shows must_reset=false
            resp_verify_new = requests.get(f"{BASE_URL}/auth/verify", headers={"Authorization": f"Bearer {new_token}"})
            test("2.4: GET /api/auth/verify with new token returns 200", resp_verify_new.status_code == 200, f"Got {resp_verify_new.status_code}")
            
            if resp_verify_new.status_code == 200:
                verify_new_data = resp_verify_new.json()
                test("2.5: New token shows must_reset=false", verify_new_data.get('must_reset') == False, f"Got {verify_new_data}")
            
            # 2.6: POST /api/admin/jobs with new token should now succeed
            resp_admin_new = requests.post(f"{BASE_URL}/admin/jobs", json=sample_job, headers={"Authorization": f"Bearer {new_token}"})
            test("2.6: POST /api/admin/jobs with new token succeeds (200 or 201)", resp_admin_new.status_code in [200, 201], f"Got {resp_admin_new.status_code}: {resp_admin_new.text}")
            
            if resp_admin_new.status_code in [200, 201]:
                created_job = resp_admin_new.json()
                created_job_id = created_job.get('id')
                # Clean up: delete the test job
                if created_job_id:
                    requests.delete(f"{BASE_URL}/admin/jobs/{created_job_id}", headers={"Authorization": f"Bearer {new_token}"})
            
            # 2.7: Old password (admin/admin) should no longer work
            resp_old_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
            test("2.7: Login with old password (admin/admin) returns 401", resp_old_login.status_code == 401, f"Got {resp_old_login.status_code}")
            
            # 2.8: Login with new password should succeed with must_reset=false
            resp_new_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "NewStrongPwd123"})
            test("2.8: Login with new password (admin/NewStrongPwd123) returns 200", resp_new_login.status_code == 200, f"Got {resp_new_login.status_code}")
            
            if resp_new_login.status_code == 200:
                new_login_data = resp_new_login.json()
                test("2.9: New login shows must_reset=false", new_login_data.get('must_reset') == False, f"Got {new_login_data}")
                valid_token = new_login_data.get('token', '')
    
    # ========== TEST 3: Rate limiting / lockout ==========
    print("\n[TEST 3] Rate limiting / lockout")
    print("-" * 60)
    
    # Attempt 5 wrong passwords
    for i in range(1, 6):
        resp_wrong = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": f"wrongpass{i}"})
        if i < 5:
            test(f"3.{i}: Wrong password attempt {i} returns 401", resp_wrong.status_code == 401, f"Got {resp_wrong.status_code}")
            if resp_wrong.status_code == 401:
                # Check for attempts-left message
                detail = resp_wrong.json().get('detail', '')
                test(f"3.{i}b: Response includes attempts-left message", 'attempt' in detail.lower(), f"Got: {detail}")
        else:
            # 5th attempt should lock the account
            test(f"3.5: 5th wrong password attempt returns 423 (locked)", resp_wrong.status_code == 423, f"Got {resp_wrong.status_code}: {resp_wrong.text}")
    
    # 3.6: Try login with correct password - should still be locked
    resp_locked = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "NewStrongPwd123"})
    test("3.6: Login with correct password while locked returns 423", resp_locked.status_code == 423, f"Got {resp_locked.status_code}")
    
    # 3.7: Verify activity log shows failed attempts
    if valid_token:
        # First unlock the account so we can access admin endpoints
        asyncio.run(unlock_admin_in_db())
        
        # Re-login to get a valid token after unlock
        resp_relogin = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "NewStrongPwd123"})
        if resp_relogin.status_code == 200:
            valid_token = resp_relogin.json().get('token', '')
        
        resp_activity = requests.get(f"{BASE_URL}/admin/activity", headers={"Authorization": f"Bearer {valid_token}"})
        test("3.7: GET /api/admin/activity returns 200", resp_activity.status_code == 200, f"Got {resp_activity.status_code}")
        
        if resp_activity.status_code == 200:
            activity_logs = resp_activity.json()
            test("3.8: Activity log is a list", isinstance(activity_logs, list), f"Got type: {type(activity_logs)}")
            if isinstance(activity_logs, list) and len(activity_logs) > 0:
                # Check that logs contain required fields
                first_log = activity_logs[0]
                required_fields = ['username', 'ip', 'success', 'timestamp', 'reason', 'user_agent']
                has_all_fields = all(field in first_log for field in required_fields)
                test("3.9: Activity log entries contain required fields", has_all_fields, f"Missing fields in: {first_log.keys()}")
    
    # ========== TEST 4: Token refresh / idle timeout ==========
    print("\n[TEST 4] Token refresh / idle timeout")
    print("-" * 60)
    
    if valid_token:
        resp_refresh = requests.post(f"{BASE_URL}/auth/refresh", headers={"Authorization": f"Bearer {valid_token}"})
        test("4.1: POST /api/auth/refresh returns 200", resp_refresh.status_code == 200, f"Got {resp_refresh.status_code}")
        
        if resp_refresh.status_code == 200:
            refresh_data = resp_refresh.json()
            test("4.2: Refresh response contains new 'token'", 'token' in refresh_data, f"Got {refresh_data}")
            test("4.3: Refresh response contains 'ttl_min=30'", refresh_data.get('ttl_min') == 30, f"Got ttl_min={refresh_data.get('ttl_min')}")
    
    # ========== TEST 5: Security headers ==========
    print("\n[TEST 5] Security headers")
    print("-" * 60)
    
    resp_headers = requests.get(f"{BASE_URL}/jobs")
    test("5.1: GET /api/jobs returns 200", resp_headers.status_code == 200, f"Got {resp_headers.status_code}")
    
    if resp_headers.status_code == 200:
        headers = resp_headers.headers
        test("5.2: Response includes 'Strict-Transport-Security' header", 'Strict-Transport-Security' in headers, f"Headers: {list(headers.keys())}")
        test("5.3: Response includes 'X-Content-Type-Options' header", 'X-Content-Type-Options' in headers, f"Headers: {list(headers.keys())}")
        test("5.4: Response includes 'X-Frame-Options' header", 'X-Frame-Options' in headers, f"Headers: {list(headers.keys())}")
        test("5.5: Response includes 'Referrer-Policy' header", 'Referrer-Policy' in headers, f"Headers: {list(headers.keys())}")
    
    # ========== TEST 6: Regression - existing functionality ==========
    print("\n[TEST 6] Regression - existing functionality")
    print("-" * 60)
    
    # 6.1: GET /api/jobs returns list
    resp_jobs = requests.get(f"{BASE_URL}/jobs")
    test("6.1: GET /api/jobs returns 200", resp_jobs.status_code == 200, f"Got {resp_jobs.status_code}")
    
    if resp_jobs.status_code == 200:
        jobs_data = resp_jobs.json()
        test("6.2: Jobs response contains 'jobs' array", 'jobs' in jobs_data, f"Got keys: {jobs_data.keys()}")
        if 'jobs' in jobs_data:
            jobs_list = jobs_data['jobs']
            test("6.3: Jobs list has 19+ jobs", len(jobs_list) >= 19, f"Got {len(jobs_list)} jobs")
            
            # 6.4: GET /api/jobs/{id} - get first job
            if len(jobs_list) > 0:
                first_job_id = jobs_list[0]['id']
                resp_job_detail = requests.get(f"{BASE_URL}/jobs/{first_job_id}")
                test("6.4: GET /api/jobs/{id} returns 200", resp_job_detail.status_code == 200, f"Got {resp_job_detail.status_code}")
                
                if resp_job_detail.status_code == 200:
                    job_detail = resp_job_detail.json()
                    test("6.5: Job detail contains 'id' field", 'id' in job_detail, f"Got keys: {job_detail.keys()}")
                    test("6.6: Job detail contains 'views' field", 'views' in job_detail, f"Got keys: {job_detail.keys()}")
    
    # 6.7: GET /api/stats
    resp_stats = requests.get(f"{BASE_URL}/stats")
    test("6.7: GET /api/stats returns 200", resp_stats.status_code == 200, f"Got {resp_stats.status_code}")
    
    if resp_stats.status_code == 200:
        stats_data = resp_stats.json()
        test("6.8: Stats contains 'total_jobs'", 'total_jobs' in stats_data, f"Got keys: {stats_data.keys()}")
        test("6.9: Stats contains 'by_category'", 'by_category' in stats_data, f"Got keys: {stats_data.keys()}")
        test("6.10: Stats contains 'by_type'", 'by_type' in stats_data, f"Got keys: {stats_data.keys()}")
    
    # 6.11: POST /api/contact (public)
    contact_data = {
        "name": "Security Test User",
        "email": "sectest@example.com",
        "subject": "Security Testing",
        "message": "This is a test message for security testing"
    }
    resp_contact = requests.post(f"{BASE_URL}/contact", json=contact_data)
    test("6.11: POST /api/contact returns 200", resp_contact.status_code == 200, f"Got {resp_contact.status_code}")
    
    contact_id = None
    if resp_contact.status_code == 200:
        contact_resp = resp_contact.json()
        test("6.12: Contact response contains 'success: true'", contact_resp.get('success') == True, f"Got {contact_resp}")
        contact_id = contact_resp.get('id')
    
    # 6.13: GET /api/admin/contacts (with auth)
    if valid_token:
        resp_contacts = requests.get(f"{BASE_URL}/admin/contacts", headers={"Authorization": f"Bearer {valid_token}"})
        test("6.13: GET /api/admin/contacts returns 200", resp_contacts.status_code == 200, f"Got {resp_contacts.status_code}")
        
        if resp_contacts.status_code == 200:
            contacts_list = resp_contacts.json()
            test("6.14: Contacts list is an array", isinstance(contacts_list, list), f"Got type: {type(contacts_list)}")
        
        # 6.15: DELETE /api/admin/contacts/{id}
        if contact_id:
            resp_del_contact = requests.delete(f"{BASE_URL}/admin/contacts/{contact_id}", headers={"Authorization": f"Bearer {valid_token}"})
            test("6.15: DELETE /api/admin/contacts/{id} returns 200", resp_del_contact.status_code == 200, f"Got {resp_del_contact.status_code}")
        
        # 6.16: PUT /api/admin/jobs/{id} - update a job
        if len(jobs_list) > 0:
            job_to_update = jobs_list[0]['id']
            update_data = {"description": "Updated description for security testing"}
            resp_update = requests.put(f"{BASE_URL}/admin/jobs/{job_to_update}", json=update_data, headers={"Authorization": f"Bearer {valid_token}"})
            test("6.16: PUT /api/admin/jobs/{id} returns 200", resp_update.status_code == 200, f"Got {resp_update.status_code}")
        
        # 6.17: DELETE /api/admin/jobs/{id} - create a test job first, then delete
        test_job = {
            "title": "Test Job for Deletion",
            "organization": "Test Org",
            "category": "govt",
            "job_type": "recruitment",
            "description": "This job will be deleted",
            "location": "Assam"
        }
        resp_create_test = requests.post(f"{BASE_URL}/admin/jobs", json=test_job, headers={"Authorization": f"Bearer {valid_token}"})
        if resp_create_test.status_code in [200, 201]:
            test_job_id = resp_create_test.json().get('id')
            resp_delete = requests.delete(f"{BASE_URL}/admin/jobs/{test_job_id}", headers={"Authorization": f"Bearer {valid_token}"})
            test("6.17: DELETE /api/admin/jobs/{id} returns 200", resp_delete.status_code == 200, f"Got {resp_delete.status_code}")
    
    # ========== CLEANUP: Reset admin password ==========
    print("\n[CLEANUP] Resetting admin password for user testing")
    print("-" * 60)
    asyncio.run(reset_admin_password())
    
    # Verify reset worked
    resp_final = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    test("CLEANUP: Admin password reset successful (login with admin/admin works)", resp_final.status_code == 200, f"Got {resp_final.status_code}")
    if resp_final.status_code == 200:
        test("CLEANUP: Reset admin has must_reset=true", resp_final.json().get('must_reset') == True, f"Got {resp_final.json()}")
    
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

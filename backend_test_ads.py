#!/usr/bin/env python3
"""
Comprehensive Ads Endpoints Testing for AssamVacancies backend
Tests: GET /api/ads/settings, PUT /api/admin/ads/settings, GET /api/ads.txt, regression
"""
import requests
import time
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import bcrypt
from datetime import datetime, timedelta

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

async def restore_ad_settings():
    """Restore ad settings to defaults"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.site_settings.update_one(
        {'_key': 'ads'},
        {'$set': {
            '_key': 'ads',
            'ads_enabled': True,
            'disabled_paths': ['/privacy', '/terms', '/disclaimer', '/contact']
        }},
        upsert=True
    )
    client.close()
    print("🔄 Ad settings restored to defaults")

def run_tests():
    global tests_passed, tests_failed
    
    print("\n" + "="*80)
    print("ADS ENDPOINTS TESTING - AssamVacancies Backend")
    print("="*80 + "\n")
    
    # ========== TEST 1: GET /api/ads/settings (public, no auth) ==========
    print("\n[TEST 1] GET /api/ads/settings (public, no auth)")
    print("-" * 60)
    
    # 1.1: GET /api/ads/settings without auth
    resp = requests.get(f"{BASE_URL}/ads/settings")
    test("1.1: GET /api/ads/settings returns 200", resp.status_code == 200, f"Got {resp.status_code}: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        test("1.2: Response contains 'ads_enabled' key", 'ads_enabled' in data, f"Got keys: {data.keys()}")
        test("1.3: Response contains 'disabled_paths' key", 'disabled_paths' in data, f"Got keys: {data.keys()}")
        
        if 'ads_enabled' in data:
            test("1.4: 'ads_enabled' is boolean", isinstance(data['ads_enabled'], bool), f"Got type: {type(data['ads_enabled'])}")
        
        if 'disabled_paths' in data:
            test("1.5: 'disabled_paths' is array", isinstance(data['disabled_paths'], list), f"Got type: {type(data['disabled_paths'])}")
            
            # Check default values (first call or when no setting saved)
            disabled_paths = data['disabled_paths']
            expected_defaults = ['/privacy', '/terms', '/disclaimer', '/contact']
            # May have defaults or custom values, just verify it's an array of strings
            all_strings = all(isinstance(p, str) for p in disabled_paths)
            test("1.6: All 'disabled_paths' are strings", all_strings, f"Got types: {[type(p) for p in disabled_paths]}")
    
    # ========== TEST 2: PUT /api/admin/ads/settings (admin auth required) ==========
    print("\n[TEST 2] PUT /api/admin/ads/settings (admin auth required)")
    print("-" * 60)
    
    # 2.1: Login as admin (try multiple passwords)
    admin_token = None
    passwords_to_try = ["admin", "TestPass1234", "AdminPass1234", "NewStrongPwd123"]
    
    for pwd in passwords_to_try:
        resp_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": pwd})
        
        if resp_login.status_code == 200:
            login_data = resp_login.json()
            admin_token = login_data.get('token')
            must_reset = login_data.get('must_reset', False)
            
            # If must_reset, change password
            if must_reset:
                resp_change = requests.post(
                    f"{BASE_URL}/auth/change-password",
                    json={"old_password": pwd, "new_password": "TestPass1234"},
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                if resp_change.status_code == 200:
                    admin_token = resp_change.json().get('token')
                    test(f"2.1: Admin login successful (password was {pwd}, changed to TestPass1234)", True)
                else:
                    test("2.1: Admin login successful", False, f"Password change failed: {resp_change.status_code}")
            else:
                test(f"2.1: Admin login successful (with password {pwd})", True)
            break
    
    if not admin_token:
        test("2.1: Admin login successful", False, f"All passwords failed: {passwords_to_try}")
    
    if admin_token:
        # 2.2: PUT /api/admin/ads/settings with valid token
        settings_1 = {
            "ads_enabled": False,
            "disabled_paths": ["/foo", "/bar"]
        }
        
        resp_put_1 = requests.put(f"{BASE_URL}/admin/ads/settings", json=settings_1, headers={"Authorization": f"Bearer {admin_token}"})
        test("2.2: PUT /api/admin/ads/settings returns 200", resp_put_1.status_code == 200, f"Got {resp_put_1.status_code}: {resp_put_1.text}")
        
        if resp_put_1.status_code == 200:
            put_data_1 = resp_put_1.json()
            test("2.3: Response has ads_enabled=false", put_data_1.get('ads_enabled') == False, f"Got {put_data_1.get('ads_enabled')}")
            test("2.4: Response has disabled_paths=['/foo', '/bar']", put_data_1.get('disabled_paths') == ['/foo', '/bar'], f"Got {put_data_1.get('disabled_paths')}")
        
        # 2.5: GET /api/ads/settings reflects new values
        resp_get_after_put = requests.get(f"{BASE_URL}/ads/settings")
        test("2.5: GET /api/ads/settings returns 200", resp_get_after_put.status_code == 200, f"Got {resp_get_after_put.status_code}")
        
        if resp_get_after_put.status_code == 200:
            get_data = resp_get_after_put.json()
            test("2.6: GET reflects ads_enabled=false", get_data.get('ads_enabled') == False, f"Got {get_data.get('ads_enabled')}")
            test("2.7: GET reflects disabled_paths=['/foo', '/bar']", get_data.get('disabled_paths') == ['/foo', '/bar'], f"Got {get_data.get('disabled_paths')}")
        
        # 2.8: PUT with path normalization
        settings_2 = {
            "ads_enabled": True,
            "disabled_paths": ["privacy", "  /custom-path  ", "", "/admin"]
        }
        
        resp_put_2 = requests.put(f"{BASE_URL}/admin/ads/settings", json=settings_2, headers={"Authorization": f"Bearer {admin_token}"})
        test("2.8: PUT with unnormalized paths returns 200", resp_put_2.status_code == 200, f"Got {resp_put_2.status_code}: {resp_put_2.text}")
        
        if resp_put_2.status_code == 200:
            put_data_2 = resp_put_2.json()
            normalized_paths = put_data_2.get('disabled_paths', [])
            
            # Expected: ["/privacy", "/custom-path", "/admin"]
            # - "privacy" -> "/privacy" (leading slash added)
            # - "  /custom-path  " -> "/custom-path" (whitespace stripped)
            # - "" -> dropped (empty)
            # - "/admin" -> "/admin" (already normalized)
            
            test("2.9: Normalized paths include '/privacy'", '/privacy' in normalized_paths, f"Got {normalized_paths}")
            test("2.10: Normalized paths include '/custom-path'", '/custom-path' in normalized_paths, f"Got {normalized_paths}")
            test("2.11: Normalized paths include '/admin'", '/admin' in normalized_paths, f"Got {normalized_paths}")
            test("2.12: Empty string dropped from paths", '' not in normalized_paths, f"Got {normalized_paths}")
            test("2.13: Whitespace stripped from paths", '  /custom-path  ' not in normalized_paths, f"Got {normalized_paths}")
            test("2.14: Exactly 3 paths after normalization", len(normalized_paths) == 3, f"Got {len(normalized_paths)} paths: {normalized_paths}")
    
    # 2.15: PUT without Authorization header returns 401 or 403
    settings_no_auth = {
        "ads_enabled": True,
        "disabled_paths": ["/test"]
    }
    resp_no_auth = requests.put(f"{BASE_URL}/admin/ads/settings", json=settings_no_auth)
    test("2.15: PUT without Authorization returns 401 or 403", resp_no_auth.status_code in [401, 403], f"Got {resp_no_auth.status_code}")
    
    # 2.16: PUT with bogus token returns 401
    resp_bogus_token = requests.put(
        f"{BASE_URL}/admin/ads/settings",
        json=settings_no_auth,
        headers={"Authorization": "Bearer bogus-token-12345"}
    )
    test("2.16: PUT with bogus token returns 401", resp_bogus_token.status_code == 401, f"Got {resp_bogus_token.status_code}")
    
    # ========== TEST 3: GET /api/ads.txt ==========
    print("\n[TEST 3] GET /api/ads.txt")
    print("-" * 60)
    
    # 3.1: GET /api/ads.txt
    resp_ads_txt = requests.get(f"{BASE_URL}/ads.txt")
    test("3.1: GET /api/ads.txt returns 200", resp_ads_txt.status_code == 200, f"Got {resp_ads_txt.status_code}: {resp_ads_txt.text}")
    
    if resp_ads_txt.status_code == 200:
        # 3.2: Content-Type starts with "text/plain"
        content_type = resp_ads_txt.headers.get('content-type', '')
        test("3.2: Content-Type starts with 'text/plain'", content_type.startswith('text/plain'), f"Got Content-Type: {content_type}")
        
        # 3.3: Body's first line starts with "# AssamVacancies.com ads.txt"
        body = resp_ads_txt.text
        lines = body.split('\n')
        first_line = lines[0] if lines else ''
        test("3.3: First line starts with '# AssamVacancies.com ads.txt'", first_line.startswith('# AssamVacancies.com ads.txt'), f"Got first line: {first_line}")
        
        # 3.4: Body contains a line starting with "google.com,"
        has_google_line = any(line.startswith('google.com,') for line in lines)
        test("3.4: Body contains line starting with 'google.com,'", has_google_line, f"Lines: {lines}")
    
    # ========== TEST 4: Regression checks ==========
    print("\n[TEST 4] Regression checks")
    print("-" * 60)
    
    # 4.1: GET /api/notices
    resp_notices = requests.get(f"{BASE_URL}/notices")
    test("4.1: GET /api/notices returns 200", resp_notices.status_code == 200, f"Got {resp_notices.status_code}")
    
    # 4.2: GET /api/sitemap.xml
    resp_sitemap = requests.get(f"{BASE_URL}/sitemap.xml")
    test("4.2: GET /api/sitemap.xml returns 200", resp_sitemap.status_code == 200, f"Got {resp_sitemap.status_code}")
    
    # 4.3: GET /api/robots.txt
    resp_robots = requests.get(f"{BASE_URL}/robots.txt")
    test("4.3: GET /api/robots.txt returns 200", resp_robots.status_code == 200, f"Got {resp_robots.status_code}")
    
    # 4.4: GET /api/districts
    resp_districts = requests.get(f"{BASE_URL}/districts")
    test("4.4: GET /api/districts returns 200", resp_districts.status_code == 200, f"Got {resp_districts.status_code}")
    
    # 4.5: GET /api/stats
    resp_stats = requests.get(f"{BASE_URL}/stats")
    test("4.5: GET /api/stats returns 200", resp_stats.status_code == 200, f"Got {resp_stats.status_code}")
    
    # 4.6: POST /api/contact
    contact_data = {
        "name": "Ads Test User",
        "email": "adstest@example.com",
        "subject": "Ads Testing",
        "message": "This is a test message for ads testing"
    }
    resp_contact = requests.post(f"{BASE_URL}/contact", json=contact_data)
    test("4.6: POST /api/contact returns 200", resp_contact.status_code == 200, f"Got {resp_contact.status_code}")
    
    contact_id = None
    if resp_contact.status_code == 200:
        contact_id = resp_contact.json().get('id')
    
    # 4.7: GET /api/admin/activity (admin auth)
    if admin_token:
        resp_activity = requests.get(f"{BASE_URL}/admin/activity", headers={"Authorization": f"Bearer {admin_token}"})
        test("4.7: GET /api/admin/activity returns 200", resp_activity.status_code == 200, f"Got {resp_activity.status_code}")
        
        # Cleanup contact message
        if contact_id:
            requests.delete(f"{BASE_URL}/admin/contacts/{contact_id}", headers={"Authorization": f"Bearer {admin_token}"})
    
    # ========== CLEANUP: Reset admin and restore ad settings ==========
    print("\n[CLEANUP] Resetting admin password and restoring ad settings")
    print("-" * 60)
    
    asyncio.run(reset_admin_password())
    asyncio.run(restore_ad_settings())
    
    # Verify admin reset worked
    resp_final = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    test("CLEANUP.1: Admin password reset successful", resp_final.status_code == 200, f"Got {resp_final.status_code}")
    if resp_final.status_code == 200:
        test("CLEANUP.2: Reset admin has must_reset=true", resp_final.json().get('must_reset') == True, f"Got {resp_final.json()}")
    
    # Verify ad settings restored
    resp_ads_final = requests.get(f"{BASE_URL}/ads/settings")
    test("CLEANUP.3: Ad settings restored", resp_ads_final.status_code == 200, f"Got {resp_ads_final.status_code}")
    if resp_ads_final.status_code == 200:
        final_ads = resp_ads_final.json()
        test("CLEANUP.4: ads_enabled=true", final_ads.get('ads_enabled') == True, f"Got {final_ads.get('ads_enabled')}")
        expected_paths = ['/privacy', '/terms', '/disclaimer', '/contact']
        test("CLEANUP.5: disabled_paths restored to defaults", final_ads.get('disabled_paths') == expected_paths, f"Got {final_ads.get('disabled_paths')}")
    
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

#!/usr/bin/env python3
"""
SEO endpoints testing for AssamVacancies backend
Tests: sitemap.xml, robots.txt, dynamic sitemap regeneration, regression
"""
import requests
import re
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
    print("SEO ENDPOINTS TESTING - AssamVacancies Backend")
    print("="*80 + "\n")
    
    # ========== TEST 1: GET /api/sitemap.xml ==========
    print("\n[TEST 1] GET /api/sitemap.xml")
    print("-" * 60)
    
    resp_sitemap = requests.get(f"{BASE_URL}/sitemap.xml")
    test("1.1: GET /api/sitemap.xml returns 200", resp_sitemap.status_code == 200, f"Got {resp_sitemap.status_code}: {resp_sitemap.text[:200]}")
    
    if resp_sitemap.status_code == 200:
        content_type = resp_sitemap.headers.get('Content-Type', '')
        test("1.2: Content-Type is application/xml or text/xml", 
             content_type.startswith('application/xml') or content_type.startswith('text/xml'),
             f"Got Content-Type: {content_type}")
        
        body = resp_sitemap.text
        test("1.3: Body starts with XML declaration", 
             body.startswith('<?xml version="1.0" encoding="UTF-8"?>'),
             f"Body starts with: {body[:100]}")
        
        test("1.4: Body contains urlset with sitemap namespace",
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in body,
             "Missing urlset with namespace")
        
        # Check for 7 static pages
        static_pages = ['/', '/jobs', '/admit-card', '/result', '/answer-key', '/about', '/contact']
        for page in static_pages:
            # Check for full URL (not relative path)
            pattern = f'<loc>https?://[^<]+{re.escape(page)}</loc>'
            test(f"1.5: Sitemap contains static page {page} with full URL",
                 re.search(pattern, body) is not None,
                 f"Pattern {pattern} not found in sitemap")
        
        # Count total <url> entries
        url_count = body.count('<url>')
        print(f"   Total <url> entries in sitemap: {url_count}")
        
        # Get current notice count from /api/notices
        resp_notices = requests.get(f"{BASE_URL}/notices")
        if resp_notices.status_code == 200:
            notices_data = resp_notices.json()
            notices_total = notices_data.get('total', 0)
            print(f"   Total notices in database: {notices_total}")
            
            expected_urls = 7 + notices_total
            test(f"1.6: Total <url> entries == 7 static + {notices_total} notices = {expected_urls}",
                 url_count == expected_urls,
                 f"Expected {expected_urls} URLs, got {url_count}")
            
            # Check that each notice has a <loc> entry
            if notices_total > 0:
                notices_list = notices_data.get('notices', [])
                if len(notices_list) > 0:
                    first_notice_id = notices_list[0]['id']
                    pattern = f'<loc>https?://[^<]+/notice/{re.escape(first_notice_id)}</loc>'
                    test(f"1.7: Sitemap contains notice entry for /notice/{first_notice_id}",
                         re.search(pattern, body) is not None,
                         f"Pattern {pattern} not found in sitemap")
        
        # Check that URLs use public host (not localhost:8001)
        test("1.8: URLs use public host (not localhost:8001)",
             'localhost:8001' not in body,
             "Found localhost:8001 in sitemap URLs")
        
        # Check for required XML elements in each URL entry
        test("1.9: Each URL entry has <lastmod>",
             body.count('<lastmod>') >= url_count,
             f"Expected at least {url_count} <lastmod> tags")
        
        test("1.10: Each URL entry has <changefreq>",
             body.count('<changefreq>') >= url_count,
             f"Expected at least {url_count} <changefreq> tags")
        
        test("1.11: Each URL entry has <priority>",
             body.count('<priority>') >= url_count,
             f"Expected at least {url_count} <priority> tags")
    
    # ========== TEST 2: GET /api/robots.txt ==========
    print("\n[TEST 2] GET /api/robots.txt")
    print("-" * 60)
    
    resp_robots = requests.get(f"{BASE_URL}/robots.txt")
    test("2.1: GET /api/robots.txt returns 200", resp_robots.status_code == 200, f"Got {resp_robots.status_code}")
    
    if resp_robots.status_code == 200:
        content_type = resp_robots.headers.get('Content-Type', '')
        test("2.2: Content-Type is text/plain",
             content_type.startswith('text/plain'),
             f"Got Content-Type: {content_type}")
        
        body = resp_robots.text
        test("2.3: Body contains 'User-agent: *'",
             'User-agent: *' in body,
             f"Body: {body}")
        
        test("2.4: Body contains 'Disallow: /admin/'",
             'Disallow: /admin/' in body,
             f"Body: {body}")
        
        test("2.5: Body contains 'Sitemap:' line with /api/sitemap.xml",
             'Sitemap:' in body and '/api/sitemap.xml' in body,
             f"Body: {body}")
    
    # ========== TEST 3: Dynamic sitemap regeneration ==========
    print("\n[TEST 3] Dynamic sitemap regeneration")
    print("-" * 60)
    
    # Login as admin to get token
    resp_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    
    admin_token = None
    if resp_login.status_code == 200:
        login_data = resp_login.json()
        admin_token = login_data.get('token', '')
        must_reset = login_data.get('must_reset', False)
        
        # If must_reset is true, change password first
        if must_reset:
            resp_change = requests.post(
                f"{BASE_URL}/auth/change-password",
                json={"old_password": "admin", "new_password": "TestSEO123!"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            if resp_change.status_code == 200:
                admin_token = resp_change.json().get('token', '')
                print("   Admin password changed for testing")
    
    if admin_token:
        # Get current sitemap and count URLs
        resp_sitemap_before = requests.get(f"{BASE_URL}/sitemap.xml")
        if resp_sitemap_before.status_code == 200:
            url_count_before = resp_sitemap_before.text.count('<url>')
            print(f"   URLs in sitemap before: {url_count_before}")
            
            # Create a new test notice
            test_notice = {
                "title": "SEO Sitemap Test Notice",
                "organization": "Test Organization",
                "type": "job",
                "category": "govt",
                "district": "Kamrup Metropolitan",
                "description": "This is a test notice for SEO sitemap testing",
                "location": "Assam"
            }
            
            resp_create = requests.post(
                f"{BASE_URL}/admin/notices",
                json=test_notice,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            
            test("3.1: POST /api/admin/notices creates test notice",
                 resp_create.status_code == 200,
                 f"Got {resp_create.status_code}: {resp_create.text}")
            
            test_notice_id = None
            if resp_create.status_code == 200:
                created_notice = resp_create.json()
                test_notice_id = created_notice.get('id')
                print(f"   Created test notice with ID: {test_notice_id}")
                
                # Immediately get sitemap again
                resp_sitemap_after = requests.get(f"{BASE_URL}/sitemap.xml")
                test("3.2: GET /api/sitemap.xml after creating notice returns 200",
                     resp_sitemap_after.status_code == 200,
                     f"Got {resp_sitemap_after.status_code}")
                
                if resp_sitemap_after.status_code == 200:
                    body_after = resp_sitemap_after.text
                    url_count_after = body_after.count('<url>')
                    print(f"   URLs in sitemap after: {url_count_after}")
                    
                    test("3.3: Sitemap URL count increased by 1",
                         url_count_after == url_count_before + 1,
                         f"Expected {url_count_before + 1}, got {url_count_after}")
                    
                    # Check that new notice appears in sitemap
                    pattern = f'<loc>https?://[^<]+/notice/{re.escape(test_notice_id)}</loc>'
                    test(f"3.4: New notice /notice/{test_notice_id} appears in sitemap",
                         re.search(pattern, body_after) is not None,
                         f"Pattern {pattern} not found in sitemap")
                
                # Delete the test notice
                resp_delete = requests.delete(
                    f"{BASE_URL}/admin/notices/{test_notice_id}",
                    headers={"Authorization": f"Bearer {admin_token}"}
                )
                
                test("3.5: DELETE /api/admin/notices/{id} deletes test notice",
                     resp_delete.status_code == 200,
                     f"Got {resp_delete.status_code}: {resp_delete.text}")
                
                # Get sitemap a third time
                resp_sitemap_final = requests.get(f"{BASE_URL}/sitemap.xml")
                test("3.6: GET /api/sitemap.xml after deleting notice returns 200",
                     resp_sitemap_final.status_code == 200,
                     f"Got {resp_sitemap_final.status_code}")
                
                if resp_sitemap_final.status_code == 200:
                    body_final = resp_sitemap_final.text
                    url_count_final = body_final.count('<url>')
                    print(f"   URLs in sitemap after deletion: {url_count_final}")
                    
                    test("3.7: Sitemap URL count back to original",
                         url_count_final == url_count_before,
                         f"Expected {url_count_before}, got {url_count_final}")
                    
                    # Check that deleted notice no longer appears
                    pattern = f'<loc>https?://[^<]+/notice/{re.escape(test_notice_id)}</loc>'
                    test(f"3.8: Deleted notice /notice/{test_notice_id} no longer in sitemap",
                         re.search(pattern, body_final) is None,
                         f"Pattern {pattern} still found in sitemap")
    else:
        print("   ⚠️  Could not get admin token, skipping dynamic sitemap tests")
    
    # ========== TEST 4: Regression - all previous endpoints still respond ==========
    print("\n[TEST 4] Regression - all previous endpoints")
    print("-" * 60)
    
    # 4.1: GET /api/ - root endpoint
    resp_root = requests.get(f"{BASE_URL}/")
    test("4.1: GET /api/ returns 200",
         resp_root.status_code == 200,
         f"Got {resp_root.status_code}")
    
    if resp_root.status_code == 200:
        root_data = resp_root.json()
        test("4.2: Root endpoint returns AssamVacancies API message",
             'AssamVacancies' in root_data.get('message', ''),
             f"Got: {root_data}")
    
    # 4.3: GET /api/notices
    resp_notices = requests.get(f"{BASE_URL}/notices")
    test("4.3: GET /api/notices returns 200",
         resp_notices.status_code == 200,
         f"Got {resp_notices.status_code}")
    
    # 4.4: GET /api/districts
    resp_districts = requests.get(f"{BASE_URL}/districts")
    test("4.4: GET /api/districts returns 200",
         resp_districts.status_code == 200,
         f"Got {resp_districts.status_code}")
    
    # 4.5: GET /api/stats
    resp_stats = requests.get(f"{BASE_URL}/stats")
    test("4.5: GET /api/stats returns 200",
         resp_stats.status_code == 200,
         f"Got {resp_stats.status_code}")
    
    # 4.6: Check security headers still present
    if resp_notices.status_code == 200:
        headers = resp_notices.headers
        test("4.6: Security header 'Strict-Transport-Security' present",
             'Strict-Transport-Security' in headers,
             f"Headers: {list(headers.keys())}")
        
        test("4.7: Security header 'X-Content-Type-Options' present",
             'X-Content-Type-Options' in headers,
             f"Headers: {list(headers.keys())}")
    
    # ========== CLEANUP: Reset admin password ==========
    print("\n[CLEANUP] Resetting admin password for user testing")
    print("-" * 60)
    asyncio.run(reset_admin_password())
    
    # Verify reset worked
    resp_final = requests.post(f"{BASE_URL}/auth/login", json={"username": "admin", "password": "admin"})
    test("CLEANUP: Admin password reset successful (login with admin/admin works)",
         resp_final.status_code == 200,
         f"Got {resp_final.status_code}")
    
    if resp_final.status_code == 200:
        test("CLEANUP: Reset admin has must_reset=true",
             resp_final.json().get('must_reset') == True,
             f"Got {resp_final.json()}")
    
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

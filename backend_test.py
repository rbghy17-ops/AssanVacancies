#!/usr/bin/env python3
"""
Backend API Test Suite for AssamVacancies
Tests all public and admin endpoints
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Read backend URL from frontend/.env
def get_backend_url():
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                base_url = line.split('=')[1].strip()
                return f"{base_url}/api"
    raise Exception("REACT_APP_BACKEND_URL not found in /app/frontend/.env")

BASE_URL = get_backend_url()
print(f"Testing backend at: {BASE_URL}\n")

# Test credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# Global token storage
auth_token = None
created_job_id = None
created_contact_id = None

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def success(self, test_name: str, details: str = ""):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
        if details:
            print(f"   {details}")
    
    def fail(self, test_name: str, error: str):
        self.failed += 1
        self.errors.append({"test": test_name, "error": error})
        print(f"❌ FAIL: {test_name}")
        print(f"   Error: {error}")
    
    def summary(self):
        print("\n" + "="*70)
        print(f"TEST SUMMARY: {self.passed} passed, {self.failed} failed")
        print("="*70)
        if self.errors:
            print("\nFailed Tests:")
            for err in self.errors:
                print(f"  - {err['test']}: {err['error']}")
        return self.failed == 0

result = TestResult()

def test_request(method: str, endpoint: str, test_name: str, 
                 expected_status: int = 200, 
                 json_data: Optional[Dict] = None,
                 headers: Optional[Dict] = None,
                 params: Optional[Dict] = None) -> Optional[Dict]:
    """Make HTTP request and validate response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "POST":
            resp = requests.post(url, json=json_data, headers=headers, timeout=10)
        elif method == "PUT":
            resp = requests.put(url, json=json_data, headers=headers, timeout=10)
        elif method == "DELETE":
            resp = requests.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if resp.status_code != expected_status:
            result.fail(test_name, f"Expected status {expected_status}, got {resp.status_code}. Response: {resp.text[:200]}")
            return None
        
        result.success(test_name, f"Status: {resp.status_code}")
        
        try:
            return resp.json()
        except:
            return {"status_code": resp.status_code}
    
    except Exception as e:
        result.fail(test_name, f"Request failed: {str(e)}")
        return None

print("="*70)
print("1. PUBLIC ENDPOINTS (No Auth Required)")
print("="*70 + "\n")

# Test 1: Root health check
print("Test 1: GET /api/ - Root health check")
data = test_request("GET", "/", "Root health check")
if data and "message" in data:
    print(f"   Response: {data['message']}\n")
else:
    print()

# Test 2: List all jobs (default)
print("Test 2: GET /api/jobs - List all jobs")
data = test_request("GET", "/jobs", "List all jobs")
if data:
    print(f"   Total jobs: {data.get('total', 0)}, Returned: {len(data.get('jobs', []))}\n")
    # Store a job ID for later tests
    if data.get('jobs'):
        test_job_id = data['jobs'][0]['id']
        print(f"   Sample job ID for testing: {test_job_id}\n")
else:
    test_job_id = None
    print()

# Test 3: Filter by category
print("Test 3: GET /api/jobs?category=govt - Filter by category")
data = test_request("GET", "/jobs", "Filter by category (govt)", params={"category": "govt"})
if data:
    print(f"   Govt jobs: {data.get('total', 0)}\n")
else:
    print()

# Test 4: Filter by job_type
print("Test 4: GET /api/jobs?job_type=admit_card - Filter by job type")
data = test_request("GET", "/jobs", "Filter by job_type (admit_card)", params={"job_type": "admit_card"})
if data:
    print(f"   Admit card jobs: {data.get('total', 0)}\n")
else:
    print()

# Test 5: Search
print("Test 5: GET /api/jobs?search=police - Search jobs")
data = test_request("GET", "/jobs", "Search jobs (police)", params={"search": "police"})
if data:
    print(f"   Search results: {data.get('total', 0)}\n")
else:
    print()

# Test 6: Filter featured
print("Test 6: GET /api/jobs?featured=true - Filter featured jobs")
data = test_request("GET", "/jobs", "Filter featured jobs", params={"featured": "true"})
if data:
    print(f"   Featured jobs: {data.get('total', 0)}\n")
else:
    print()

# Test 7: Pagination
print("Test 7: GET /api/jobs?limit=5&skip=0 - Pagination")
data = test_request("GET", "/jobs", "Pagination (limit=5, skip=0)", params={"limit": 5, "skip": 0})
if data:
    print(f"   Returned: {len(data.get('jobs', []))} jobs\n")
else:
    print()

# Test 8: Get single job and verify views increment
if test_job_id:
    print(f"Test 8: GET /api/jobs/{test_job_id} - Get single job")
    data1 = test_request("GET", f"/jobs/{test_job_id}", "Get single job (first call)")
    if data1:
        views1 = data1.get('views', 0)
        print(f"   Views after first call: {views1}")
        
        # Call again to verify views increment
        data2 = test_request("GET", f"/jobs/{test_job_id}", "Get single job (second call)")
        if data2:
            views2 = data2.get('views', 0)
            print(f"   Views after second call: {views2}")
            if views2 > views1:
                result.success("Views counter increments", f"Views increased from {views1} to {views2}")
            else:
                result.fail("Views counter increments", f"Views did not increment: {views1} -> {views2}")
        print()
else:
    result.fail("Get single job", "No job ID available from list")
    print()

# Test 9: Stats endpoint
print("Test 9: GET /api/stats - Get statistics")
data = test_request("GET", "/stats", "Get statistics")
if data:
    print(f"   Total jobs: {data.get('total_jobs', 0)}")
    print(f"   By category: {data.get('by_category', {})}")
    print(f"   By type: {data.get('by_type', {})}")
    print(f"   Messages: {data.get('messages', 0)}\n")
else:
    print()

print("="*70)
print("2. AUTHENTICATION")
print("="*70 + "\n")

# Test 10: Login with correct credentials
print("Test 10: POST /api/auth/login - Login with correct credentials")
login_data = {"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD}
data = test_request("POST", "/auth/login", "Login with correct credentials", json_data=login_data)
if data and "token" in data:
    auth_token = data["token"]
    print(f"   Token received: {auth_token[:50]}...\n")
else:
    print("   ⚠️  No token received - admin tests will fail\n")

# Test 11: Login with wrong credentials
print("Test 11: POST /api/auth/login - Login with wrong credentials")
wrong_login = {"username": "admin", "password": "wrongpassword"}
test_request("POST", "/auth/login", "Login with wrong credentials", expected_status=401, json_data=wrong_login)
print()

# Test 12: Verify token
if auth_token:
    print("Test 12: GET /api/auth/verify - Verify valid token")
    headers = {"Authorization": f"Bearer {auth_token}"}
    data = test_request("GET", "/auth/verify", "Verify valid token", headers=headers)
    if data:
        print(f"   Username: {data.get('username', 'N/A')}\n")
    else:
        print()
else:
    result.fail("Verify valid token", "No auth token available")
    print()

# Test 13: Verify without token
print("Test 13: GET /api/auth/verify - Verify without token")
test_request("GET", "/auth/verify", "Verify without token", expected_status=403)
print()

print("="*70)
print("3. ADMIN JOB CRUD (With Auth)")
print("="*70 + "\n")

if not auth_token:
    print("⚠️  Skipping admin tests - no auth token available\n")
else:
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Test 14: Create job
    print("Test 14: POST /api/admin/jobs - Create new job")
    new_job = {
        "title": "Test Assam Police Constable Recruitment 2025",
        "organization": "Assam Police Department",
        "category": "police",
        "job_type": "recruitment",
        "description": "Recruitment for Constable positions in Assam Police. This is a test job created by automated testing.",
        "qualification": "Graduate",
        "vacancy_count": "500",
        "location": "Assam",
        "last_date": "2025-03-31"
    }
    data = test_request("POST", "/admin/jobs", "Create new job", json_data=new_job, headers=headers)
    if data and "id" in data:
        created_job_id = data["id"]
        print(f"   Created job ID: {created_job_id}")
        print(f"   Generated slug: {data.get('slug', 'N/A')}\n")
    else:
        print()
    
    # Test 15: Update job
    if created_job_id:
        print(f"Test 15: PUT /api/admin/jobs/{created_job_id} - Update job")
        update_data = {
            "title": "Updated Test Assam Police Constable Recruitment 2025",
            "vacancy_count": "600"
        }
        data = test_request("PUT", f"/admin/jobs/{created_job_id}", "Update job", json_data=update_data, headers=headers)
        if data:
            print(f"   Updated title: {data.get('title', 'N/A')}")
            print(f"   Updated vacancy: {data.get('vacancy_count', 'N/A')}\n")
        else:
            print()
    else:
        result.fail("Update job", "No created job ID available")
        print()
    
    # Test 16: Create job without auth
    print("Test 16: POST /api/admin/jobs - Create job WITHOUT auth")
    test_request("POST", "/admin/jobs", "Create job without auth", expected_status=403, json_data=new_job)
    print()
    
    # Test 17: Delete job
    if created_job_id:
        print(f"Test 17: DELETE /api/admin/jobs/{created_job_id} - Delete job")
        data = test_request("DELETE", f"/admin/jobs/{created_job_id}", "Delete job", headers=headers)
        if data:
            print(f"   Success: {data.get('success', False)}\n")
        else:
            print()
    else:
        result.fail("Delete job", "No created job ID available")
        print()

print("="*70)
print("4. CONTACT FORM")
print("="*70 + "\n")

# Test 18: Submit contact form
print("Test 18: POST /api/contact - Submit contact message")
contact_data = {
    "name": "Rajesh Kumar",
    "email": "rajesh.kumar@example.com",
    "subject": "Query about Police Recruitment",
    "message": "I would like to know more details about the upcoming Assam Police recruitment. What are the eligibility criteria?"
}
data = test_request("POST", "/contact", "Submit contact message", json_data=contact_data)
if data and "id" in data:
    created_contact_id = data["id"]
    print(f"   Contact ID: {created_contact_id}\n")
else:
    print()

# Test 19: Get contacts (admin)
if auth_token:
    print("Test 19: GET /api/admin/contacts - Get all contacts (admin)")
    headers = {"Authorization": f"Bearer {auth_token}"}
    data = test_request("GET", "/admin/contacts", "Get all contacts", headers=headers)
    if data:
        print(f"   Total contacts: {len(data)}")
        if created_contact_id:
            found = any(c.get('id') == created_contact_id for c in data)
            if found:
                result.success("New contact in list", f"Contact {created_contact_id} found in list")
            else:
                result.fail("New contact in list", f"Contact {created_contact_id} not found in list")
        print()
    else:
        print()
else:
    result.fail("Get all contacts", "No auth token available")
    print()

# Test 20: Delete contact (admin)
if auth_token and created_contact_id:
    print(f"Test 20: DELETE /api/admin/contacts/{created_contact_id} - Delete contact")
    headers = {"Authorization": f"Bearer {auth_token}"}
    data = test_request("DELETE", f"/admin/contacts/{created_contact_id}", "Delete contact", headers=headers)
    if data:
        print(f"   Success: {data.get('success', False)}\n")
    else:
        print()
elif not auth_token:
    result.fail("Delete contact", "No auth token available")
    print()
elif not created_contact_id:
    result.fail("Delete contact", "No contact ID available")
    print()

# Final summary
success = result.summary()
sys.exit(0 if success else 1)

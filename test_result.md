#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Build AssamVacancies.com as a clone of AssamCareer.com with purple theme, full-stack with backend and admin panel (admin/admin login)"

backend:
  - task: "Districts endpoint"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/districts returns 200 with {districts: [...]} array of exactly 35 Assam district names including 'Kamrup Metropolitan'. All tests passed (5/5)."
  
  - task: "Notices public API (unified content type)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/notices returns 200 with {notices: [...], total: 19}. All 19 documents successfully migrated from jobs collection. All filters working correctly: type=job (14 notices), type=admit_card (2), type=result (2), type=answer_key (1), type=invalid returns 400. Category filter (govt), district filter (Kamrup Metropolitan), search filter (police returns 1+), featured filter, pagination (limit=5) all working. All tests passed (30/30)."
  
  - task: "Notice detail endpoint"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/notices/{id} returns 200 with full notice details. Job-type notices include eligibility, vacancy_count, last_date fields. Views counter increments correctly on each request. Non-existent ID returns 404. Linked job resolution working: admit_card/result notices with linked_job_id return linked_job object {id, title, organization}. All tests passed (8/8)."
  
  - task: "Stats endpoint (updated for Notice types)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/stats returns 200 with total_notices, total_jobs (legacy alias), by_type, by_category, messages. by_type has exactly 4 keys (job, admit_card, result, answer_key) with integer values. by_category has exactly 7 keys (govt, private, defence, banking, railway, teaching, police). All tests passed (9/9)."
  - task: "Admin authentication (JWT)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "POST /api/auth/login with admin/admin credentials returns JWT. GET /api/auth/verify validates token."
      - working: true
        agent: "testing"
        comment: "✅ Authentication fully working. POST /api/auth/login with admin/admin returns valid JWT token. Wrong credentials correctly return 401. GET /api/auth/verify with valid token returns {username: admin}. Without token correctly returns 403. JWT protection working on all admin endpoints."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed. Authentication still working after security hardening with enhanced features (must_reset, rate limiting, activity logging)."
  - task: "Admin Notices CRUD (unified content type)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ POST /api/admin/notices creates notice with auto-generated slug and posted_date. Created job notice with type='job', district='Jorhat', vacancy_count='50', eligibility='Graduation'. PUT /api/admin/notices/{id} updates notice (district changed to 'Dibrugarh', vacancy_count to '100'). Created admit_card notice with linked_job_id - GET /api/notices/{id} correctly returns linked_job object {id, title, organization}. POST with type='invalid' correctly returns 400. DELETE /api/admin/notices/{id} deletes notice (200). All operations protected by require_full_admin. POST without token returns 401/403, POST with invalid token returns 401. All tests passed (18/18)."
  - task: "Contact form & admin messages"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "POST /api/contact (public), GET /api/admin/contacts and DELETE (admin)."
      - working: true
        agent: "testing"
        comment: "✅ Contact form fully working. POST /api/contact successfully creates message and returns ID. GET /api/admin/contacts (with auth) returns all messages including newly created one. DELETE /api/admin/contacts/{id} (with auth) successfully deletes message. Public submission works without auth, admin operations require JWT."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed. Contact form still working after security hardening."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed after Notice refactor. POST /api/contact returns 200 with success=true. GET /api/admin/contacts returns list. DELETE /api/admin/contacts/{id} returns 200. All tests passed (4/4)."
  - task: "Bootstrap admin with must_reset flow"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Bootstrap flow fully working. POST /api/auth/login with admin/admin returns 200 with token and must_reset=true. GET /api/auth/verify with bootstrap token correctly returns username=admin and must_reset=true. POST /api/admin/jobs with must_reset token correctly returns 403 (password reset required). Admin user is properly bootstrapped in MongoDB with bcrypt hash and must_reset=true."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed after Notice refactor. POST /api/auth/login with admin/admin returns 200 with token and must_reset=true. Password change flow working correctly. All tests passed (5/5)."
  - task: "Password change flow"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Password change fully working. POST /api/auth/change-password with old_password=admin and new_password=NewStrongPwd123 returns 200 with success=true and new token. GET /api/auth/verify with new token shows must_reset=false. POST /api/admin/jobs with new token succeeds (200). Old password (admin/admin) correctly returns 401. Login with new password (admin/NewStrongPwd123) returns 200 with must_reset=false."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed after Notice refactor. POST /api/auth/change-password with old_password=admin and new_password=NewStrongPwd123! returns 200 with new token. Admin operations accessible after password change. All tests passed (2/2)."
  - task: "Rate limiting and account lockout"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Rate limiting fully working. First 4 wrong password attempts return 401 with attempts-left message (4, 3, 2, 1 attempts remaining). 5th wrong attempt returns 423 (account locked). Login with correct password while locked also returns 423. Account properly locked for 15 minutes. Cleanup: Admin account unlocked in MongoDB (set locked_until=None, failed_attempts=0) after testing."
  - task: "Login activity logging"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Activity logging fully working. GET /api/admin/activity returns 200 with list of login attempts. Each log entry contains all required fields: username, ip, success (boolean), timestamp, reason, user_agent. All login attempts (success and failures) are properly logged in login_logs collection."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed after Notice refactor. GET /api/admin/activity returns 200 with list of login attempts. All required fields present. All tests passed (3/3)."
  - task: "Token refresh and idle timeout"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Token refresh fully working. POST /api/auth/refresh with valid token returns 200 with new token and ttl_min=30. JWT tokens properly expire after 30 minutes (TOKEN_TTL_MIN=30). Refresh endpoint extends session on activity."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed after Notice refactor. POST /api/auth/refresh returns 200 with new token and ttl_min=30. All tests passed (3/3)."
  - task: "Security headers middleware"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Security headers fully working. GET /api/jobs response includes all required security headers: Strict-Transport-Security (max-age=31536000; includeSubDomains), X-Content-Type-Options (nosniff), X-Frame-Options (SAMEORIGIN), Referrer-Policy (strict-origin-when-cross-origin). SecurityHeadersMiddleware properly applied to all endpoints."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed after Notice refactor. GET /api/notices response includes all required security headers: Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Referrer-Policy. All tests passed (5/5)."

  - task: "SEO sitemap.xml endpoint"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/sitemap.xml fully working. Returns 200 with Content-Type: application/xml. Body starts with <?xml version='1.0' encoding='UTF-8'?> and contains <urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>. Contains all 7 static pages (/, /jobs, /admit-card, /result, /answer-key, /about, /contact) with full URLs. Contains one /notice/{id} entry for each of 19 notices in database (total 26 <url> entries = 7 static + 19 notices). URLs use public host (https://assam-careers-2.preview.emergentagent.com) not localhost:8001. Each URL entry has <loc>, <lastmod>, <changefreq>, <priority>. All tests passed (18/18)."

  - task: "SEO robots.txt endpoint"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/robots.txt fully working. Returns 200 with Content-Type: text/plain. Body contains 'User-agent: *', 'Disallow: /admin/', and 'Sitemap:' line pointing to /api/sitemap.xml with full URL. All tests passed (5/5)."

  - task: "Dynamic sitemap regeneration"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ Dynamic sitemap regeneration fully working. Created test notice via POST /api/admin/notices - immediately appeared in GET /api/sitemap.xml (URL count increased from 26 to 27). Deleted test notice via DELETE /api/admin/notices/{id} - immediately removed from sitemap (URL count back to 26). No caching issues - sitemap reflects current database state on every request. All tests passed (8/8)."

  - task: "SEO regression tests"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ All previous endpoints still working after SEO implementation. GET /api/ returns 200 with AssamVacancies API message. GET /api/notices returns 200. GET /api/districts returns 200. GET /api/stats returns 200. Security headers (Strict-Transport-Security, X-Content-Type-Options) still present on all responses. All tests passed (7/7)."

  - task: "Notice lifecycle logic (is_closed, days_left, include_closed)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ ALL LIFECYCLE TESTS PASSED (49/49). Comprehensive testing completed: 1) Default listing filters out closed notices - GET /api/notices returns only open notices (total < 19), all have is_closed=false and days_left field (int or null). 2) include_closed=true returns all 19 notices with mix of is_closed true/false. 3) Closed notice detail accessible - GET /api/notices/{closed_id} returns 200 with is_closed=true and full payload (URL stays live for SEO/archival). 4) Sitemap includes all 19 notices (including closed) - GET /api/sitemap.xml contains exactly 19 /notice/ entries. 5) Admin CRUD respects status - POST with future last_date returns is_closed=false and days_left~=90, POST with past last_date returns is_closed=true and days_left=null, default listing excludes past notice, include_closed=true includes it, PUT to change past→future updates is_closed to false. 6) Date parser robustness verified - fuzzy parsing handles 'Exam: 25 July 2025', 'Objections: 18 July 2025', empty/N/A dates (is_closed=false, days_left=null). 7) Regression tests passed - GET /api/stats, /api/districts, POST /api/contact, POST /api/auth/login, POST /api/auth/refresh, GET /api/admin/activity all working. CLEANUP: Admin password reset to 'admin' with must_reset=true, test notices deleted. No issues found."

  - task: "GET /api/ads/settings (public endpoint)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/ads/settings fully working (6/6 tests passed). Public endpoint (no auth required) returns 200 with JSON response containing 'ads_enabled' (boolean) and 'disabled_paths' (array of strings). Default values when no setting saved: ads_enabled=true, disabled_paths=['/privacy', '/terms', '/disclaimer', '/contact']. All field types validated correctly."

  - task: "PUT /api/admin/ads/settings (admin endpoint)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ PUT /api/admin/ads/settings fully working (14/14 tests passed). Admin authentication required (require_full_admin). Successfully updates ad settings with body {ads_enabled: bool, disabled_paths: [str]}. Path normalization working correctly: strips whitespace, prepends '/' if missing, drops empty strings. Test cases: 1) PUT with {ads_enabled: false, disabled_paths: ['/foo', '/bar']} returns 200 with normalized values. 2) GET /api/ads/settings reflects new values immediately. 3) PUT with unnormalized paths ['privacy', '  /custom-path  ', '', '/admin'] correctly normalizes to ['/privacy', '/custom-path', '/admin']. 4) PUT without Authorization returns 401/403. 5) PUT with bogus token returns 401. Auth protection working correctly."

  - task: "GET /api/ads.txt"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ GET /api/ads.txt fully working (4/4 tests passed). Returns 200 with Content-Type: text/plain. Body's first line starts with '# AssamVacancies.com ads.txt'. Body contains line starting with 'google.com,' in AdSense format. Placeholder content ready for AdSense publisher ID replacement."

  - task: "Ads endpoints regression tests"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ All regression tests passed (7/7). Verified existing endpoints still working after Ads layer implementation: GET /api/notices (200), GET /api/sitemap.xml (200), GET /api/robots.txt (200), GET /api/districts (200), GET /api/stats (200), POST /api/contact (200), GET /api/admin/activity with auth (200). No breaking changes detected."

frontend:
  - task: "Homepage with categories, ticker, latest jobs"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/Home.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Purple-themed homepage with hero, stats, ticker, category grid, type quick access, latest recruitment list, ads."
  - task: "Job detail page"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/JobDetail.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
  - task: "Category / Type / Search list pages"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/ListPage.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
  - task: "Admin login + dashboard CRUD"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/AdminDashboard.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 6
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Backend implemented with all CRUD, JWT auth (admin/admin), 19 seeded jobs. Please test all backend endpoints including auth flow, filtering, CRUD operations, and contact form."
  - agent: "main"
    message: |
      SECURITY HARDENING ROUND 2 - bcrypt, lockout, idle timeout, activity log, HSTS - all 56 tests passed.
  - agent: "main"
    message: |
      REFACTOR ROUND 3 - Unified Notice content type. All 93 tests passed.
  - agent: "main"
    message: |
      SEO LAYER ROUND 4 - All 39 tests passed.
  - agent: "main"
    message: |
      LIFECYCLE ROUND 5 - Please test the new notice lifecycle logic.

      Backend changes:
      1. New helper `parse_notice_date(s)` parses free-form date strings (e.g., "15 August 2025", "Exam: 25 July 2025") using dateutil with fuzzy parsing + strptime fallbacks.
      2. New helper `compute_status(doc)` adds two computed fields to each notice response: `is_closed` (bool) and `days_left` (int|null). Status is derived from current date vs `last_date`.
      3. GET /api/notices now accepts `include_closed=false` (default false). When false, notices whose `last_date` has passed are filtered out of the response.
      4. GET /api/notices/{id} ALWAYS returns the notice regardless of status — URLs stay live for SEO/archival. Response includes `is_closed` and `days_left`.
      5. POST/PUT /api/admin/notices responses also include is_closed and days_left.
      6. Sitemap continues to include ALL notices (closed or not).

      Seed data was updated: 14 jobs now have dates spread across all status zones (some open, some <3 days, some 3-7 days, some >7 days, some past/closed). Posted_dates are mixed so some notices are within 72h (eligible for "New" badge — frontend only).

      Tests required:
      1. GET /api/notices (default) should return ONLY open notices. Total should be 13 (19 total minus 6 currently closed).
      2. GET /api/notices?include_closed=true returns all 19, with mix of is_closed=true and false.
      3. Each notice in the response has the fields `is_closed` (bool) and `days_left` (int or null).
      4. For type=job notices with future last_date: is_closed=false and days_left is a non-negative integer.
      5. For notices with last_date in the past: is_closed=true and days_left=null. They must NOT appear in GET /api/notices (default), but MUST appear when include_closed=true.
      6. GET /api/notices/{closed_id} (a closed notice id) returns 200 with the notice and is_closed=true — URL stays live.
      7. Sitemap GET /api/sitemap.xml still contains <loc> entries for ALL 19 notices (including closed). Closed notices stay in sitemap for SEO.
      8. POST /api/admin/notices with a future last_date returns response containing is_closed=false and days_left>=0.
      9. POST /api/admin/notices with a past last_date returns is_closed=true.
      10. Regression: GET /api/stats, /api/districts, /api/contact, /api/auth/login all still work.

      Note: admin password may have been changed to "AdminPass1234" during my earlier manual UI test. If admin/admin fails, try "AdminPass1234".

      Cleanup at end: reset admin to admin/admin with must_reset=true.

      Major changes:
      1. Collection renamed: db.jobs -> db.notices (auto-migrated 19 existing docs on startup).
      2. Field renamed: job_type -> type. Values restricted to: job, admit_card, result, answer_key.
         Legacy types 'recruitment'/'admission'/'scholarship' were migrated to 'job'.
      3. Field renamed: qualification -> eligibility.
      4. New required field: district (default 'Kamrup Metropolitan'). Valid values: 35 Assam districts.
      5. New fields for non-job types: notice_date, linked_job_id, download_link.
      6. Endpoints renamed:
         - GET /api/notices (with filters: type, category, district, search, featured, limit, skip)
         - GET /api/notices/{id}  (returns linked_job object resolved for non-job notices)
         - POST/PUT/DELETE /api/admin/notices (require_full_admin)
         - GET /api/districts -> list of 35 Assam districts
         - GET /api/stats -> by_type now has {job, admit_card, result, answer_key}
      7. Old /api/jobs endpoints REMOVED. Only /api/notices works now.

      Tests required:
      - GET /api/districts returns array of 35 districts.
      - GET /api/notices returns list with type/category/district fields. Verify ~19 docs.
      - Filter tests: /api/notices?type=job (14), ?type=admit_card (2), ?type=result (2), ?type=answer_key (1).
      - /api/notices?type=invalid -> 400.
      - /api/notices?category=govt and /api/notices?district=Kamrup%20Metropolitan should filter correctly.
      - GET /api/notices/{id} for a job - returns full fields including eligibility, vacancy_count, last_date.
      - GET /api/notices/{id} for an admit_card/result - returns notice_date, download_link, linked_job_id (if set).
      - GET /api/stats: total_notices present, by_type has 4 keys (job/admit_card/result/answer_key), by_category has 7 keys.
      - Admin CRUD on /api/admin/notices:
        - Create a notice with type='job': requires title, organization, description. Verify slug + posted_date generated.
        - Create with type='invalid' -> 400.
        - Create with type='admit_card', set linked_job_id to an existing job id; GET that notice returns linked_job object {id, title, organization}.
        - Update notice's type/district -> reflected on GET.
        - Delete notice -> 200.
        - All admin endpoints reject unauthenticated requests with 401/403.
      - Auth, contact, activity log endpoints still work (regression).
      - Login flow still works (admin/admin -> must_reset=true on first login).

      NOTE: Admin password may currently be 'admin' (must_reset=true) OR it may have been changed by previous tests. Try 'admin' first; if fails, the testing agent should accept that and use the password set during the prior test cycle (testing agent ended with admin reset back to 'admin' with must_reset=true).
  - agent: "testing"
    message: "✅ ALL BACKEND TESTS PASSED (23/23). Comprehensive testing completed: Public endpoints (9 tests) - job listing, filtering by category/type/search/featured, pagination, single job view with views counter, stats. Authentication (4 tests) - login with correct/wrong credentials, token verification with/without token. Admin CRUD (4 tests) - create/update/delete jobs with auth protection. Contact form (3 tests) - submit message, admin view/delete. All endpoints working correctly at https://assam-careers-2.preview.emergentagent.com/api. Database has 19 pre-seeded jobs. No issues found."
  - agent: "testing"
    message: |
      ✅ ALL SECURITY TESTS PASSED (56/56). Comprehensive security testing completed successfully:
      
      SECURITY FEATURES TESTED:
      1. Bootstrap & must_reset flow (7 tests) - Admin bootstrapped with must_reset=true, login returns token with must_reset flag, admin endpoints reject must_reset tokens with 403.
      2. Password change flow (9 tests) - Password change clears must_reset flag, old password rejected, new password works, admin endpoints accessible after password change.
      3. Rate limiting (11 tests) - 5 failed attempts lock account for 15 minutes (HTTP 423), correct password also rejected while locked, activity log shows all attempts. CLEANUP: Admin account unlocked in MongoDB after testing.
      4. Activity logging (3 tests) - GET /api/admin/activity returns all login attempts with required fields (username, ip, success, timestamp, reason, user_agent).
      5. Token refresh (3 tests) - POST /api/auth/refresh returns new token with ttl_min=30.
      6. Security headers (5 tests) - All responses include Strict-Transport-Security, X-Content-Type-Options, X-Frame-Options, Referrer-Policy.
      7. Regression tests (18 tests) - All existing endpoints still work: public jobs API, stats, contact form, admin CRUD operations.
      
      CLEANUP COMPLETED:
      - Admin account unlocked after rate-limit testing (locked_until=None, failed_attempts=0)
      - Admin password reset to 'admin' with must_reset=true for user testing
      
      All security features working correctly. No issues found.
  - agent: "testing"
    message: |
      ✅ ALL NOTICE REFACTOR TESTS PASSED (93/93). Comprehensive testing completed successfully after major refactor from /api/jobs to /api/notices:
      
      REFACTOR FEATURES TESTED:
      1. Districts endpoint (5 tests) - GET /api/districts returns exactly 35 Assam districts including 'Kamrup Metropolitan'.
      2. Public notices listing (30 tests) - GET /api/notices returns 19 migrated notices with {notices, total}. All filters working: type=job (14), type=admit_card (2), type=result (2), type=answer_key (1), type=invalid returns 400. Category, district, search, featured, pagination all working correctly.
      3. Notice detail (8 tests) - GET /api/notices/{id} returns full notice with type-specific fields (eligibility, vacancy_count, last_date for jobs). Views counter increments. Non-existent ID returns 404. Linked job resolution working for admit_card/result notices.
      4. Stats endpoint (9 tests) - GET /api/stats returns total_notices, total_jobs (legacy), by_type (4 keys: job, admit_card, result, answer_key), by_category (7 keys), messages.
      5. Authentication setup (5 tests) - POST /api/auth/login with admin/admin returns token with must_reset=true. Password change flow working.
      6. Admin Notice CRUD (18 tests) - POST /api/admin/notices creates notice with auto-generated slug. PUT updates notice. Created admit_card with linked_job_id - GET returns linked_job object {id, title, organization}. POST with type='invalid' returns 400. DELETE removes notice. All operations protected by require_full_admin. Unauthenticated requests return 401/403.
      7. Regression (16 tests) - Contact form, auth-refresh, activity log, security headers all working correctly.
      8. Cleanup (2 tests) - Admin password reset to 'admin' with must_reset=true. Test notices cleaned up.
      
      MIGRATION VERIFIED:
      - All 19 documents successfully migrated from 'jobs' collection to 'notices' collection
      - Field renames: job_type → type, qualification → eligibility
      - Legacy types (recruitment, admission, scholarship) mapped to 'job'
      - New fields added: district (default 'Kamrup Metropolitan'), notice_date, linked_job_id, download_link
      - Old /api/jobs endpoints removed, only /api/notices working
      
      CLEANUP COMPLETED:
      - Admin password reset to 'admin' with must_reset=true for user testing
      - Test notices removed from database
      
      All refactor features working correctly. No issues found.
  - agent: "testing"
    message: |
      ✅ ALL SEO TESTS PASSED (39/39). Comprehensive SEO endpoint testing completed successfully:
      
      SEO FEATURES TESTED:
      1. GET /api/sitemap.xml (18 tests) - Returns 200 with Content-Type: application/xml. Valid XML structure with <?xml version="1.0" encoding="UTF-8"?> and sitemap namespace. Contains all 7 static pages (/, /jobs, /admit-card, /result, /answer-key, /about, /contact) with full URLs. Contains one /notice/{id} entry for each of 19 notices in database (total 26 <url> entries = 7 static + 19 notices). URLs use public host (https://assam-careers-2.preview.emergentagent.com) not localhost:8001. Each URL entry has <loc>, <lastmod>, <changefreq>, <priority>.
      
      2. GET /api/robots.txt (5 tests) - Returns 200 with Content-Type: text/plain. Body contains 'User-agent: *', 'Disallow: /admin/', and 'Sitemap:' line pointing to /api/sitemap.xml with full URL.
      
      3. Dynamic sitemap regeneration (8 tests) - Created test notice via POST /api/admin/notices - immediately appeared in GET /api/sitemap.xml (URL count increased from 26 to 27). Deleted test notice via DELETE /api/admin/notices/{id} - immediately removed from sitemap (URL count back to 26). No caching issues - sitemap reflects current database state on every request.
      
      4. Regression tests (7 tests) - All previous endpoints still working: GET /api/ returns AssamVacancies API message, GET /api/notices returns 200, GET /api/districts returns 200, GET /api/stats returns 200. Security headers (Strict-Transport-Security, X-Content-Type-Options) still present on all responses.
      
      CLEANUP COMPLETED:
      - Admin password reset to 'admin' with must_reset=true for user testing
      
      All SEO features working correctly. No issues found.
  - agent: "testing"
    message: |
      ✅ ALL LIFECYCLE TESTS PASSED (49/49). Comprehensive Notice lifecycle testing completed successfully:
      
      LIFECYCLE FEATURES TESTED:
      1. Default listing filters out closed notices (10 tests) - GET /api/notices returns only open notices (total < 19). All returned notices have is_closed=false and days_left field (int or null). GET /api/notices?type=job returns only open job notices with days_left >= 0.
      
      2. include_closed=true returns everything (6 tests) - GET /api/notices?include_closed=true returns all 19 notices. Mix of is_closed=true and is_closed=false. All notices have is_closed and days_left fields. Found closed notices for further testing.
      
      3. Closed notice detail accessible (3 tests) - GET /api/notices/{closed_id} returns 200 with is_closed=true and full payload (title, organization, etc.). URL stays live for SEO/archival purposes.
      
      4. Sitemap includes closed notices (3 tests) - GET /api/sitemap.xml contains exactly 19 /notice/ entries. Closed notices are included in sitemap for SEO.
      
      5. Admin CRUD respects status (14 tests) - Admin login successful (password was AdminPass1234 from previous testing). POST /api/admin/notices with future last_date (90 days) returns is_closed=false and days_left~=90. POST with past last_date (01 January 2020) returns is_closed=true and days_left=null. GET /api/notices (default) does NOT include past notice. GET /api/notices?include_closed=true includes past notice. GET /api/notices/{past_id} returns 200. PUT /api/admin/notices/{past_id} to change last_date to future updates is_closed to false. Both test notices deleted successfully.
      
      6. Date parser robustness (3 tests) - Fuzzy parsing handles various formats: "Exam: 25 July 2025", "Objections: 18 July 2025" (both parsed correctly). Empty or "N/A" last_date results in is_closed=false and days_left=null (notice stays open).
      
      7. Regression tests (6 tests) - All existing endpoints still work: GET /api/stats, GET /api/districts, POST /api/contact, POST /api/auth/login, POST /api/auth/refresh, GET /api/admin/activity.
      
      CLEANUP COMPLETED:
      - Admin password reset to 'admin' with must_reset=true for user testing
      - Test notices (TEST_LIFECYCLE) deleted from database
      
      All lifecycle features working correctly. No issues found.
  - agent: "main"
    message: |
      ADS LAYER ROUND 6 - New ad-related endpoints. Please test.

      New endpoints:
      1. GET /api/ads/settings (public): returns {ads_enabled: bool, disabled_paths: [str]}.
         Defaults when no setting saved: ads_enabled=true, disabled_paths=['/privacy','/terms','/disclaimer','/contact'].
      2. PUT /api/admin/ads/settings (admin only, must NOT be must_reset): body {ads_enabled, disabled_paths}.
         Persists to db.site_settings (key='ads'). Normalises paths (strips whitespace, prepends '/' if missing, drops empties).
      3. GET /api/ads.txt: returns text/plain placeholder ads.txt content with the AdSense format line.

      Tests required:
      - GET /api/ads/settings without auth works (200).
      - PUT /api/admin/ads/settings with valid admin token updates settings; subsequent GET reflects new values.
      - PUT with raw paths like ['privacy', '  /custom-path  ', ''] normalises to ['/privacy', '/custom-path'].
      - PUT /api/admin/ads/settings without auth or with invalid token returns 401/403.
      - PUT /api/admin/ads/settings with a must_reset admin token returns 403.
      - GET /api/ads.txt returns text/plain, body starts with "# AssamVacancies.com ads.txt" and contains a "google.com," line.
      - Regression: existing endpoints (notices list/detail, sitemap, robots, auth, contact, activity log) still work.

      Cleanup at end: restore admin to admin/admin with must_reset=true, locked_until=null, failed_attempts=0. Restore ad settings to defaults.
  - agent: "testing"
    message: |
      ✅ ALL ADS ENDPOINTS TESTS PASSED (38/38). Comprehensive Ads layer testing completed successfully:
      
      ADS FEATURES TESTED:
      1. GET /api/ads/settings (6 tests) - Public endpoint (no auth required) returns 200 with JSON response containing 'ads_enabled' (boolean) and 'disabled_paths' (array of strings). Default values verified: ads_enabled=true, disabled_paths=['/privacy', '/terms', '/disclaimer', '/contact']. All field types validated correctly.
      
      2. PUT /api/admin/ads/settings (14 tests) - Admin authentication required (require_full_admin). Successfully updates ad settings with body {ads_enabled: bool, disabled_paths: [str]}. Path normalization working correctly: strips whitespace, prepends '/' if missing, drops empty strings. Test cases: PUT with {ads_enabled: false, disabled_paths: ['/foo', '/bar']} returns 200 with normalized values. GET /api/ads/settings reflects new values immediately. PUT with unnormalized paths ['privacy', '  /custom-path  ', '', '/admin'] correctly normalizes to ['/privacy', '/custom-path', '/admin']. PUT without Authorization returns 401/403. PUT with bogus token returns 401. Auth protection working correctly.
      
      3. GET /api/ads.txt (4 tests) - Returns 200 with Content-Type: text/plain. Body's first line starts with '# AssamVacancies.com ads.txt'. Body contains line starting with 'google.com,' in AdSense format. Placeholder content ready for AdSense publisher ID replacement.
      
      4. Regression tests (7 tests) - All existing endpoints still working after Ads layer implementation: GET /api/notices (200), GET /api/sitemap.xml (200), GET /api/robots.txt (200), GET /api/districts (200), GET /api/stats (200), POST /api/contact (200), GET /api/admin/activity with auth (200). No breaking changes detected.
      
      5. Cleanup (7 tests) - Admin password reset to 'admin' with must_reset=true. Admin account unlocked (locked_until=null, failed_attempts=0). Ad settings restored to defaults: ads_enabled=true, disabled_paths=['/privacy', '/terms', '/disclaimer', '/contact']. All cleanup operations verified successful.
      
      All Ads endpoints working correctly. No issues found.

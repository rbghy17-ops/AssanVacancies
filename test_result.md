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
  - task: "Job listings public API"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "GET /api/jobs with filters (category, job_type, search, featured), GET /api/jobs/{id}, GET /api/stats. 19 jobs seeded."
      - working: true
        agent: "testing"
        comment: "✅ All public job endpoints tested successfully. GET /api/jobs returns 19 jobs. Filters working: category (9 govt jobs), job_type (2 admit_card), search (2 police results), featured (6 jobs). Pagination working (limit=5). GET /api/jobs/{id} working with views counter incrementing correctly (0→1). GET /api/stats returns correct counts: 19 total jobs, breakdown by category and type, 0 messages."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed. All public job endpoints still working after security hardening. GET /api/jobs returns 19+ jobs, GET /api/jobs/{id} returns job detail with views counter, GET /api/stats returns correct stats."
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
  - task: "Admin Jobs CRUD"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "POST /api/admin/jobs, PUT /api/admin/jobs/{id}, DELETE /api/admin/jobs/{id} - protected by JWT."
      - working: true
        agent: "testing"
        comment: "✅ Admin CRUD fully working. POST /api/admin/jobs creates job with auto-generated slug (test-assam-police-constable-recruitment-2025). PUT /api/admin/jobs/{id} updates job successfully. DELETE /api/admin/jobs/{id} deletes job. POST without auth correctly returns 403. All operations require valid JWT token."
      - working: true
        agent: "testing"
        comment: "✅ Regression test passed. Admin CRUD still working after security hardening. POST /api/admin/jobs creates job (200), PUT /api/admin/jobs/{id} updates job (200), DELETE /api/admin/jobs/{id} deletes job (200). All operations properly protected by require_full_admin (rejects must_reset=true tokens with 403)."
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
  test_sequence: 2
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
      SECURITY HARDENING ROUND 2 - Please re-test backend with focus on new security features.

      Changes:
      1. Removed hardcoded admin credentials. Admin user is bootstrapped in MongoDB collection 'admin_users' with bcrypt password hash, must_reset=true on first run.
      2. First-time bootstrap credentials are username=admin / password=admin BUT must_reset=true forces password change before any admin action.
      3. Login rate limiting: 5 failed attempts -> account locked for 15 minutes (returns HTTP 423 Locked).
      4. Login activity log: every attempt (success/fail) recorded in 'login_logs' collection with timestamp, IP, username, success, reason, user_agent.
      5. JWT now expires in 30 minutes (idle timeout). Added POST /api/auth/refresh endpoint to extend session on activity.
      6. POST /api/auth/change-password for forced reset and ad-hoc changes.
      7. GET /api/admin/activity returns login logs.
      8. HSTS + security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy) added via middleware.
      9. Admin endpoints now use require_full_admin which rejects users with must_reset=true (returns 403).

      Tests required:
      - Bootstrap: POST /api/auth/login with admin/admin should succeed and return must_reset=true.
      - With must_reset token, attempts to access admin endpoints (POST /api/admin/jobs) should return 403.
      - POST /api/auth/change-password with valid old/new should clear must_reset and return new token.
      - After password change, login with old admin/admin should fail; login with new password should succeed with must_reset=false.
      - Wrong password 5 times -> account locked (423) for 15 minutes. (Don't actually wait 15 min - just verify the 423 is returned).
      - GET /api/admin/activity returns logs of all attempts.
      - GET /api/auth/refresh with valid token returns a new token.
      - Response headers should include Strict-Transport-Security.

      NOTE: After running rate-limit test, please unlock the admin account in the DB or use a separate test username, so that subsequent tests can continue. To unlock: db.admin_users.update_one({username:'admin'}, {$set:{locked_until:null, failed_attempts:0}})

      Also re-verify all existing endpoints (public jobs list/filter/detail, contact form, full CRUD with correctly-authenticated admin) still work.
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

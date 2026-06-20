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
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus: []
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Backend implemented with all CRUD, JWT auth (admin/admin), 19 seeded jobs. Please test all backend endpoints including auth flow, filtering, CRUD operations, and contact form."
  - agent: "testing"
    message: "✅ ALL BACKEND TESTS PASSED (23/23). Comprehensive testing completed: Public endpoints (9 tests) - job listing, filtering by category/type/search/featured, pagination, single job view with views counter, stats. Authentication (4 tests) - login with correct/wrong credentials, token verification with/without token. Admin CRUD (4 tests) - create/update/delete jobs with auth protection. Contact form (3 tests) - submit message, admin view/delete. All endpoints working correctly at https://assam-careers-2.preview.emergentagent.com/api. Database has 19 pre-seeded jobs. No issues found."

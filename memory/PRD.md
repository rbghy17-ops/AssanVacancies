# AssamVacancies.com — PRD

## Original Problem Statement
Build a pixel-perfect, fully functional clone of AssamCareer.com (named AssamVacancies.com) — purple theme, mock-realistic Indian gov-job data, admin panel (originally `admin/admin`), ad placeholders, and full-stack data management.

## Stack
- Frontend: React + React Router, Tailwind, Shadcn UI, Context API
- Backend: FastAPI + Motor (async MongoDB), PyJWT, bcrypt, APScheduler, BeautifulSoup4, rapidfuzz
- Integrations: GA4 Data API (service-account), Search Console (meta-tag), AdSense placeholder

## Completed
- Public site: Home, type-listings (Jobs / Admit Cards / Results / Answer Keys), detail page, static pages (About/Privacy/Terms/Disclaimer), cookie-consent gate, AdSlot system, SeoMeta + JSON-LD + sitemap + robots.txt.
- Notice schema unified into `notices` collection with `type` polymorphism + lifecycle (`is_closed`, `days_left`) + closed-archival.
- Admin panel: secure JWT auth (bcrypt, lockout, idle timeout, forced reset), CRUD on notices, ads-enable toggle + per-path disable, Search Console meta-tag manager, GA4 widgets (top notices + traffic sources), login activity log.
- **Auto-Aggregation Step A — Backend pipeline (Feb 2026)**: source registry, fetcher with timeout + UA + SSL bypass, structured-facts-only extractor (no paragraph copying), template-built original summary, URL hash dedup + fuzzy (rapidfuzz token_set_ratio ≥88) dedup against existing notices, drafts saved as `status='draft'` (never auto-publish), full run log per source, APScheduler with configurable interval-hours + enable toggle. Default seed: APSC + SLPRB only. Fixture test passes.
- **Auto-Aggregation P1 — Review UI (Feb 2026)**: new admin "Aggregator" tab with 4 sub-tabs — Review Queue (approve / reject / edit / bulk approve / bulk reject + filter by source), Sources (CRUD + per-source Run + Run-All + enabled toggle), Run Log, Scheduler. Backend endpoints: approve / reject / bulk for drafts, source-id filter on drafts list. Full backend pytest (15/15) and UI integration (15/15) green via testing agent.

## Endpoints (selected)
- `GET /api/notices` & `/api/notices/{id}` — public; both exclude `status='draft'`.
- `GET/POST/PUT/DELETE /api/admin/aggregator/sources`
- `POST /api/admin/aggregator/sources/{id}/run` and `POST /api/admin/aggregator/run-all`
- `GET /api/admin/aggregator/runs`, `GET /api/admin/aggregator/drafts`
- `GET/PUT /api/admin/aggregator/settings` (enabled, interval_hours 1–168)

## Roadmap
- **P2 — Aggregator Step C (Graduated trust)**: per-source approval/rejection-rate trust score, optional auto-publish above threshold with admin override.
- **Backlog**: real AdSense publisher ID (currently `pub-XXXXXXXXXXXXXXXX`), GA4 dashboard ingestion once site has traffic, more reachable official sources beyond APSC/SLPRB.

## Known notes
- APSC/SLPRB list pages timed-out / returned 500 from the pod cluster during testing. Aggregator captures these errors per-source in `aggregator_runs` and continues; admin can see them in `last_run_summary` / `/api/admin/aggregator/runs`.
- The `description` field on aggregator drafts is always built from a template using only the extracted structured facts — never copies source paragraphs. This is a hard rule (AdSense originality).

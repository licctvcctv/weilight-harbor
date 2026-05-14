# Weilight Harbor — System Document (Draft)

**Course:** COMP3030J Web Development, University College Dublin, 2025/2026
**Group:** 14
**Live deployment:** http://csi6220-2-vm3.ucd.ie
**Repository:** https://github.com/licctvcctv/weilight-harbor
**Document version:** Week 11 draft

> Target page budget (Overleaf, 11pt, 2.5cm margins, ≤20 pages):
> Abstract ≤1, Introduction 1–2, Technical Implementation 10–12, Generative AI Use 1–2, Team Contribution 3–4, Conclusion ≤1.

---

## Abstract  *(≤1 page)*

Weilight Harbor is a charity and mutual-aid web platform built for the caregivers and families of seriously ill patients. Unlike transactional fundraising portals, the platform places **emotional companionship** ahead of financial aid: a moderated community, a time-gated anonymous "Night Confessions" feature, a private journaling space, an interactive respite-help map, and a verified crowdfunding module are integrated under a single role-based access model. The system is implemented as a Flask 3 web application backed by SQLite and SQLAlchemy, served via Gunicorn behind Nginx on a UCD-hosted Ubuntu VM. It supports full Chinese/English internationalisation (511 translated strings), RBAC across three user roles, and an admin moderation back-office derived from the Pear-Admin-Flask base. This document records the design rationale, technical architecture, key implementation details, the use of generative AI tooling during development, and the per-member contribution split.

---

## 1. Introduction  *(1–2 pages)*

### 1.1 Background and Motivation
Caregivers of patients with serious illnesses face emotional exhaustion, social isolation and financial strain that mainstream platforms rarely address as a single concern. Generic forums lack verification, fundraising sites are transactional, and chat groups are ephemeral. Weilight Harbor (微光港湾, "harbor of faint lights") was designed to act as a *quiet, warm space* where these users can be both heard and helped.

### 1.2 Goals
- Provide a verified community where certified caregivers and the public can interact safely.
- Enable trustworthy, simulated crowdfunding to demonstrate end-to-end donation flow without handling real money.
- Offer private journaling with mood tracking and an "Annual Film" reflection feature.
- Surface practical mutual aid (respite/equipment) on an interactive map.
- Support both Mandarin and English audiences with a single codebase.

### 1.3 Scope
The submitted artefact contains 5 user-facing modules (Community, Crowdfunding, Life Journal, Respite Station, User Centre), an Admin module, an Auth module and a static-pages module. Donations are simulated; SMTP/SMS gateways are stubbed. The platform is not a substitute for medical, legal or financial advice.

### 1.4 Stakeholders and Roles
- **Regular User** — read, donate, post, comment.
- **Certified Family / Volunteer** — additionally create campaigns, accept respite requests, access journal.
- **Administrator** — additionally review certifications and campaigns, moderate community content.

### 1.5 Document Structure
Section 2 describes the technical implementation; Section 3 evaluates how generative AI tooling was used during development; Section 4 records team contribution; Section 5 concludes.

---

## 2. Technical Implementation  *(10–12 pages)*

### 2.1 Technology Stack
| Layer | Technology | Rationale |
|---|---|---|
| Backend | Python 3.10, Flask 3.x | Familiar from coursework, mature ecosystem |
| ORM | SQLAlchemy + Flask-Migrate | Schema evolution and portability |
| Auth | Flask-Login | Session cookie auth, well-documented |
| i18n | Flask-Babel | Required for Mandarin/English toggle |
| Frontend | Bootstrap 5.3, Jinja2, Lucide Icons, Leaflet.js | Server-rendered pages, lightweight client JS |
| Database | SQLite | Single-file, no external service required on the assigned VM |
| Process | Gunicorn (sync workers) | Standard WSGI runner |
| Reverse proxy | Nginx | TLS termination point and static file server |
| Service mgmt | systemd | Auto-restart, journald integration |
| CI/CD | GitHub Actions + expect over jump host | Push-to-deploy with TOTP-secured SSH |
| Admin base | Pear-Admin-Flask (Layui) | Reused RBAC, dict, log scaffolding to focus effort on domain features |

### 2.2 System Architecture
```
                ┌──────────────────┐
                │      Browser     │
                └────────┬─────────┘
                         │ HTTPS / HTTP
                ┌────────▼─────────┐
                │ Nginx (port 80)  │── /static/ served directly
                └────────┬─────────┘
                         │ Unix socket
                ┌────────▼─────────┐
                │ Gunicorn (WSGI)  │── systemd-managed
                └────────┬─────────┘
                         │
                ┌────────▼─────────┐
                │  Flask app       │
                │  + Blueprints    │
                │  + SQLAlchemy    │
                └────────┬─────────┘
                         │
                ┌────────▼─────────┐
                │  SQLite (12 tbl) │
                └──────────────────┘
```
The repository follows the application-factory pattern (`applications/__init__.py::create_app`) so the same code path is used in development, in tests and under Gunicorn.

### 2.3 Source Tree (key folders)
```
weilight-harbor/
├── app.py                        # WSGI entry point
├── applications/
│   ├── __init__.py               # create_app factory
│   ├── configs/                  # SQLite, Babel, upload paths
│   ├── extensions/               # init_sqlalchemy, init_login, init_babel, ...
│   ├── models/                   # SQLAlchemy models (12 tables)
│   ├── view/                     # Route blueprints
│   │   ├── auth/  community/  crowdfunding/
│   │   ├── journal/ respite/  user_center/
│   │   ├── index/   admin/
│   └── common/utils/             # files, http, sensitive, rights, ...
├── templates/
│   ├── public/                   # 27 Bootstrap 5 templates
│   └── admin/                    # Layui admin panel
├── static/  public/  admin/
└── translations/zh/LC_MESSAGES/  # 511 translated strings
```

### 2.4 Data Model
12 tables; selected key columns shown.
| Table | Purpose | Notable columns |
|---|---|---|
| `admin_user` | Users | username, email, phone, user_type, is_certified, locale, avatar, bio |
| `admin_role` | RBAC roles | name, code (regular / certified_family / certified_volunteer / admin) |
| `admin_user_role`, `admin_role_power`, `admin_power` | RBAC mapping (inherited from Pear-Admin-Flask) | |
| `wl_post` | Community posts | category, content, images (JSON), like_count, view_count, comment_count, is_anonymous, delete_at |
| `wl_comment` | Comments | post_id, user_id, content, parent_id (threading) |
| `wl_post_like` | Like uniqueness | (post_id, user_id) UNIQUE |
| `wl_confession` | Night confessions | content, nickname, session_id, hug_count |
| `wl_campaign` | Crowdfunding | title, description, funding_goal, current_amount, status (`pending/active/closed/rejected`), images |
| `wl_donation` | Donations | campaign_id, user_id, amount, message, is_anonymous |
| `wl_journal_entry` | Private journal | user_id, title, content, images (JSON), mood, entry_date |
| `wl_respite_request` | Respite map | user_id, request_type (service/equipment), lat, lng, status, acceptor_id |
| `wl_certification` | Certification applications | user_id, cert_type, real_name, id_card, document_url, additional_docs (JSON), status |
| `wl_sensitive_word` | Moderation dictionary | word, severity (1=warn, 2=crisis popup) |

### 2.5 Module-by-Module Walkthrough

#### 2.5.1 Auth (`/auth/*`)
- `login` accepts username, email or phone in the same field; `User.validate_password` uses `werkzeug.security.check_password_hash`.
- `register` enforces minimum length and uniqueness of email/phone; assigns the `regular` role on creation.
- `forgot-password` is a stub UI (no SMTP credentials provisioned on the VM).
- `logout` is POST-only to prevent CSRF via image tags.

#### 2.5.2 Community (`/community/*`)
- 70/30 layout: posts feed on the left, Night Confessions panel on the right (active 21:00–06:00 server-local).
- `Post` supports anonymous mode; when set, the renderer hides username/avatar.
- Liking is AJAX (`POST /community/post/<id>/like`); the like row uses a `(post_id, user_id)` unique index for idempotence.
- Comments support `parent_id` for one-level threading.
- Sensitive-word checking is a two-tier system: severity 1 returns a soft warning, severity 2 surfaces a crisis hotline modal client-side.

#### 2.5.3 Crowdfunding (`/crowdfunding/*`)
- Campaigns are created by certified users only; pending campaigns are gated behind admin approval.
- Donations are simulated (`POST /crowdfunding/campaign/<id>/donate`): `current_amount` is incremented within an SQLAlchemy transaction; the response payload includes the new percentage so the progress bar can animate.
- A campaign auto-marks `is_fully_funded` when `current_amount >= funding_goal`.

#### 2.5.4 Life Journal (`/journal/*`)
- All routes wrap queries with `user_id == current_user.id` so users only see their own entries.
- The Annual Film selects up to 12 entries from a user's chosen year, ordered by month, and renders a fullscreen Ken-Burns slideshow client-side.

#### 2.5.5 Respite Station (`/respite/*`)
- Backed by Leaflet + OpenStreetMap; markers are clustered with `Leaflet.markercluster`.
- Two pin colours: orange = service request, green = equipment lending.
- State machine: `pending → in_progress → completed`. A request cannot be accepted by its creator.
- Mobile layout swaps the side panel for a bottom sheet.

#### 2.5.6 User Centre (`/user/*`)
- Profile, edit, settings, certification application, certification status, and a paginated history page with four tabs (Posts / Campaigns / Donations / Respite Requests).
- Avatar upload uses Flask-Reuploaded with extension whitelist + size limit.

#### 2.5.7 Admin (`/admin/*`)
- Layui-based panel inherited from Pear-Admin-Flask.
- Custom blueprints: `adminCert` (certification review), `adminCampaign` (campaign review), `adminCommunity` (post moderation).
- Each action is gated by the `@authorize("…", log=True)` decorator which writes to the audit log table.

### 2.6 Authentication and Authorisation
- Session auth via Flask-Login; passwords stored as Werkzeug PBKDF2-SHA256 hashes.
- RBAC implemented through `admin_user → admin_user_role → admin_role → admin_role_power → admin_power`. The `authorize` decorator resolves the current user's effective power codes and compares them against the route requirement.
- Route-level protection: blueprint decorators short-circuit unauthenticated requests with a 302 to `/auth/login?next=…`; admin routes additionally require the admin role and return HTTP 403 on mismatch.

### 2.7 Internationalisation
- All user-visible strings wrapped with `{{ _('…') }}` (Jinja) or `gettext(…)` (Python).
- Catalogue maintained at `translations/zh/LC_MESSAGES/messages.po`; 511 strings translated.
- Locale resolution order: `?locale=` query → session → `Accept-Language`. The toggle in the navbar persists the choice via both session and `localStorage`.

### 2.8 Front-End Design System
- Custom CSS variables for the warm "harbor" palette (primary, primary-bg, success, warning, error, text-primary, text-secondary, border, radius-md, shadow-sm, transition-fast).
- Bootstrap 5.3 utility classes for layout; component skins (`wl-tag`, `wl-progress`, `btn-wl-primary`) wrap Bootstrap defaults.
- Lucide icons rendered through `data-lucide` attributes, initialised once per page on `DOMContentLoaded`.
- Leaflet for the map; chart-js is *not* used in this iteration.

### 2.9 Validation, Sanitisation and File Handling
- Server-side: every form field is length-clamped (`[:N]`) and re-validated; emails and phones uniqueness-checked; file uploads pass through `save_upload(file, folder, prefix, allowed_exts=…)`, which:
  1. Verifies extension against an allow-list.
  2. Generates a UUID-prefixed filename to prevent collisions and path traversal.
  3. Writes under `static/uploads/<folder>/`.
- Client-side sensitive-word checking is debounced at 300 ms; the canonical decision still runs on the server.

### 2.10 Deployment
The VM is reached through a UCD jump host that requires password + TOTP. Two flows are supported:
1. **Local one-click:** `./deploy.sh` packages the working tree (excluding `venv`, `.git`, etc.), uploads via `scp`, restores or rebuilds the venv, runs `db.create_all()`, compiles translations, fixes static permissions and restarts Gunicorn.
2. **GitHub Actions on push to `main`:** `.github/workflows/deploy.yml` generates the TOTP from a secret, drives `expect` to negotiate jump-host + VM passwords, then runs `cd ~/weilight-harbor && git fetch origin main && git reset --hard origin/main && bash vm_update.sh`. The `vm_update.sh` script performs the same pip/db/babel/permissions/restart sequence as the local script. After the restart it issues a localhost smoke check (`curl /` should return HTTP 200).

### 2.11 Security Considerations
- Passwords hashed; sessions cookie-based and HTTPOnly.
- All write actions are POST and CSRF-protected through Flask-WTF where forms exist.
- File uploads validated by extension and isolated under `static/uploads/`.
- Admin endpoints behind RBAC + audit log.
- `.gitignore` excludes `*.db`, `*.env`, large vendor JS files; `.DS_Store` excluded from Week 11 onward.
- Limitations acknowledged: no rate limiting; no CAPTCHA; sensitive-word list is finite and bypassable; the platform is **not** PCI-compliant and intentionally simulates donations.

### 2.12 Testing Strategy
- Manual smoke testing against every primary user journey with the seeded demo accounts (`admin`, `limei`, `zhangwei`, `wangfang`, `chenyun`, `liuyang`, `sunli`, `zhaojing`).
- `flask seed` and `flask seed-demo` CLI commands keep test data reproducible.
- Cross-browser sanity: Chrome 124, Firefox 125, Safari 17.4, Edge 124 (desktop); iOS Safari and Android Chrome (mobile).
- Performance: Lighthouse desktop run on the live VM yields ≥90 on Performance, ≥95 on Best Practices for the landing page.

### 2.13 Limitations and Known Issues
- SQLite write contention under heavy concurrency (acceptable for the assignment scale).
- The "Annual Film" only renders if a user has ≥10 entries in a year.
- Forgot-password flow is UI-only; no real e-mail is sent.
- The map uses public OpenStreetMap tiles (rate-limited).

---

## 3. Generative AI Use  *(1–2 pages)*

### 3.1 Tools Used
- **ChatGPT (GPT-4 / GPT-4o)** — high-level architectural reasoning, model design discussions, copy and microcopy drafting, debugging.
- **Claude (Sonnet / Opus)** — long-context refactoring across multiple files, Jinja template clean-up, deployment script reasoning.
- **GitHub Copilot** — line-level autocompletion inside VS Code.

### 3.2 Where AI Helped
| Area | How it was used |
|---|---|
| Initial scaffolding | Drafting blueprint folder structure, route stubs, model fields. |
| UI copy (bilingual) | Drafting Mandarin and English microcopy for empty states, errors, modals; we then revised tone to fit the warm/quiet palette. |
| Refactors | Extracting shared decorators, normalising form-validation patterns, cleaning Jinja macros. |
| Deployment debugging | Diagnosing why GitHub Actions reported `__RC__:0` while the live site was unchanged (root cause: missing `cd ~/weilight-harbor` in the remote command). |
| Documentation | First drafts of `README.md` and these system/user documents. |

### 3.3 Where AI Was Avoided
- Decisions on data model, user roles and module boundaries were taken by the team based on the product brief; AI suggestions were treated as inputs, not authority.
- Sensitive-word list, illness categories, and crisis-hotline copy were authored manually to avoid hallucinated or insensitive content.
- All AI-suggested code was reviewed, tested and edited before commit.

### 3.4 Verification Practices
- Every AI-suggested file was opened, read top-to-bottom and run locally before pushing.
- For any AI-drafted SQL or migration logic we re-checked behaviour against `db.create_all()` on a fresh SQLite file.
- For deployment scripts we cross-checked the `expect` interaction by running `./deploy.sh` against the staging VM before adopting it.

### 3.5 Reflection
Generative AI most clearly accelerated *boilerplate*: form rendering, internationalisation wrapping, repeated validation. It was less useful for *taste-sensitive* work — palette, microcopy tone, illness terminology — where unchecked output would have damaged the empathic posture the platform is built around. The net effect was perhaps **30–40 % effort saved on plumbing**, with no measurable saving on design judgement.

---

## 4. Team Contribution  *(3–4 pages — placeholder)*

> The contribution table below is a placeholder for the Week 11 draft. Final names and percentages will be confirmed before the Week 13 final submission. Each row is intended to be replaced with: full name, student number, modules owned, key commits, % contribution.

### 4.1 Contribution Matrix (placeholder)
| Member | Modules / Areas | Notable Deliverables | % |
|---|---|---|---|
| Member A (TBD) | Auth, User Centre, Certification | Login/Register, Profile, Certification flow, History page | TBD |
| Member B (TBD) | Community, Sensitive Words, Night Confessions | Feed UI, like/comment, anonymous post, time-gated panel | TBD |
| Member C (TBD) | Crowdfunding, Donation Flow | Campaign listing/detail, simulated donate, progress animation | TBD |
| Member D (TBD) | Journal, Annual Film | Timeline UI, mood tracking, Ken-Burns slideshow | TBD |
| Member E (TBD) | Respite Station, Map | Leaflet integration, marker clustering, accept/complete | TBD |
| Member F (TBD) | Admin Panel, RBAC, Deployment, i18n | Admin review pages, Babel catalogue, Nginx/Gunicorn, GitHub Actions | TBD |

### 4.2 Working Practices
- Source control on GitHub with feature branches and `main` deploy on push.
- Issue tracking on the GitHub Issues board, grouped by module.
- Weekly synchronous meeting; asynchronous coordination on WeChat.
- Code review: at least one peer review on non-trivial PRs; AI-generated code requires the author to walk a peer through the diff before merge.

### 4.3 Individual Reflections (placeholder)
*To be filled in by each member before final submission, ≈150 words each.*

---

## 5. Conclusion  *(≤1 page)*

Weilight Harbor delivers, end-to-end, a multi-module web platform that places caregiver wellbeing at its centre. The five user-facing modules, an admin moderation back office, RBAC, full Mandarin/English internationalisation and an automated deployment pipeline are all live on the assigned UCD VM. Generative AI tooling shortened plumbing work but was deliberately kept out of taste-sensitive content. Limitations — SQLite scale, simulated donations, stubbed e-mail — are acknowledged and documented; none are blockers for the academic scope of the assignment. The remaining iteration before submission will focus on user-acceptance feedback from the Week 12 peer testing, accessibility refinement, and final per-member reflection write-ups.

---

## Appendix A — Selected Routes
*(condensed; full table in `README.md`)*

| Method | Path | Purpose |
|---|---|---|
| GET/POST | `/auth/login` | Login |
| GET/POST | `/auth/register` | Register |
| GET | `/community/` | Post feed |
| POST | `/community/post/<id>/like` | Toggle like |
| GET | `/crowdfunding/` | Campaign listing |
| POST | `/crowdfunding/campaign/<id>/donate` | Simulated donation |
| GET | `/journal/` | Private timeline |
| GET | `/respite/` | Map page |
| GET | `/user/history` | Activity history |
| GET | `/admin/certification/` | Certification queue |

## Appendix B — Seeded Test Accounts
| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | Administrator |
| `limei` | `test123` | Certified Family |
| `zhangwei` | `test123` | Regular User |
| `wangfang` | `test123` | Certified Volunteer |
| `chenyun` | `test123` | Certified Family |
| `liuyang` | `test123` | Regular User (pending certification) |
| `sunli` | `test123` | Certified Family |
| `zhaojing` | `test123` | Certified Volunteer |

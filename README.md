# Weilight Harbor (微光港湾)

A warm harbor for caregivers and families facing serious illness. Built for COMP3030J Web Development (UCD, 2024).

**Live Site:** http://csi6220-2-vm3.ucd.ie
**Repository:** https://github.com/licctvcctv/weilight-harbor

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started (Local Development)](#getting-started-local-development)
- [Deployment to VM](#deployment-to-vm)
- [Test Accounts](#test-accounts)
- [API Endpoints](#api-endpoints)
- [i18n (Internationalization)](#i18n-internationalization)
- [Database Schema](#database-schema)
- [Team](#team)

---

## Overview

Weilight Harbor is a charity/mutual-aid web platform designed for caregivers of patients with serious illnesses. The platform provides five core modules:

1. **Community (共鸣社区)** - A social forum for caregivers to share experiences, with Night Confessions (深夜独白) for anonymous after-dark support
2. **Crowdfunding (微光筹)** - A fundraising platform where verified caregivers can launch campaigns and receive simulated donations
3. **Life Journal (生命手账)** - A private timeline diary with photo uploads and an Annual Film feature
4. **Respite Station (喘息驿站)** - An interactive map for requesting/offering temporary care help and equipment lending
5. **Admin Panel (管理后台)** - Review certifications, moderate community content, and approve crowdfunding campaigns

Three user roles are supported:
- **Regular User** - Browse, donate, post in community
- **Certified Family/Volunteer** - All above + create campaigns, accept respite requests, journal access
- **Administrator** - All above + admin panel for reviews and moderation

---

## Features

| Module | Key Features |
|--------|-------------|
| **Auth** | Login (username/email), Register, Forgot Password, Logout |
| **Community** | Post CRUD, category filtering, sort (latest/hot/empathy), likes ("I feel the same"), comments with replies, image upload (max 9), anonymous posting, sensitive word detection |
| **Night Confessions** | Time-gated (21:00-06:00), anonymous, "Hug" reactions, mobile bottom sheet, crisis hotline popup |
| **Crowdfunding** | Campaign CRUD with admin approval, simulated donations, progress bars, search, donor list, "Fully Funded" badge |
| **Life Journal** | Private timeline, mood tracking (5 emojis), photo diary, year/month filtering, Annual Film slideshow |
| **Respite Station** | Leaflet/OpenStreetMap, orange (service) / green (equipment) pins, marker clustering, radius filter, accept/complete flow |
| **User Center** | Profile, avatar upload, edit profile, certification application, status tracker, history (posts/campaigns/donations/requests), settings, change password |
| **Admin** | Certification review (approve/reject), Campaign review, Community moderation (approve/hide/delete) |
| **i18n** | Full Chinese/English toggle (511 translated strings), session + localStorage persistence |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10, Flask 3.x, SQLAlchemy, Flask-Login, Flask-Babel |
| **Frontend** | Bootstrap 5.3, Jinja2 templates, Lucide Icons, Leaflet.js |
| **Database** | SQLite |
| **Server** | Gunicorn (WSGI) + Nginx (reverse proxy) |
| **Deployment** | Ubuntu 22.04 VM, systemd services |
| **Admin Panel** | Layui (pear-admin-flask base) |

---

## Project Structure

```
weilight-harbor/
├── app.py                              # Flask app entry point
├── deploy.sh                           # One-click deployment to VM
├── vm_update.sh                        # Update script (run on VM after git pull)
├── babel.cfg                           # Flask-Babel extraction config
│
├── applications/
│   ├── __init__.py                     # App factory (create_app)
│   ├── configs/config.py              # Config (SQLite, Babel, uploads)
│   ├── extensions/                     # Flask extensions init
│   ├── models/                         # Database models (12 tables)
│   ├── view/                           # Route blueprints
│   │   ├── auth/                      # /auth/* (login, register, logout)
│   │   ├── community/                 # /community/* (posts, confessions)
│   │   ├── crowdfunding/              # /crowdfunding/* (campaigns, donate)
│   │   ├── journal/                   # /journal/* (timeline, entries)
│   │   ├── respite/                   # /respite/* (map, requests)
│   │   ├── user_center/              # /user/* (profile, settings)
│   │   ├── index/                     # / (landing, about, help, etc.)
│   │   └── admin/                     # /admin/* (review panels)
│   └── common/utils/                   # Shared utilities
│
├── templates/
│   ├── public/                         # Bootstrap 5 frontend (27 templates)
│   └── admin/                          # Layui admin panel
│
├── static/
│   ├── public/                         # CSS design system + JS modules
│   └── admin/                          # Layui assets
│
└── translations/zh/LC_MESSAGES/        # Chinese translations (511 strings)
```

---

## Getting Started (Local Development)

### Prerequisites

- Python 3.9+
- pip

### Setup

```bash
# Clone the repository
git clone https://github.com/licctvcctv/weilight-harbor.git
cd weilight-harbor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-sqlalchemy flask-login flask-migrate flask-babel \
  flask-marshmallow marshmallow-sqlalchemy Pillow python-dotenv flask-mail \
  psutil flask-apscheduler captcha werkzeug wtforms flask-wtf sqlparse \
  webargs gunicorn Flask-Reuploaded

# Create .flaskenv
echo "FLASK_APP=app.py" > .flaskenv

# Initialize database and seed demo data
flask seed-demo

# Compile translations
pybabel compile -d translations

# Run development server
flask run --port 5000
```

Visit http://localhost:5000

### CLI Commands

| Command | Description |
|---------|-------------|
| `flask seed` | Seed base data (roles, admin user, sensitive words) |
| `flask seed-demo` | Seed rich demo data (8 users, 12 posts, 7 campaigns, etc.) |

---

## Deployment to VM

### VM Details

| Item | Value |
|------|-------|
| **VM Hostname** | csi6220-2-vm3.ucd.ie |
| **VM IP** | 137.43.49.37 |
| **SSH User** | student |
| **Jump Host** | ipa-rdp.ucd.ie |
| **OS** | Ubuntu 22.04.5 LTS |
| **Python** | 3.10.12 |

### Architecture

```
Internet --> Nginx (port 80) --> Unix Socket --> Gunicorn --> Flask App
                  |
           /static/ served directly by Nginx
```

### Method 1: One-click Deploy (from local machine)

```bash
./deploy.sh
```

This script automatically handles: package -> upload to jump host -> SCP to VM -> extract -> venv -> pip install -> db init -> seed -> compile translations -> fix permissions -> restart Gunicorn -> verify.

### Method 2: Git Pull (on VM)

```bash
# SSH to VM (via jump host)
ssh CS23219619@ipa-rdp.ucd.ie     # password + TOTP code
ssh student@csi6220-2-vm3.ucd.ie  # VM password

# Pull and update
cd ~/weilight-harbor
git pull origin main
bash vm_update.sh
```

### Systemd Service Files

**gunicorn.service** (`/etc/systemd/system/gunicorn.service`):
```ini
[Unit]
Description=gunicorn daemon for weilight-harbor
Requires=gunicorn.socket
After=network.target

[Service]
Type=notify
User=student
Group=student
RuntimeDirectory=gunicorn
WorkingDirectory=/home/student/weilight-harbor
ExecStart=/home/student/weilight-harbor/venv/bin/gunicorn -c gunicorn.conf.py "applications:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**gunicorn.socket** (`/etc/systemd/system/gunicorn.socket`):
```ini
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock
SocketUser=www-data

[Install]
WantedBy=sockets.target
```

**Nginx config** (`/etc/nginx/sites-available/csi6220-2-vm3.ucd.ie`):
```nginx
upstream app_server {
    server unix:/run/gunicorn.sock fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name csi6220-2-vm3.ucd.ie;
    client_max_body_size 20M;

    location /static/ {
        alias /home/student/weilight-harbor/static/;
        expires 30d;
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://app_server;
    }
}
```

### Useful VM Commands

```bash
sudo systemctl restart gunicorn    # Restart app after code changes
sudo systemctl status gunicorn     # Check app status
sudo journalctl -u gunicorn -f     # View app logs
sudo systemctl restart nginx       # Restart Nginx
sudo nginx -t                      # Check Nginx config
```

---

## Test Accounts

| Username | Password | Role | Description |
|----------|----------|------|-------------|
| `admin` | `admin123` | Administrator | Full admin access |
| `limei` | `test123` | Certified Family | ALS caregiver, has campaigns |
| `zhangwei` | `test123` | Regular User | Donor, tech background |
| `wangfang` | `test123` | Certified Volunteer | Retired nurse |
| `chenyun` | `test123` | Certified Family | Alzheimer's caregiver |
| `liuyang` | `test123` | Regular User | Has pending certification |
| `sunli` | `test123` | Certified Family | Pediatric cancer caregiver |
| `zhaojing` | `test123` | Certified Volunteer | Social worker |

---

## API Endpoints

### Public Pages
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Landing page |
| GET | `/about` | About page |
| GET | `/help` | Help / FAQ |
| GET | `/privacy` | Privacy policy |
| GET | `/terms` | Terms of service |

### Auth (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| GET/POST | `/auth/login` | Login |
| GET/POST | `/auth/register` | Register |
| GET/POST | `/auth/forgot-password` | Forgot password |
| POST | `/auth/logout` | Logout |

### Community (`/community`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/community/` | Post listing (`?category=`, `?sort=`, `?page=`) |
| GET | `/community/post/<id>` | Post detail |
| GET/POST | `/community/create` | Create post |
| POST | `/community/post/<id>/like` | Toggle like (AJAX) |
| POST | `/community/post/<id>/comment` | Add comment |
| POST | `/community/post/<id>/delete` | Soft delete post |
| GET | `/community/confessions` | Load confessions (JSON) |
| POST | `/community/confessions` | Submit confession (JSON) |
| POST | `/community/confessions/<id>/hug` | Hug reaction (JSON) |
| POST | `/community/check-sensitive` | Sensitive word check (JSON) |

### Crowdfunding (`/crowdfunding`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/crowdfunding/` | Campaign listing |
| GET | `/crowdfunding/campaign/<id>` | Campaign detail |
| GET/POST | `/crowdfunding/create` | Create campaign (certified only) |
| POST | `/crowdfunding/campaign/<id>/donate` | Simulated donation (AJAX) |
| GET | `/crowdfunding/search?q=` | Search campaigns |

### Life Journal (`/journal`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/journal/` | Timeline (`?year=`, `?month=`) |
| GET/POST | `/journal/create` | New entry |
| GET | `/journal/entry/<id>` | View entry |
| GET/POST | `/journal/entry/<id>/edit` | Edit entry |
| POST | `/journal/entry/<id>/delete` | Delete entry |
| GET | `/journal/annual-film` | Annual Film slideshow |

### Respite Station (`/respite`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/respite/` | Map page |
| GET | `/respite/requests` | Active requests (JSON, `?type=`) |
| GET | `/respite/request/<id>` | Request detail (JSON) |
| POST | `/respite/create` | Create request (certified only) |
| POST | `/respite/request/<id>/accept` | Accept request |
| POST | `/respite/request/<id>/complete` | Mark completed |

### User Center (`/user`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/user/profile` | User profile |
| GET/POST | `/user/edit` | Edit profile |
| GET/POST | `/user/certification` | Certification application |
| GET | `/user/certification/status` | Status tracker |
| GET | `/user/history` | Activity history |
| GET/POST | `/user/settings` | Account settings |

### Admin (`/admin`)
| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/certification/` | Certification review |
| PUT | `/admin/certification/approve/<id>` | Approve |
| PUT | `/admin/certification/reject/<id>` | Reject |
| GET | `/admin/campaign-review/` | Campaign review |
| PUT | `/admin/campaign-review/approve/<id>` | Approve |
| PUT | `/admin/campaign-review/reject/<id>` | Reject |
| GET | `/admin/community/` | Community moderation |
| PUT | `/admin/community/approve/<id>` | Approve post |
| PUT | `/admin/community/hide/<id>` | Hide post |
| DELETE | `/admin/community/delete/<id>` | Delete post |

### Utility
| Method | Path | Description |
|--------|------|-------------|
| POST | `/set-locale` | Switch language (`{"locale": "zh"}` or `{"locale": "en"}`) |

---

## i18n (Internationalization)

Toggle language via the `中/EN` button in the navbar. 511 strings fully translated.

### Updating translations

```bash
# Extract new strings
pybabel extract -F babel.cfg -o translations/messages.pot .

# Update catalog
pybabel update -i translations/messages.pot -d translations

# Edit translations/zh/LC_MESSAGES/messages.po

# Compile
pybabel compile -d translations
```

---

## Database Schema

| Table | Description | Key Fields |
|-------|-------------|------------|
| `admin_user` | Users (extended) | username, email, phone, user_type, is_certified, locale |
| `admin_role` | RBAC roles | name, code (regular/certified_family/certified_volunteer/admin) |
| `wl_post` | Community posts | user_id, title, content, category, images(JSON), like_count |
| `wl_comment` | Comments | post_id, user_id, content, parent_id (threading) |
| `wl_post_like` | Likes | post_id, user_id (unique) |
| `wl_confession` | Night Confessions | content, nickname, session_id, hug_count |
| `wl_campaign` | Crowdfunding | user_id, title, funding_goal, current_amount, status |
| `wl_donation` | Donations | campaign_id, user_id, amount, message, is_anonymous |
| `wl_journal_entry` | Journal | user_id, title, content, images(JSON), mood, entry_date |
| `wl_respite_request` | Respite | user_id, request_type, lat, lng, status, acceptor_id |
| `wl_certification` | Certifications | user_id, cert_type, status, patient_illness, hospital_name |
| `wl_sensitive_word` | Sensitive words | word, severity (1=warning, 2=crisis popup) |

---

## Team

**Group 14** - COMP3030J Web Development, University College Dublin, 2024

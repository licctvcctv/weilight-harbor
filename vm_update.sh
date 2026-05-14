#!/bin/bash
# ============================================
# Run this ON THE VM after git pull
# Usage: cd ~/weilight-harbor && bash vm_update.sh
# ============================================
set -e

echo "🔄 Updating Weilight Harbor..."

# Activate venv
source venv/bin/activate

# Install any new dependencies
pip install -q -r requirements.txt 2>/dev/null || pip install -q \
    flask flask-sqlalchemy flask-login flask-migrate flask-babel \
    flask-marshmallow marshmallow-sqlalchemy Pillow python-dotenv flask-mail \
    psutil flask-apscheduler captcha werkzeug wtforms flask-wtf sqlparse \
    webargs gunicorn Flask-Reuploaded

# Update database tables (idempotent — keeps existing rows)
export FLASK_APP=app.py
python3 -c "from applications import create_app; from applications.extensions import db; app=create_app(); app.app_context().push(); db.create_all()"

# Seed demo data if the database is empty (first deploy or after clean)
USER_COUNT=$(python3 -c "
from applications import create_app
from applications.extensions import db
from applications.models import User
app = create_app(); app.app_context().push()
print(User.query.count())
" 2>/dev/null || echo 0)

if [ "${USER_COUNT}" = "0" ]; then
    echo "📦 Empty database detected, running seed-demo..."
    flask seed-demo
else
    echo "ℹ️  Database has ${USER_COUNT} users; skipping seed."
fi

# Compile translations
pybabel compile -d translations

# Fix permissions
chmod -R 755 static/

# Restart gunicorn (sudo will prompt for password if not NOPASSWD)
sudo systemctl restart gunicorn

echo "✅ Update complete! Site is live."

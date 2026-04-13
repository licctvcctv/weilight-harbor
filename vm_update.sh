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
pip install -q -r requirements.txt 2>/dev/null || pip install -q flask flask-sqlalchemy flask-login flask-migrate flask-babel flask-marshmallow marshmallow-sqlalchemy Pillow python-dotenv flask-mail psutil flask-apscheduler captcha werkzeug wtforms flask-wtf sqlparse webargs gunicorn Flask-Reuploaded

# Update database tables
export FLASK_APP=app.py
python3 -c "from applications import create_app; from applications.extensions import db; app=create_app(); app.app_context().push(); db.create_all()"

# Compile translations
pybabel compile -d translations

# Fix permissions
chmod -R 755 static/

# Restart gunicorn
sudo systemctl restart gunicorn

echo "✅ Update complete! Site is live."

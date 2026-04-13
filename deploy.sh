#!/bin/bash
# ============================================
# Weilight Harbor - One-click Deploy to UCD VM
# ============================================
# Usage: ./deploy.sh
#
# Prerequisites:
#   - pip install pyotp sshpass (on local machine)
#   - SSH access to ipa-rdp.ucd.ie (jumper)
#   - TOTP secret key set in TOTP_SECRET env var
#
# Config (edit these):
JUMPER_USER="CS23219619"
JUMPER_HOST="ipa-rdp.ucd.ie"
JUMPER_PASS="CKOcSeiRGhYZQVZn"
TOTP_SECRET="${TOTP_SECRET:-C2DB364C7ZDSFHIQWGVEAA3QLA}"

VM_USER="student"
VM_HOST="csi6220-2-vm3.ucd.ie"
VM_PASS="group14good!"

PROJECT_DIR="/home/student/weilight-harbor"
# ============================================

set -e

echo "🚢 Weilight Harbor Deployment"
echo "=============================="

# Step 1: Package project
echo "📦 Packaging project..."
tar czf /tmp/weilight-deploy.tar.gz \
  --exclude='venv' --exclude='__pycache__' --exclude='.git' \
  --exclude='*.pyc' --exclude='*.db' --exclude='references' \
  --exclude='*.pdf' --exclude='*.docx' --exclude='product_design.md' \
  -C "$(dirname "$(cd "$(dirname "$0")" && pwd)")" weilight-harbor

# Step 2: Generate TOTP
TOTP=$(python3 -c "import pyotp; print(pyotp.TOTP('${TOTP_SECRET}').now())")
echo "🔑 TOTP generated: ${TOTP}"

# Step 3: Upload to jumper
echo "⬆️  Uploading to jumper..."
expect -c "
set timeout 60
spawn scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/weilight-deploy.tar.gz ${JUMPER_USER}@${JUMPER_HOST}:/tmp/
expect \"*assword*\"
send \"${JUMPER_PASS}\r\"
expect \"*erification*\"
send \"${TOTP}\r\"
expect eof
" 2>&1 | grep -E "100%|Error" || true

# Step 4: Deploy via jumper -> VM
echo "🚀 Deploying to VM..."
TOTP=$(python3 -c "import pyotp; print(pyotp.TOTP('${TOTP_SECRET}').now())")

expect -c "
set timeout 300
spawn ssh -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${JUMPER_USER}@${JUMPER_HOST}
expect \"*assword*\"
send \"${JUMPER_PASS}\r\"
expect \"*erification*\"
send \"${TOTP}\r\"
expect \"ipa-rdp\"

# SCP to VM
send \"scp -o StrictHostKeyChecking=no /tmp/weilight-deploy.tar.gz ${VM_USER}@${VM_HOST}:/tmp/\r\"
expect \"*assword*\"
send \"${VM_PASS}\r\"
expect \"ipa-rdp\"

# SSH to VM and deploy
send \"ssh -tt -o StrictHostKeyChecking=no ${VM_USER}@${VM_HOST}\r\"
expect \"*assword*\"
send \"${VM_PASS}\r\"
expect \"student@csi\"

# Extract (preserve venv if exists)
send \"cd ~ && rm -rf weilight-harbor-old && mv weilight-harbor weilight-harbor-old 2>/dev/null; tar xzf /tmp/weilight-deploy.tar.gz && echo EXTRACTED\r\"
expect \"EXTRACTED\"
expect \"student@csi\"

# Restore or create venv
send \"cd ~/weilight-harbor && if test -d ~/weilight-harbor-old/venv; then cp -r ~/weilight-harbor-old/venv ./venv; echo VENV_RESTORED; else python3 -m venv venv && echo VENV_CREATED; fi\r\"
expect {
    \"VENV_RESTORED\" {}
    \"VENV_CREATED\" {}
}
expect \"student@csi\"

# Install deps
send \"cd ~/weilight-harbor && source venv/bin/activate && pip install -q flask flask-sqlalchemy flask-login flask-migrate flask-babel flask-marshmallow marshmallow-sqlalchemy Pillow python-dotenv flask-mail psutil flask-apscheduler captcha werkzeug wtforms flask-wtf sqlparse webargs gunicorn Flask-Reuploaded 2>&1 | tail -1\r\"
expect \"student@csi\"

# Init DB + seed + compile translations
send \"export FLASK_APP=app.py && python3 -c \\\"from applications import create_app; from applications.extensions import db; app=create_app(); app.app_context().push(); db.create_all()\\\" && flask seed-demo 2>&1 | tail -3\r\"
expect \"student@csi\"

send \"pybabel compile -d translations 2>&1 | tail -1\r\"
expect \"student@csi\"

# Fix permissions
send \"chmod 755 /home/student && chmod -R 755 /home/student/weilight-harbor/static\r\"
expect \"student@csi\"

# Restart services
send \"sudo systemctl daemon-reload && sudo systemctl restart gunicorn && echo SVC_OK\r\"
expect {
    \"*assword for student*\" { send \"${VM_PASS}\r\"; exp_continue }
    \"SVC_OK\" {}
}
expect \"student@csi\"

# Test
send \"sleep 2 && curl -s -o /dev/null -w HTTP_%{http_code} http://localhost/ && echo _LIVE\r\"
expect \"_LIVE\"

send \"exit\r\"
expect \"ipa-rdp\"
send \"exit\r\"
expect eof
" 2>&1 | grep -E "EXTRACTED|VENV|seed|compil|SVC_OK|HTTP_|LIVE|Error"

echo ""
echo "✅ Deployment complete!"
echo "🌐 Visit: http://${VM_HOST}"

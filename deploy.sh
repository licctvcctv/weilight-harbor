#!/bin/bash
# ============================================
# Weilight Harbor — local one-click deploy
# ============================================
# Usage:
#   ./deploy.sh           Deploy: VM resets to origin/main and runs vm_update.sh
#   ./deploy.sh --diag    Inspect VM state only (no deploy)
#   ./deploy.sh -h        Show this help
#
# Override defaults via env vars:
#   JUMPER_USER, JUMPER_PASS, TOTP_SECRET,
#   VM_USER, VM_PASS, VM_HOST, PROJECT_DIR, BRANCH, SITE_URL.
#
# Prerequisites:
#   - expect, curl, git, python3 with the 'pyotp' module
# ============================================
set -euo pipefail

# --- Style helpers ---------------------------------------------------------
GREEN=$'\033[1;32m'; RED=$'\033[1;31m'; YEL=$'\033[1;33m'; BLU=$'\033[1;36m'; NC=$'\033[0m'
log()  { printf '%s[deploy]%s %s\n' "$BLU" "$NC" "$*"; }
ok()   { printf '%s✓%s %s\n' "$GREEN" "$NC" "$*"; }
warn() { printf '%s⚠%s %s\n' "$YEL" "$NC" "$*"; }
err()  { printf '%s✗%s %s\n' "$RED" "$NC" "$*" >&2; }

usage() { sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'; }

# --- Config (env vars override defaults) -----------------------------------
JUMPER_USER="${JUMPER_USER:-CS23219619}"
JUMPER_HOST="${JUMPER_HOST:-ipa-rdp.ucd.ie}"
JUMPER_PASS="${JUMPER_PASS:-CKOcSeiRGhYZQVZn}"
TOTP_SECRET="${TOTP_SECRET:-C2DB364C7ZDSFHIQWGVEAA3QLA}"
VM_USER="${VM_USER:-student}"
VM_HOST="${VM_HOST:-csi6220-2-vm3.ucd.ie}"
VM_PASS="${VM_PASS:-group14good!}"
PROJECT_DIR="${PROJECT_DIR:-/home/student/weilight-harbor}"
REPO_URL="${REPO_URL:-https://github.com/licctvcctv/weilight-harbor.git}"
BRANCH="${BRANCH:-main}"
SITE_URL="${SITE_URL:-http://${VM_HOST}}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- Flags -----------------------------------------------------------------
MODE="deploy"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --diag)        MODE="diag"; shift ;;
        -h|--help)     usage; exit 0 ;;
        *)             err "Unknown argument: $1"; usage; exit 1 ;;
    esac
done

# --- Pre-flight ------------------------------------------------------------
for tool in expect python3 curl git; do
    command -v "$tool" >/dev/null 2>&1 || { err "Missing required tool: $tool"; exit 1; }
done

if ! python3 -c 'import pyotp' 2>/dev/null; then
    err "Python module 'pyotp' missing. Install with one of:"
    err "    python3 -m pip install --user pyotp"
    err "    python3 -m venv ~/.wlh-venv && ~/.wlh-venv/bin/pip install pyotp"
    exit 1
fi

# --- Local sanity ----------------------------------------------------------
LOCAL_SHA=""
if [[ "$MODE" == "deploy" ]]; then
    cd "$SCRIPT_DIR"
    LOCAL_SHA=$(git rev-parse "$BRANCH" 2>/dev/null) \
        || { err "Local branch '$BRANCH' not found"; exit 1; }

    REMOTE_SHA=$(git ls-remote --quiet "$REPO_URL" "refs/heads/$BRANCH" \
                  | awk '{print $1}' || true)

    log "Local  $BRANCH:  $LOCAL_SHA"
    log "Remote $BRANCH: ${REMOTE_SHA:-?}"

    if [[ -n "$REMOTE_SHA" && "$LOCAL_SHA" != "$REMOTE_SHA" ]]; then
        warn "Local commits differ from origin/$BRANCH."
        warn "The VM will reset to origin/$BRANCH (the remote commit)."
        warn "Push first if you want the VM to run your latest local code:"
        warn "    git push origin $BRANCH"
        read -r -p "Continue anyway? [y/N] " ans
        [[ "$ans" =~ ^[Yy]$ ]] || exit 1
    fi

    if ! git diff --quiet || ! git diff --cached --quiet; then
        warn "Working tree has uncommitted changes — they will NOT be deployed."
    fi
fi

# --- Build remote command (one logical command, RC propagates) -------------
case "$MODE" in
    deploy)
        REMOTE_CMD="set -e; cd '${PROJECT_DIR}'; \
if ! git remote get-url origin >/dev/null 2>&1; then git remote add origin '${REPO_URL}'; fi; \
git fetch origin '${BRANCH}'; \
git checkout -fB '${BRANCH}' FETCH_HEAD; \
git reset --hard FETCH_HEAD; \
git clean -fd; \
bash vm_update.sh; \
printf '__SHA__:%s\\n' \$(git rev-parse HEAD)"
        ;;
    diag)
        REMOTE_CMD="cd '${PROJECT_DIR}' 2>/dev/null && { \
echo '== gunicorn =='; sudo -n systemctl is-active gunicorn 2>&1 | head -1; \
echo '== gunicorn cwd =='; ls -l /proc/\$(pgrep -f 'gunicorn.*applications' | head -1)/cwd 2>/dev/null || echo no-pid; \
echo '== repo =='; git log -1 --oneline; git status -s | head -5; \
echo '== file timestamps =='; stat -c '%y %n' templates/public/user/history.html templates/admin/community/main.html 2>/dev/null; \
printf '__SHA__:%s\\n' \$(git rev-parse HEAD); }"
        ;;
esac

# --- TOTP (just-in-time so it's fresh) -------------------------------------
TOTP=$(python3 -c "import pyotp; print(pyotp.TOTP('${TOTP_SECRET}').now())")
log "Generated TOTP for jump host"

# --- Drive expect through jumper -> VM -------------------------------------
DEPLOY_LOG="$(mktemp -t wlh-deploy.XXXXXX)"
trap 'rm -f "$DEPLOY_LOG"' EXIT
export JUMPER_USER JUMPER_HOST JUMPER_PASS VM_USER VM_HOST VM_PASS TOTP REMOTE_CMD

log "Connecting to VM through jump host..."

set +e
expect <<'EXPECT_EOF' | tee "$DEPLOY_LOG"
set timeout 900
log_user 1

spawn ssh -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    $env(JUMPER_USER)@$env(JUMPER_HOST)
expect {
    -nocase -re "password" { send "$env(JUMPER_PASS)\r"; exp_continue }
    -nocase -re "verification" { send "$env(TOTP)\r"; exp_continue }
    -re {ipa-rdp[^\$#]*[\$#] ?$} {}
    timeout { send_user "\nTIMEOUT_JUMPER\n"; exit 10 }
    eof     { send_user "\nEOF_JUMPER\n";     exit 10 }
}

send "ssh -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $env(VM_USER)@$env(VM_HOST)\r"
expect {
    -nocase -re "password" { send "$env(VM_PASS)\r"; exp_continue }
    -re {csi6220-2-vm3[^\$#]*[\$#] ?$} {}
    timeout { send_user "\nTIMEOUT_VM\n"; exit 11 }
    eof     { send_user "\nEOF_VM\n";     exit 11 }
}

send "$env(REMOTE_CMD)\r"
expect {
    -nocase -re "password for" { send "$env(VM_PASS)\r"; exp_continue }
    -re {__SHA__:[A-Za-z0-9]+} { exp_continue }
    -re {csi6220-2-vm3[^\$#]*[\$#] ?$} {}
    timeout { send_user "\nTIMEOUT_DEPLOY\n"; exit 12 }
    eof     { send_user "\nEOF_DEPLOY\n";     exit 12 }
}

send "printf '__RC__:%s\\n' \$?\r"
expect {
    -re {__RC__:0\r?\n}            { send_user "\n(deploy) RC=0\n" }
    -re {__RC__:([1-9][0-9]*)\r?\n} {
        send_user "\n(deploy) RC=$expect_out(1,string)\n"
        send "exit\r"; expect -re {ipa-rdp} { send "exit\r" }
        exit 13
    }
    timeout { send_user "\nTIMEOUT_RC\n"; exit 14 }
}

send "exit\r"
expect {
    -re {ipa-rdp[^\$#]*[\$#] ?$} {}
    timeout {}
}
send "exit\r"
expect eof
EXPECT_EOF
EXPECT_RC=$?
set -e

if [[ $EXPECT_RC -ne 0 ]]; then
    err "Remote session failed (expect exit code $EXPECT_RC)"
    exit "$EXPECT_RC"
fi

# --- Capture deployed SHA --------------------------------------------------
DEPLOYED_SHA=$(grep -oE '__SHA__:[A-Za-z0-9]+' "$DEPLOY_LOG" | tail -1 | cut -d: -f2 || true)

if [[ -n "$DEPLOYED_SHA" ]]; then
    log "VM HEAD: $DEPLOYED_SHA"
else
    warn "Could not capture deployed SHA from session output"
fi

if [[ "$MODE" == "diag" ]]; then
    ok "Diagnostics complete"
    exit 0
fi

# --- Verify SHA match ------------------------------------------------------
if [[ -n "$DEPLOYED_SHA" && -n "$LOCAL_SHA" ]]; then
    if [[ "$DEPLOYED_SHA" == "$LOCAL_SHA" ]]; then
        ok "VM HEAD matches local $BRANCH"
    else
        warn "VM HEAD ($DEPLOYED_SHA) does not match local $BRANCH ($LOCAL_SHA)"
        warn "Hint: did you 'git push origin $BRANCH' before deploying?"
    fi
fi

# --- Smoke test ------------------------------------------------------------
log "Smoke-testing $SITE_URL ..."
HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$SITE_URL/" || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    ok "Landing page reachable (HTTP 200)"
else
    err "Landing page returned HTTP $HTTP_CODE"
    exit 3
fi

if curl -s --max-time 15 "$SITE_URL/" | grep -q "Weilight Harbor"; then
    ok "Landing page contains brand string"
else
    warn "Landing page reachable but brand string not found (template may be cached)"
fi

ok "Deployment complete"
echo "🌐 $SITE_URL"

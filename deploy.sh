#!/bin/bash
# ============================================
# Weilight Harbor — local one-click deploy
# ============================================
# Usage:
#   ./deploy.sh                  Deploy: VM resets to origin/main and runs vm_update.sh
#   ./deploy.sh --diag           Inspect VM state only (no deploy)
#   ./deploy.sh --sync-vendor    Upload large layui/tinymce/echarts vendor files
#   ./deploy.sh --no-vendor      Skip auto vendor check during deploy
#   ./deploy.sh --quiet          Suppress remote SSH banners (only show key output)
#   ./deploy.sh -h               Show this help
#
# A normal deploy auto-checks the layui.js asset on the VM and triggers
# --sync-vendor on demand. Pass --no-vendor to skip that probe.
#
# Override defaults via env vars:
#   JUMPER_USER, JUMPER_PASS, TOTP_SECRET,
#   VM_USER, VM_PASS, VM_HOST, PROJECT_DIR, BRANCH, SITE_URL.
#
# Prerequisites: expect, curl, git, python3 with the 'pyotp' module.
# ============================================
set -euo pipefail

# --- Style helpers ---------------------------------------------------------
GREEN=$'\033[1;32m'; RED=$'\033[1;31m'; YEL=$'\033[1;33m'; BLU=$'\033[1;36m'; NC=$'\033[0m'
log()  { printf '%s[deploy]%s %s\n' "$BLU" "$NC" "$*"; }
ok()   { printf '%s✓%s %s\n' "$GREEN" "$NC" "$*"; }
warn() { printf '%s⚠%s %s\n' "$YEL" "$NC" "$*"; }
err()  { printf '%s✗%s %s\n' "$RED" "$NC" "$*" >&2; }

usage() { sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; }

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
AUTO_VENDOR=1
QUIET=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --diag)          MODE="diag"; shift ;;
        --sync-vendor)   MODE="vendor"; shift ;;
        --no-vendor)     AUTO_VENDOR=0; shift ;;
        --quiet|-q)      QUIET=1; shift ;;
        -h|--help)       usage; exit 0 ;;
        *)               err "Unknown argument: $1"; usage; exit 1 ;;
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

DEPLOY_LOG="$(mktemp -t wlh-deploy.XXXXXX)"
trap 'rm -f "$DEPLOY_LOG"' EXIT
export JUMPER_USER JUMPER_HOST JUMPER_PASS VM_USER VM_HOST VM_PASS QUIET

# Re-generate TOTP just before each remote step (codes are 30-second windowed)
fresh_totp() {
    TOTP=$(python3 -c "import pyotp; print(pyotp.TOTP('${TOTP_SECRET}').now())")
    export TOTP
}

# --- run_remote: drive jumper -> VM and execute REMOTE_CMD -----------------
# Stdout is captured to $DEPLOY_LOG; with --quiet, banners are filtered out.
run_remote() {
    local _cmd="$1"
    fresh_totp
    export REMOTE_CMD="$_cmd"

    set +e
    if [[ "$QUIET" == "1" ]]; then
        expect "$SCRIPT_DIR/.deploy/run_remote.expect" 2>&1 \
            | tee "$DEPLOY_LOG" \
            | grep -E '^(==|__SHA__|__RC__|TIMEOUT_|EOF_|\(deploy\)|HEAD is now|Switched|Removing|Updating|Empty database|Database has|Created|Demo data|compiling|✅|⚠|✓|sudo:)' || true
    else
        expect "$SCRIPT_DIR/.deploy/run_remote.expect" 2>&1 | tee "$DEPLOY_LOG"
    fi
    local _rc=${PIPESTATUS[0]}
    set -e
    return "$_rc"
}

# --- run_scp_to_jumper: scp a local file to /tmp on the jump host ----------
run_scp_to_jumper() {
    local _src="$1"
    fresh_totp
    export SCP_SRC="$_src"

    set +e
    expect "$SCRIPT_DIR/.deploy/scp_to_jumper.expect" 2>&1 | tee -a "$DEPLOY_LOG" >/dev/null
    local _rc=${PIPESTATUS[0]}
    set -e
    return "$_rc"
}

# --- Generate the expect helpers (idempotent) ------------------------------
mkdir -p "$SCRIPT_DIR/.deploy"

cat > "$SCRIPT_DIR/.deploy/run_remote.expect" <<'EXPECT_REMOTE'
#!/usr/bin/expect -f
set timeout 1800
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
    -re {__SHA__:[A-Za-z0-9-]+} { exp_continue }
    -re {VENDOR_OK} { exp_continue }
    -re {csi6220-2-vm3[^\$#]*[\$#] ?$} {}
    timeout { send_user "\nTIMEOUT_DEPLOY\n"; exit 12 }
    eof     { send_user "\nEOF_DEPLOY\n";     exit 12 }
}

send "printf '__RC__:%s\\n' \$?\r"
expect {
    -re {__RC__:0\r?\n} {
        send_user "\n(deploy) RC=0\n"
    }
    -re {__RC__:([1-9][0-9]*)\r?\n} {
        send_user "\n(deploy) RC=$expect_out(1,string)\n"
        send "exit\r"
        expect -re {ipa-rdp[^\$#]*[\$#] ?$}
        send "exit\r"
        expect eof
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
EXPECT_REMOTE

cat > "$SCRIPT_DIR/.deploy/scp_to_jumper.expect" <<'EXPECT_SCP'
#!/usr/bin/expect -f
set timeout 1800
log_user 0

spawn scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    $env(SCP_SRC) $env(JUMPER_USER)@$env(JUMPER_HOST):/tmp/
expect {
    -nocase -re "password" { send "$env(JUMPER_PASS)\r"; exp_continue }
    -nocase -re "verification" { send "$env(TOTP)\r"; exp_continue }
    eof {}
    timeout { send_user "\nTIMEOUT_SCP_JUMPER\n"; exit 20 }
}
EXPECT_SCP

# --- Sub-task: vendor sync (used by --sync-vendor and auto check) ----------
do_vendor_sync() {
    local _layui="${SCRIPT_DIR}/static/admin/component/layui/layui.js"
    [[ -f "$_layui" ]] || { err "Local layui.js missing at $_layui"; return 1; }

    local _tar="/tmp/wlh-vendor.tar.gz"
    log "Packing admin vendor assets..."
    tar czf "$_tar" -C "${SCRIPT_DIR}/static/admin/component" \
        layui/layui.js \
        pear/module/echarts.js \
        pear/module/tinymce
    local _size; _size=$(ls -lh "$_tar" | awk '{print $5}')
    log "Vendor tarball: $_size"

    log "Uploading vendor tarball to jump host..."
    run_scp_to_jumper "$_tar" \
        || { err "SCP to jump host failed"; return 1; }

    log "Pushing tarball from jump host to VM and unpacking..."
    local _remote_cmd
    _remote_cmd="scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/wlh-vendor.tar.gz ${VM_USER}@${VM_HOST}:/tmp/ <<< '${VM_PASS}' >/dev/null 2>&1 || true; \
cd '${PROJECT_DIR}/static/admin/component' && tar xzf /tmp/wlh-vendor.tar.gz && \
test -f layui/layui.js && test -f pear/module/echarts.js && \
echo VENDOR_OK"
    # The 'scp <<< pass' trick won't work because scp reads tty for the password;
    # do the scp in a separate run by chaining: jumper scp + then unpack on VM.
    # Implementation: split into 2 jumper-only steps using run_remote variants.

    # Step A: from jumper, scp to VM (use a short bash that handles the password
    # via expect at the local level; here we instead push the tar file by
    # spawning another expect script that goes jumper -> scp to VM -> exit).
    expect "$SCRIPT_DIR/.deploy/jumper_to_vm_scp.expect" 2>&1 \
        | tee -a "$DEPLOY_LOG" >/dev/null \
        || { err "Jumper-to-VM SCP failed"; return 1; }

    # Step B: unpack on VM
    run_remote "cd '${PROJECT_DIR}/static/admin/component' && \
tar xzf /tmp/wlh-vendor.tar.gz && \
test -f layui/layui.js && test -f pear/module/echarts.js && \
echo VENDOR_OK" \
        || { err "Vendor unpack failed"; return 1; }

    rm -f "$_tar"

    local _http
    _http=$(curl -s -o /dev/null -w '%{http_code}' --max-time 20 \
        "$SITE_URL/static/admin/component/layui/layui.js")
    if [[ "$_http" == "200" ]]; then
        ok "layui.js reachable on the VM (HTTP 200)"
        return 0
    else
        err "layui.js still returning HTTP $_http after sync"
        return 1
    fi
}

# Helper expect for jumper-to-VM SCP (fresh TOTP each time).
cat > "$SCRIPT_DIR/.deploy/jumper_to_vm_scp.expect" <<'EXPECT_J2V'
#!/usr/bin/expect -f
set timeout 1800
log_user 1

spawn ssh -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    $env(JUMPER_USER)@$env(JUMPER_HOST)
expect {
    -nocase -re "password" { send "$env(JUMPER_PASS)\r"; exp_continue }
    -nocase -re "verification" { send "$env(TOTP)\r"; exp_continue }
    -re {ipa-rdp[^\$#]*[\$#] ?$} {}
    timeout { send_user "\nTIMEOUT_JUMPER\n"; exit 21 }
}

send "scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null /tmp/wlh-vendor.tar.gz $env(VM_USER)@$env(VM_HOST):/tmp/\r"
expect {
    -nocase -re "password" { send "$env(VM_PASS)\r"; exp_continue }
    -re {100%} { exp_continue }
    -re {ipa-rdp[^\$#]*[\$#] ?$} {}
    timeout { send_user "\nTIMEOUT_SCP_VM\n"; exit 22 }
}

send "exit\r"
expect eof
EXPECT_J2V

# === Mode dispatch ==========================================================

if [[ "$MODE" == "vendor" ]]; then
    fresh_totp
    do_vendor_sync && exit 0 || exit 1
fi

# --- diag mode ------------------------------------------------------------
if [[ "$MODE" == "diag" ]]; then
    DIAG_CMD="cd '${PROJECT_DIR}' 2>/dev/null && { \
echo '== gunicorn =='; sudo -n systemctl is-active gunicorn 2>&1 | head -1; \
echo '== gunicorn cwd =='; ls -l /proc/\$(pgrep -f 'gunicorn.*applications' | head -1)/cwd 2>/dev/null || echo no-pid; \
echo '== repo =='; git log -1 --oneline; git status -s | head -5; \
echo '== file timestamps =='; stat -c '%y %n' templates/public/user/history.html templates/admin/community/main.html 2>/dev/null; \
printf '__SHA__:%s\\n' \$(git rev-parse HEAD); }"
    run_remote "$DIAG_CMD" || { err "Diagnostics session failed"; exit 1; }
    DEPLOYED_SHA=$(grep -oE '__SHA__:[A-Za-z0-9-]+' "$DEPLOY_LOG" | tail -1 | cut -d: -f2 || true)
    [[ -n "$DEPLOYED_SHA" ]] && log "VM HEAD: $DEPLOYED_SHA"
    ok "Diagnostics complete"
    exit 0
fi

# === deploy mode ============================================================

# --- Local sanity ----------------------------------------------------------
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

# --- The remote command ---------------------------------------------------
DEPLOY_CMD="set -e; cd '${PROJECT_DIR}'; \
if ! git remote get-url origin >/dev/null 2>&1; then git remote add origin '${REPO_URL}'; fi; \
git fetch origin '${BRANCH}'; \
git checkout -fB '${BRANCH}' FETCH_HEAD; \
git reset --hard FETCH_HEAD; \
git clean -fd; \
bash vm_update.sh; \
printf '__SHA__:%s\\n' \$(git rev-parse HEAD)"

log "Connecting to VM through jump host..."
run_remote "$DEPLOY_CMD" || { err "Remote deployment failed"; exit 1; }

# --- Capture deployed SHA --------------------------------------------------
DEPLOYED_SHA=$(grep -oE '__SHA__:[A-Za-z0-9-]+' "$DEPLOY_LOG" | tail -1 | cut -d: -f2 || true)
if [[ -n "$DEPLOYED_SHA" ]]; then
    log "VM HEAD: $DEPLOYED_SHA"
else
    warn "Could not capture deployed SHA from session output"
fi

if [[ -n "$DEPLOYED_SHA" && -n "$LOCAL_SHA" ]]; then
    if [[ "$DEPLOYED_SHA" == "$LOCAL_SHA" ]]; then
        ok "VM HEAD matches local $BRANCH"
    else
        warn "VM HEAD ($DEPLOYED_SHA) does not match local $BRANCH ($LOCAL_SHA)"
        warn "Hint: did you 'git push origin $BRANCH' before deploying?"
    fi
fi

# --- Vendor auto-check -----------------------------------------------------
if [[ "$AUTO_VENDOR" == "1" ]]; then
    log "Probing admin vendor asset..."
    HTTP=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
        "$SITE_URL/static/admin/component/layui/layui.js" || echo "000")
    if [[ "$HTTP" == "200" ]]; then
        ok "Admin vendor assets present"
    else
        warn "layui.js returns HTTP $HTTP; running vendor sync..."
        do_vendor_sync || { err "Vendor sync failed"; exit 5; }
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

if curl -s --max-time 15 "$SITE_URL/" | tr -d '\n' | grep -q "Weilight Harbor"; then
    ok "Landing page contains brand string"
else
    warn "Landing page reachable but brand string not found (template may be cached)"
fi

# Verify the admin dashboard at least redirects to login (i.e. the route exists)
ADMIN_HTTP=$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$SITE_URL/admin/" || echo "000")
if [[ "$ADMIN_HTTP" =~ ^(200|302|308)$ ]]; then
    ok "Admin route responds (HTTP $ADMIN_HTTP)"
else
    warn "Admin route returned HTTP $ADMIN_HTTP"
fi

ok "Deployment complete"
echo "🌐 $SITE_URL"

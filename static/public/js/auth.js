// ============================================
// Weilight Harbor - Auth Module JS
// ============================================

function initPhoneCodeSender(config) {
    var phoneInput = document.querySelector(config.phoneSelector);
    var sendBtn = document.querySelector(config.buttonSelector);
    var messageEl = document.querySelector(config.messageSelector);
    var defaultText = sendBtn ? sendBtn.textContent.trim() : 'Send Code';
    var timer = null;

    function showMessage(text, type) {
        if (!messageEl) return;
        messageEl.textContent = text;
        messageEl.className = type === 'error' ? 'small text-danger mt-1' : 'small text-success mt-1';
    }

    function startCountdown(seconds) {
        var remaining = seconds;
        clearInterval(timer);
        if (!sendBtn) return;
        sendBtn.disabled = true;
        sendBtn.textContent = remaining + 's';
        timer = setInterval(function() {
            remaining -= 1;
            if (remaining <= 0) {
                clearInterval(timer);
                sendBtn.disabled = false;
                sendBtn.textContent = defaultText;
                return;
            }
            sendBtn.textContent = remaining + 's';
        }, 1000);
    }

    if (!phoneInput || !sendBtn) return;

    sendBtn.addEventListener('click', function() {
        var phone = phoneInput.value.trim();
        if (!phone) {
            showMessage('Please enter your phone number first.', 'error');
            phoneInput.focus();
            return;
        }

        sendBtn.disabled = true;
        sendBtn.textContent = 'Sending...';

        fetch('/auth/send-phone-code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: phone })
        })
        .then(function(resp) {
            return resp.json().then(function(data) {
                return { ok: resp.ok, data: data };
            });
        })
        .then(function(result) {
            if (!result.ok || !result.data.success) {
                showMessage(result.data.error || 'Unable to send verification code.', 'error');
                sendBtn.disabled = false;
                sendBtn.textContent = defaultText;
                return;
            }

            if (result.data.dev_code) {
                showMessage('Local verification code: ' + result.data.dev_code, 'success');
            } else {
                showMessage(result.data.message || 'Verification code sent.', 'success');
            }
            startCountdown(60);
        })
        .catch(function() {
            showMessage('Network error. Please try again.', 'error');
            sendBtn.disabled = false;
            sendBtn.textContent = defaultText;
        });
    });
}

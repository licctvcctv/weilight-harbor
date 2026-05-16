// ============================================
// Weilight Harbor - Crowdfunding Module JS
// ============================================

function initCrowdfundingDetail(config) {
    var selectedAmount = 100;
    var isCustom = false;
    var selectedPaymentMethod = 'wechat';
    var paymentStatusTimer = null;
    function t(key, fallback) {
        var i18n = window.WL_CROWDFUNDING_I18N || {};
        return i18n[key] || fallback;
    }

    function getConfirmAmountSpan() {
        return document.getElementById('confirmAmount');
    }

    function updateConfirmAmountLabel() {
        var span = getConfirmAmountSpan();
        if (!span) return;
        if (selectedAmount && selectedAmount > 0) {
            span.textContent = '\u00a5' + selectedAmount.toFixed(2);
        } else {
            span.textContent = '\u00a5--';
        }
    }

    function showStep(stepNumber) {
        ['donateStep1', 'donateStep2', 'donateStep3', 'donateStep4'].forEach(function(id) {
            var el = document.getElementById(id);
            if (el) el.style.display = id === 'donateStep' + stepNumber ? 'block' : 'none';
        });
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    function readSelectedAmount() {
        var customInput = document.getElementById('customAmountInput');
        if (isCustom && customInput) {
            selectedAmount = parseFloat(customInput.value);
        }
        return selectedAmount;
    }

    function getPaymentMethodLabel(method) {
        var labels = {
            wechat: t('wechatPay', 'WeChat Pay'),
            alipay: t('alipay', 'Alipay')
        };
        return labels[method] || labels.wechat;
    }

    function setButtonLoading(button, loadingText) {
        if (!button) return;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>' + loadingText;
    }

    function restoreFinishButton() {
        var finishBtn = document.getElementById('finishPaymentBtn');
        if (!finishBtn) return;
        finishBtn.disabled = false;
        finishBtn.textContent = t('iHavePaid', 'I Have Paid');
    }

    function beginPaymentStatusCycle() {
        var statusEl = document.getElementById('paymentStatusText');
        if (!statusEl) return;

        clearInterval(paymentStatusTimer);
        var messages = [
            t('waitingConfirmation', 'Waiting for payment confirmation'),
            t('keepWindowOpen', 'Keep this window open after scanning'),
            t('clickPaid', 'Click "I Have Paid" once the transfer is complete')
        ];
        var index = 0;
        statusEl.textContent = messages[index];
        paymentStatusTimer = setInterval(function() {
            index = (index + 1) % messages.length;
            statusEl.textContent = messages[index];
        }, 2500);
    }

    function updatePaymentStep() {
        var instruction = document.getElementById('paymentInstruction');
        var statusEl = document.getElementById('paymentStatusText');
        if (instruction) {
            instruction.textContent = t('payVia', 'Pay {amount} via {method}, then confirm after payment.')
                .replace('{amount}', '\u00a5' + selectedAmount.toFixed(2))
                .replace('{method}', getPaymentMethodLabel(selectedPaymentMethod));
        }
        if (statusEl) {
            statusEl.textContent = config.paymentQrUrl ?
                t('waitingConfirmation', 'Waiting for payment confirmation') :
                t('noQr', 'No QR code was uploaded. Confirm only after using the organizer payment information.');
        }
        beginPaymentStatusCycle();
    }

    // Animate progress bar on load
    document.querySelectorAll('.wl-progress-bar[data-progress]').forEach(function(bar) {
        var target = parseFloat(bar.getAttribute('data-progress'));
        setTimeout(function() {
            bar.style.width = target + '%';
        }, 200);
    });

    // Amount preset buttons
    var presetBtns = document.querySelectorAll('.amount-preset-btn');
    var customWrapper = document.getElementById('customAmountWrapper');
    var customInput = document.getElementById('customAmountInput');

    presetBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            presetBtns.forEach(function(b) { b.classList.remove('selected'); });
            btn.classList.add('selected');

            var amt = btn.getAttribute('data-amount');
            if (amt === 'custom') {
                isCustom = true;
                if (customWrapper) customWrapper.style.display = 'block';
                if (customInput) customInput.focus();
                var val = customInput ? parseFloat(customInput.value) : 0;
                selectedAmount = val > 0 ? val : 0;
            } else {
                isCustom = false;
                if (customWrapper) customWrapper.style.display = 'none';
                selectedAmount = parseFloat(amt);
            }
            updateConfirmAmountLabel();
        });
    });

    // Custom amount input
    if (customInput) {
        customInput.addEventListener('input', function() {
            var val = parseFloat(this.value);
            selectedAmount = val > 0 ? val : 0;
            updateConfirmAmountLabel();
        });
    }

    // Payment method selection
    document.querySelectorAll('.payment-method-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.payment-method-btn').forEach(function(b) { b.classList.remove('active'); });
            btn.classList.add('active');
            selectedPaymentMethod = btn.getAttribute('data-method') || 'wechat';
        });
    });

    // Step 1 -> Step 2
    var confirmBtn = document.getElementById('confirmDonateBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (!config.isAuthenticated) {
                window.location.href = config.loginUrl;
                return;
            }

            readSelectedAmount();
            if (!selectedAmount || selectedAmount < 1) {
                showToast('Please enter a valid amount (minimum \u00a51).', 'error');
                return;
            }

            var summary = document.getElementById('paymentAmountSummary');
            if (summary) summary.textContent = '\u00a5' + selectedAmount.toFixed(2);
            showStep(2);
        });
    }

    var backToAmountBtn = document.getElementById('backToAmountBtn');
    if (backToAmountBtn) {
        backToAmountBtn.addEventListener('click', function() {
            showStep(1);
        });
    }

    var startPaymentBtn = document.getElementById('startPaymentBtn');
    if (startPaymentBtn) {
        startPaymentBtn.addEventListener('click', function() {
            updatePaymentStep();
            showStep(3);
        });
    }

    var backToConfirmBtn = document.getElementById('backToConfirmBtn');
    if (backToConfirmBtn) {
        backToConfirmBtn.addEventListener('click', function() {
            clearInterval(paymentStatusTimer);
            showStep(2);
        });
    }

    var finishPaymentBtn = document.getElementById('finishPaymentBtn');
    if (finishPaymentBtn) {
        finishPaymentBtn.addEventListener('click', function() {
            readSelectedAmount();
            if (!selectedAmount || selectedAmount < 1) {
                showToast('Please enter a valid amount (minimum \u00a51).', 'error');
                showStep(1);
                return;
            }
            recordDonation();
        });
    }

    function recordDonation() {
        var finishBtn = document.getElementById('finishPaymentBtn');
        var messageEl = document.getElementById('donateMessage');
        var anonymousEl = document.getElementById('donateAnonymous');
        var message = messageEl ? messageEl.value.trim() : '';
        var isAnonymous = anonymousEl ? anonymousEl.checked : false;

        clearInterval(paymentStatusTimer);
        setButtonLoading(finishBtn, 'Recording...');

        fetch(config.donateUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                amount: selectedAmount,
                message: message,
                is_anonymous: isAnonymous,
                payment_method: selectedPaymentMethod,
                payment_confirmed: true
            })
        })
        .then(function(resp) { return resp.json(); })
        .then(function(data) {
            if (data.success) {
                updateCampaignProgress(data);
                showThankYou(data);
                return;
            }
            showToast(data.error || 'Donation failed. Please try again.', 'error');
            restoreFinishButton();
            beginPaymentStatusCycle();
        })
        .catch(function() {
            showToast('Network error. Please try again.', 'error');
            restoreFinishButton();
            beginPaymentStatusCycle();
        });
    }

    function updateCampaignProgress(data) {
        var amountEl = document.getElementById('amountRaised');
        if (amountEl) amountEl.textContent = '\u00a5' + data.current_amount.toFixed(2);

        var pctEl = document.getElementById('progressPct');
        if (pctEl) pctEl.textContent = data.progress + '%';

        var donorEl = document.getElementById('donorCount');
        if (donorEl) donorEl.textContent = data.donor_count;

        var donorTab = document.querySelector('.detail-tab[data-tab="donors"]');
        if (donorTab) {
            var donorTabLabel = donorTab.textContent.replace(/\s*\([^)]*\)\s*$/, '').trim();
            donorTab.textContent = donorTabLabel + ' (' + data.donor_count + ')';
        }

        var donorHeading = document.querySelector('#tab-donors h3');
        if (donorHeading) {
            var donorHeadingLabel = donorHeading.textContent.replace(/\s*\([^)]*\)\s*$/, '').trim();
            donorHeading.textContent = donorHeadingLabel + ' (' + data.donor_count + ')';
        }

        document.querySelectorAll('.wl-progress-bar').forEach(function(bar) {
            bar.style.width = data.progress + '%';
            bar.setAttribute('data-progress', data.progress);
        });

        if (data.is_fully_funded) {
            var donateBtn = document.getElementById('openDonateBtn');
            if (donateBtn) {
                donateBtn.className = 'btn-donate-lg disabled-donate';
                donateBtn.disabled = true;
                donateBtn.innerHTML = '<i data-lucide="check-circle" style="width:20px;height:20px;margin-right:6px"></i> ' + t('fullyFunded', 'Fully Funded');
                donateBtn.removeAttribute('data-bs-toggle');
                donateBtn.removeAttribute('data-bs-target');
            }
        }
    }

    function showThankYou(data) {
        var summary = document.getElementById('donationSummary');
        showStep(4);

        if (summary) {
            summary.innerHTML =
                '<div style="font-size:0.875rem;color:var(--color-text-secondary)">' +
                t('youDonated', 'You donated') + ' <strong style="color:var(--color-primary);font-size:1.25rem">\u00a5' + selectedAmount.toFixed(2) + '</strong>' +
                '</div>' +
                '<div style="font-size:0.8125rem;color:var(--color-text-disabled);margin-top:0.25rem">' +
                t('campaignFunded', 'Campaign is now {progress} percent funded with {count} donors')
                    .replace('{progress}', data.progress)
                    .replace('{count}', data.donor_count) +
                '</div>';
        }

        createConfetti(document.getElementById('thankYouScreen'));
        if (typeof lucide !== 'undefined') lucide.createIcons();
    }

    function createConfetti(container) {
        if (!container) return;
        var colors = ['#E8913A', '#F2B872', '#5B9A6B', '#D4A04A', '#6B8FAD', '#C75B5B'];
        for (var i = 0; i < 30; i++) {
            var piece = document.createElement('div');
            piece.className = 'confetti-piece';
            piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
            piece.style.left = Math.random() * 100 + '%';
            piece.style.top = Math.random() * 30 + '%';
            piece.style.animationDelay = (Math.random() * 0.5) + 's';
            piece.style.animationDuration = (1.5 + Math.random()) + 's';
            var size = 6 + Math.random() * 6;
            piece.style.width = size + 'px';
            piece.style.height = size + 'px';
            if (Math.random() > 0.5) {
                piece.style.borderRadius = '0';
            }
            container.appendChild(piece);
        }
    }

    // Reset modal state when closed
    var modal = document.getElementById('donateModal');
    if (modal) {
        modal.addEventListener('hidden.bs.modal', function() {
            clearInterval(paymentStatusTimer);
            showStep(1);

            var finishBtn = document.getElementById('finishPaymentBtn');
            if (finishBtn) {
                finishBtn.disabled = false;
                finishBtn.textContent = t('iHavePaid', 'I Have Paid');
            }

            var confirm = document.getElementById('confirmDonateBtn');
            if (confirm) {
                confirm.disabled = false;
                confirm.innerHTML = t('confirmDonation', 'Confirm Donation') + ' <span id="confirmAmount">\u00a5100</span>';
            }

            selectedAmount = 100;
            isCustom = false;
            selectedPaymentMethod = 'wechat';

            var message = document.getElementById('donateMessage');
            if (message) message.value = '';
            var anonymous = document.getElementById('donateAnonymous');
            if (anonymous) anonymous.checked = false;
            if (customWrapper) customWrapper.style.display = 'none';
            if (customInput) customInput.value = '';

            presetBtns.forEach(function(b) { b.classList.remove('selected'); });
            var defaultBtn = document.querySelector('.amount-preset-btn[data-amount="100"]');
            if (defaultBtn) defaultBtn.classList.add('selected');

            document.querySelectorAll('.payment-method-btn').forEach(function(b) { b.classList.remove('active'); });
            var defaultMethod = document.querySelector('.payment-method-btn[data-method="wechat"]');
            if (defaultMethod) defaultMethod.classList.add('active');

            updateConfirmAmountLabel();
            document.querySelectorAll('.confetti-piece').forEach(function(p) { p.remove(); });
        });
    }

    // Copy link
    window.copyLink = function() {
        var url = window.location.href;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(url).then(function() {
                showToast('Link copied to clipboard!', 'success');
            });
        } else {
            var input = document.createElement('input');
            input.value = url;
            document.body.appendChild(input);
            input.select();
            document.execCommand('copy');
            document.body.removeChild(input);
            showToast('Link copied to clipboard!', 'success');
        }
    };
}

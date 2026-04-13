// ============================================
// Weilight Harbor - Crowdfunding Module JS
// ============================================

function initCrowdfundingDetail(config) {
    var selectedAmount = 100;
    var isCustom = false;

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
    var confirmAmountSpan = document.getElementById('confirmAmount');

    presetBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            presetBtns.forEach(function(b) { b.classList.remove('selected'); });
            btn.classList.add('selected');

            var amt = btn.getAttribute('data-amount');
            if (amt === 'custom') {
                isCustom = true;
                customWrapper.style.display = 'block';
                customInput.focus();
                var val = parseFloat(customInput.value);
                if (val > 0) {
                    selectedAmount = val;
                    confirmAmountSpan.textContent = '\u00a5' + val.toFixed(2);
                } else {
                    confirmAmountSpan.textContent = '\u00a5--';
                }
            } else {
                isCustom = false;
                customWrapper.style.display = 'none';
                selectedAmount = parseFloat(amt);
                confirmAmountSpan.textContent = '\u00a5' + selectedAmount.toFixed(2);
            }
        });
    });

    // Custom amount input
    if (customInput) {
        customInput.addEventListener('input', function() {
            var val = parseFloat(this.value);
            if (val > 0) {
                selectedAmount = val;
                confirmAmountSpan.textContent = '\u00a5' + val.toFixed(2);
            } else {
                confirmAmountSpan.textContent = '\u00a5--';
            }
        });
    }

    // Confirm donation
    var confirmBtn = document.getElementById('confirmDonateBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (!config.isAuthenticated) {
                window.location.href = config.loginUrl;
                return;
            }

            if (isCustom) {
                selectedAmount = parseFloat(customInput.value);
            }

            if (!selectedAmount || selectedAmount < 1) {
                showToast('Please enter a valid amount (minimum \u00a51).', 'error');
                return;
            }

            var message = document.getElementById('donateMessage').value.trim();
            var isAnonymous = document.getElementById('donateAnonymous').checked;

            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

            fetch(config.donateUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: selectedAmount,
                    message: message,
                    is_anonymous: isAnonymous
                })
            })
            .then(function(resp) { return resp.json(); })
            .then(function(data) {
                if (data.success) {
                    // Update page values
                    var amountEl = document.getElementById('amountRaised');
                    if (amountEl) amountEl.textContent = '\u00a5' + data.current_amount.toFixed(2);

                    var pctEl = document.getElementById('progressPct');
                    if (pctEl) pctEl.textContent = data.progress + '%';

                    var donorEl = document.getElementById('donorCount');
                    if (donorEl) donorEl.textContent = data.donor_count;

                    // Update progress bar
                    document.querySelectorAll('.wl-progress-bar').forEach(function(bar) {
                        bar.style.width = data.progress + '%';
                        bar.setAttribute('data-progress', data.progress);
                    });

                    // Show thank you
                    showThankYou(data);

                    // If fully funded, update button
                    if (data.is_fully_funded) {
                        var donateBtn = document.getElementById('openDonateBtn');
                        if (donateBtn) {
                            donateBtn.className = 'btn-donate-lg disabled-donate';
                            donateBtn.disabled = true;
                            donateBtn.innerHTML = '<i data-lucide="check-circle" style="width:20px;height:20px;margin-right:6px"></i> Fully Funded';
                            donateBtn.removeAttribute('data-bs-toggle');
                            donateBtn.removeAttribute('data-bs-target');
                            if (typeof lucide !== 'undefined') lucide.createIcons();
                        }
                    }
                } else {
                    showToast(data.error || 'Donation failed. Please try again.', 'error');
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = 'Confirm Donation <span id="confirmAmount">\u00a5' + selectedAmount.toFixed(2) + '</span>';
                }
            })
            .catch(function(err) {
                showToast('Network error. Please try again.', 'error');
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = 'Confirm Donation <span id="confirmAmount">\u00a5' + selectedAmount.toFixed(2) + '</span>';
            });
        });
    }

    function showThankYou(data) {
        var step1 = document.getElementById('donateStep1');
        var step2 = document.getElementById('donateStep2');
        var summary = document.getElementById('donationSummary');

        step1.style.display = 'none';
        step2.style.display = 'block';

        summary.innerHTML =
            '<div style="font-size:0.875rem;color:var(--color-text-secondary)">' +
            'You donated <strong style="color:var(--color-primary);font-size:1.25rem">\u00a5' + selectedAmount.toFixed(2) + '</strong>' +
            '</div>' +
            '<div style="font-size:0.8125rem;color:var(--color-text-disabled);margin-top:0.25rem">' +
            'Campaign is now ' + data.progress + '% funded with ' + data.donor_count + ' donors' +
            '</div>';

        // Trigger confetti
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
            var step1 = document.getElementById('donateStep1');
            var step2 = document.getElementById('donateStep2');
            step1.style.display = 'block';
            step2.style.display = 'none';

            // Reset form
            var confirmBtn = document.getElementById('confirmDonateBtn');
            confirmBtn.disabled = false;
            confirmBtn.innerHTML = 'Confirm Donation <span id="confirmAmount">\u00a5100</span>';

            selectedAmount = 100;
            isCustom = false;
            document.getElementById('donateMessage').value = '';
            document.getElementById('donateAnonymous').checked = false;
            document.getElementById('customAmountWrapper').style.display = 'none';
            document.getElementById('customAmountInput').value = '';

            presetBtns.forEach(function(b) { b.classList.remove('selected'); });
            var defaultBtn = document.querySelector('.amount-preset-btn[data-amount="100"]');
            if (defaultBtn) defaultBtn.classList.add('selected');

            // Remove confetti
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

/**
 * Weilight Harbor - Community Module JS
 * Handles: likes, night confessions, image preview, sensitive word checks
 */

(function() {
    'use strict';

    // ========================================
    // AJAX Like / Unlike (post feed cards)
    // ========================================
    document.querySelectorAll('.like-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var postId = this.dataset.postId;
            var button = this;

            fetch('/community/post/' + postId + '/like', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(function(r) {
                if (r.status === 401 || r.redirected) {
                    window.location.href = '/auth/login';
                    return null;
                }
                return r.json();
            })
            .then(function(data) {
                if (!data) return;
                var countEl = button.querySelector('.like-count');
                if (countEl) countEl.textContent = data.count;

                if (data.liked) {
                    button.classList.add('active');
                } else {
                    button.classList.remove('active');
                }

                // Burst animation
                button.classList.add('empathy-active');
                setTimeout(function() {
                    button.classList.remove('empathy-active');
                }, 300);
            })
            .catch(function() {
                window.location.href = '/auth/login';
            });
        });
    });


    // ========================================
    // Night Confessions
    // ========================================
    var confessionInput = document.getElementById('confessionInput');
    var confessionSubmitBtn = document.getElementById('confessionSubmitBtn');
    var confessionList = document.getElementById('confessionList');

    // Generate or retrieve session ID for anonymous confessions
    function getSessionId() {
        var sid = localStorage.getItem('wl_confession_sid');
        if (!sid) {
            sid = 'sess_' + Math.random().toString(36).substr(2, 12) + Date.now().toString(36);
            localStorage.setItem('wl_confession_sid', sid);
        }
        return sid;
    }

    if (confessionSubmitBtn) {
        confessionSubmitBtn.addEventListener('click', function() {
            var content = confessionInput.value.trim();
            if (!content) return;

            confessionSubmitBtn.disabled = true;
            confessionSubmitBtn.textContent = '...';

            fetch('/community/confessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    content: content,
                    session_id: getSessionId()
                })
            })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                confessionSubmitBtn.disabled = false;
                confessionSubmitBtn.innerHTML = '<i data-lucide="send" style="width:14px;height:14px;vertical-align:-2px"></i> Send into the night';

                if (data.crisis) {
                    // Show the crisis modal
                    var modal = new bootstrap.Modal(document.getElementById('sensitiveModal'));
                    modal.show();
                    return;
                }

                if (data.error) {
                    return;
                }

                // Prepend the new confession card
                var card = document.createElement('div');
                card.className = 'night-card';
                card.dataset.confessionId = data.id;
                card.innerHTML =
                    '<div class="confession-nickname">' + escapeHtml(data.nickname) + '</div>' +
                    '<div class="confession-text-preview">' + escapeHtml(data.content) + '</div>' +
                    '<div class="confession-meta">' +
                        '<span>' + data.create_at + '</span>' +
                        '<button class="confession-hug-btn" onclick="hugConfession(' + data.id + ', this)">' +
                            '<i data-lucide="hand-heart" style="width:12px;height:12px"></i> ' +
                            '<span class="hug-count">0</span>' +
                        '</button>' +
                    '</div>';

                // Remove empty state if present
                var emptyState = confessionList.querySelector('.text-center');
                if (emptyState && confessionList.children.length === 1) {
                    confessionList.removeChild(emptyState);
                }

                confessionList.insertBefore(card, confessionList.firstChild);
                confessionInput.value = '';

                // Re-init lucide icons for the new card
                if (window.lucide) lucide.createIcons();
            })
            .catch(function() {
                confessionSubmitBtn.disabled = false;
                confessionSubmitBtn.innerHTML = '<i data-lucide="send" style="width:14px;height:14px;vertical-align:-2px"></i> Send into the night';
            });
        });
    }

    // Sensitive word check for confession input (debounced)
    var confessionSensitiveTimer = null;
    if (confessionInput) {
        confessionInput.addEventListener('input', function() {
            clearTimeout(confessionSensitiveTimer);
            confessionSensitiveTimer = setTimeout(function() {
                var text = confessionInput.value.trim();
                if (text.length < 5) return;

                fetch('/community/check-sensitive', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: text })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.has_crisis) {
                        var modal = new bootstrap.Modal(document.getElementById('sensitiveModal'));
                        modal.show();
                    }
                })
                .catch(function() {});
            }, 800);
        });
    }


    // ========================================
    // Utilities
    // ========================================
    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

})();


// ========================================
// Night Confessions Time Gate
// ========================================
window.initNightConfessionsGate = function() {
    var nightTeaser = document.getElementById('nightTeaser');
    var nightActive = document.getElementById('nightActive');
    var nightCountdown = document.getElementById('nightCountdown');
    var nightSoulsCount = document.getElementById('nightSoulsCount');
    var mobileMoonFab = document.getElementById('mobileMoonFab');
    var mobileNightSheet = document.getElementById('mobileNightSheet');
    var mobileNightOverlay = document.getElementById('mobileNightOverlay');
    var mobileNightContent = document.getElementById('mobileNightContent');
    var mobileNightTeaser = document.getElementById('mobileNightTeaser');
    var mobileNightActive = document.getElementById('mobileNightActive');
    var mobileNightCountdown = document.getElementById('mobileNightCountdown');
    var mobileNightSoulsCount = document.getElementById('mobileNightSoulsCount');

    if (!nightTeaser && !nightActive) return;

    function isNightTime() {
        var hour = new Date().getHours();
        return hour >= 21 || hour < 6;
    }

    function getSecondsUntil21() {
        var now = new Date();
        var target = new Date(now);
        target.setHours(21, 0, 0, 0);
        if (now >= target) {
            target.setDate(target.getDate() + 1);
        }
        return Math.max(0, Math.floor((target - now) / 1000));
    }

    function formatCountdown(totalSeconds) {
        var h = Math.floor(totalSeconds / 3600);
        var m = Math.floor((totalSeconds % 3600) / 60);
        var s = totalSeconds % 60;
        return (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
    }

    function updateGateState() {
        var active = isNightTime();
        if (nightTeaser) nightTeaser.style.display = active ? 'none' : 'block';
        if (nightActive) nightActive.style.display = active ? 'block' : 'none';
        if (mobileNightTeaser) mobileNightTeaser.style.display = active ? 'none' : 'block';
        if (mobileNightActive) mobileNightActive.style.display = active ? 'block' : 'none';

        // Show mobile moon FAB on small screens
        if (mobileMoonFab) {
            if (window.innerWidth < 992) {
                mobileMoonFab.style.display = 'flex';
            } else {
                mobileMoonFab.style.display = 'none';
            }
        }
    }

    function updateCountdown() {
        if (isNightTime()) return;
        var secs = getSecondsUntil21();
        var formatted = formatCountdown(secs);
        if (nightCountdown) nightCountdown.textContent = formatted;
        if (mobileNightCountdown) mobileNightCountdown.textContent = formatted;
    }

    // Fetch souls count (confessions in last 24h)
    function fetchSoulsCount() {
        fetch('/community/confessions?page=1')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var count = data.confessions ? data.confessions.length : 0;
                var text = count + ' soul' + (count !== 1 ? 's' : '') + ' in the night';
                if (nightSoulsCount) nightSoulsCount.textContent = text;
                if (mobileNightSoulsCount) mobileNightSoulsCount.textContent = text;
            })
            .catch(function() {});
    }

    // Mobile bottom sheet logic
    if (mobileMoonFab && mobileNightSheet) {
        mobileMoonFab.addEventListener('click', function() {
            mobileNightSheet.style.display = 'block';
            // Trigger animation on next frame
            requestAnimationFrame(function() {
                mobileNightContent.style.transform = 'translateY(0)';
            });
            if (window.lucide) lucide.createIcons();
        });

        mobileNightOverlay.addEventListener('click', function() {
            mobileNightContent.style.transform = 'translateY(100%)';
            setTimeout(function() {
                mobileNightSheet.style.display = 'none';
            }, 300);
        });

        // Mobile confession submit (delegates to same API)
        var mobileSubmitBtn = document.getElementById('mobileConfessionSubmitBtn');
        var mobileInput = document.getElementById('mobileConfessionInput');
        if (mobileSubmitBtn && mobileInput) {
            mobileSubmitBtn.addEventListener('click', function() {
                var content = mobileInput.value.trim();
                if (!content) return;
                mobileSubmitBtn.disabled = true;
                mobileSubmitBtn.textContent = '...';
                var sid = localStorage.getItem('wl_confession_sid') || ('sess_' + Math.random().toString(36).substr(2, 12) + Date.now().toString(36));
                localStorage.setItem('wl_confession_sid', sid);
                fetch('/community/confessions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: content, session_id: sid })
                })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    mobileSubmitBtn.disabled = false;
                    mobileSubmitBtn.innerHTML = '<i data-lucide="send" style="width:14px;height:14px;vertical-align:-2px"></i> Send into the night';
                    if (data.crisis || data.error) return;
                    var mobileList = document.getElementById('mobileConfessionList');
                    var card = document.createElement('div');
                    card.className = 'night-card';
                    card.innerHTML =
                        '<div class="confession-nickname">' + data.nickname + '</div>' +
                        '<div class="confession-text-preview">' + data.content + '</div>' +
                        '<div class="confession-meta"><span>' + data.create_at + '</span>' +
                        '<button class="confession-hug-btn" onclick="hugConfession(' + data.id + ', this)">' +
                        '<i data-lucide="hand-heart" style="width:12px;height:12px"></i> <span class="hug-count">0</span></button></div>';
                    var empty = mobileList.querySelector('.text-center');
                    if (empty && mobileList.children.length === 1) mobileList.removeChild(empty);
                    mobileList.insertBefore(card, mobileList.firstChild);
                    mobileInput.value = '';
                    if (window.lucide) lucide.createIcons();
                })
                .catch(function() {
                    mobileSubmitBtn.disabled = false;
                    mobileSubmitBtn.innerHTML = '<i data-lucide="send" style="width:14px;height:14px;vertical-align:-2px"></i> Send into the night';
                });
            });
        }
    }

    // Initialize
    updateGateState();
    updateCountdown();
    fetchSoulsCount();

    // Update countdown every second
    setInterval(function() {
        updateGateState();
        updateCountdown();
    }, 1000);

    // Listen for resize to toggle mobile fab
    window.addEventListener('resize', updateGateState);
};


// ========================================
// Hug Confession (global, called from onclick)
// ========================================
function hugConfession(confessionId, btn) {
    fetch('/community/confessions/' + confessionId + '/hug', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        var countEl = btn.querySelector('.hug-count');
        if (countEl) countEl.textContent = data.hug_count;

        // Quick pulse animation
        btn.style.transform = 'scale(1.2)';
        setTimeout(function() {
            btn.style.transform = 'scale(1)';
        }, 200);
    })
    .catch(function() {});
}

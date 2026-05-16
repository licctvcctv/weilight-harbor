// ============================================
// Weilight Harbor - Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap fallback for restricted/offline browser environments.
    ensureBootstrapFallback();

    // Language Toggle
    initLangToggle();

    // Search Toggle
    initSearchToggle();

    // User dropdown fallback
    initDropdownFallback();

    // Modal fallback
    initModalFallback();

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(el) {
        if (window.bootstrap && window.bootstrap.Tooltip) {
            new bootstrap.Tooltip(el);
        }
    });

    // On page load, check localStorage for saved language and sync if needed
    var savedLang = localStorage.getItem('wl_locale');
    if (savedLang) {
        var toggle = document.getElementById('langToggle');
        if (toggle) {
            var activeOption = toggle.querySelector('.lang-option.active');
            var currentLang = activeOption ? activeOption.getAttribute('data-lang') : null;
            if (currentLang && currentLang !== savedLang) {
                // Server locale differs from saved preference; sync server
                showLangOverlay();
                fetch('/set-locale', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ locale: savedLang })
                }).then(function() {
                    window.location.reload();
                });
            }
        }
    }
});

// --- Bootstrap fallback ---
function ensureBootstrapFallback() {
    if (window.bootstrap && window.bootstrap.Modal && window.bootstrap.Tooltip) return;

    window.bootstrap = window.bootstrap || {};
    window.bootstrap.Tooltip = window.bootstrap.Tooltip || function() {};

    if (!window.bootstrap.Modal) {
        window.bootstrap.Modal = function(el) {
            this.el = typeof el === 'string' ? document.querySelector(el) : el;
            if (this.el) this.el.__wlModal = this;
        };

        window.bootstrap.Modal.prototype.show = function() {
            if (!this.el) return;
            this.el.style.display = 'block';
            this.el.removeAttribute('aria-hidden');
            this.el.classList.add('show');
            document.body.classList.add('modal-open');
            if (!document.querySelector('.modal-backdrop')) {
                var backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
        };

        window.bootstrap.Modal.prototype.hide = function() {
            if (!this.el) return;
            this.el.classList.remove('show');
            this.el.style.display = 'none';
            this.el.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('modal-open');
            document.querySelectorAll('.modal-backdrop').forEach(function(backdrop) {
                backdrop.remove();
            });
        };

        window.bootstrap.Modal.getInstance = function(el) {
            return el && el.__wlModal ? el.__wlModal : new window.bootstrap.Modal(el);
        };
    }
}

// --- Dropdown fallback ---
function initDropdownFallback() {
    document.querySelectorAll('[data-bs-toggle="dropdown"]').forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            var menu = toggle.parentElement ? toggle.parentElement.querySelector('.dropdown-menu') : null;
            if (!menu) return;

            document.querySelectorAll('.dropdown-menu.show').forEach(function(openMenu) {
                if (openMenu !== menu) openMenu.classList.remove('show');
            });
            menu.classList.toggle('show');
        });
    });

    document.addEventListener('click', function(e) {
        if (e.target.closest && e.target.closest('.dropdown')) return;
        document.querySelectorAll('.dropdown-menu.show').forEach(function(menu) {
            menu.classList.remove('show');
        });
    });
}

// --- Modal fallback ---
function initModalFallback() {
    document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target]').forEach(function(trigger) {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            var targetSelector = trigger.getAttribute('data-bs-target');
            var target = targetSelector ? document.querySelector(targetSelector) : null;
            if (!target) return;
            new window.bootstrap.Modal(target).show();
        });
    });

    document.querySelectorAll('[data-bs-dismiss="modal"]').forEach(function(closeBtn) {
        closeBtn.addEventListener('click', function() {
            var modal = closeBtn.closest('.modal');
            if (modal) window.bootstrap.Modal.getInstance(modal).hide();
        });
    });
}

// --- Language Toggle ---
function initLangToggle() {
    const toggle = document.getElementById('langToggle');
    if (!toggle) return;

    toggle.querySelectorAll('.lang-option').forEach(function(option) {
        option.addEventListener('click', function() {
            const lang = this.getAttribute('data-lang');
            // Save to localStorage before POSTing
            localStorage.setItem('wl_locale', lang);
            // Show loading overlay
            showLangOverlay();
            fetch('/set-locale', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ locale: lang })
            }).then(function() {
                window.location.reload();
            });
        });
    });
}

// --- Language switch loading overlay ---
function showLangOverlay() {
    var overlay = document.createElement('div');
    overlay.id = 'wl-lang-overlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,255,255,0.6);z-index:99999;display:flex;align-items:center;justify-content:center;opacity:0;transition:opacity 200ms ease;';
    overlay.innerHTML = '<div style="width:32px;height:32px;border:3px solid var(--color-primary,#4a90d9);border-top-color:transparent;border-radius:50%;animation:wl-spin 0.6s linear infinite;"></div>';
    // Add spinner keyframes if not already present
    if (!document.getElementById('wl-spin-style')) {
        var style = document.createElement('style');
        style.id = 'wl-spin-style';
        style.textContent = '@keyframes wl-spin { to { transform: rotate(360deg); } }';
        document.head.appendChild(style);
    }
    document.body.appendChild(overlay);
    // Trigger reflow then fade in
    requestAnimationFrame(function() {
        overlay.style.opacity = '1';
    });
}

// --- Search Toggle ---
function initSearchToggle() {
    var btn = document.getElementById('navSearchToggle');
    var box = document.getElementById('navSearchBox');
    if (!btn || !box) return;

    btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        var isVisible = box.style.display !== 'none';
        box.style.display = isVisible ? 'none' : 'block';
        if (!isVisible) {
            var input = box.querySelector('input');
            if (input) input.focus();
        }
    });

    // Close search box when clicking outside
    document.addEventListener('click', function(e) {
        if (!box.contains(e.target) && e.target !== btn && !btn.contains(e.target)) {
            box.style.display = 'none';
        }
    });
}

// --- AJAX Helper ---
function wlFetch(url, options) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' }
    };
    return fetch(url, Object.assign(defaults, options))
        .then(function(resp) { return resp.json(); });
}

// --- Toast Notification ---
function showToast(message, type) {
    type = type || 'info';
    const toast = document.createElement('div');
    toast.className = 'alert alert-' + (type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info');
    toast.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;min-width:280px;border-radius:var(--radius-md);border:none;box-shadow:var(--shadow-lg);animation:slideInRight 200ms ease-out;';
    toast.innerHTML = message + '<button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>';
    document.body.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 4000);
}

// --- Sensitive Word Check ---
function checkSensitive(text, callback) {
    wlFetch('/community/check-sensitive', {
        method: 'POST',
        body: JSON.stringify({ text: text })
    }).then(function(data) {
        if (callback) callback(data);
    });
}

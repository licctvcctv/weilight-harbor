// ============================================
// Weilight Harbor - Main JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Language Toggle
    initLangToggle();

    // Search Toggle
    initSearchToggle();

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(el) {
        new bootstrap.Tooltip(el);
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

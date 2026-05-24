// Respite Station Map
let map, markers = [], allRequests = [];
let markerClusterGroup = null;
let hasFitInitialRequests = false;

// Radius -> Zoom level mapping
var radiusZoomMap = { 3: 15, 5: 14, 10: 13, 20: 11 };

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    loadRequests();
    initMobileBottomSheet();
});

function initMap() {
    // Initialize Leaflet map with a neutral China-wide default center.
    map = L.map('mapView').setView([35.8617, 104.1954], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Initialize marker cluster group
    markerClusterGroup = L.markerClusterGroup({
        maxClusterRadius: 50,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false,
        zoomToBoundsOnClick: true,
        iconCreateFunction: function(cluster) {
            var count = cluster.getChildCount();
            var size = count < 10 ? 'small' : count < 50 ? 'medium' : 'large';
            var sizes = { small: 36, medium: 44, large: 52 };
            return L.divIcon({
                html: '<div style="background:var(--color-primary, #E8913A);color:white;border-radius:50%;width:' + sizes[size] + 'px;height:' + sizes[size] + 'px;display:flex;align-items:center;justify-content:center;font-weight:600;font-size:0.875rem;box-shadow:0 2px 8px rgba(0,0,0,0.2);border:3px solid white;">' + count + '</div>',
                className: 'marker-cluster-custom',
                iconSize: L.point(sizes[size], sizes[size])
            });
        }
    });
    map.addLayer(markerClusterGroup);

    // Try to get user location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(pos) {
            if (hasFitInitialRequests) return;
            map.setView([pos.coords.latitude, pos.coords.longitude], 13);
        });
    }
}

function loadRequests(filter) {
    filter = filter || 'all';
    fetch('/respite/requests?type=' + filter)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            allRequests = data.requests;
            renderMarkers(allRequests);
            renderList(allRequests);
            fitMapToRequests(allRequests);
        });
}

function renderMarkers(requests) {
    // Clear existing markers from cluster group
    if (markerClusterGroup) {
        markerClusterGroup.clearLayers();
    }
    markers = [];

    requests.forEach(function(req) {
        if (!req.latitude || !req.longitude) return;

        var color = req.pin_color === 'orange' ? '#E8913A' : '#5B9A6B';
        var icon = L.divIcon({
            className: 'custom-pin',
            html: '<div style="background:' + color + ';width:24px;height:24px;border-radius:50%;border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.3);' + (req.status === 'pending' ? 'animation:pulse 2s infinite;' : '') + '"></div>',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });

        var marker = L.marker([req.latitude, req.longitude], {icon: icon});
        marker.on('click', function() { showInfoWindow(req); });
        markerClusterGroup.addLayer(marker);
        markers.push(marker);
    });
}

function fitMapToRequests(requests) {
    if (hasFitInitialRequests || !map) return;

    var points = requests
        .filter(function(req) { return req.latitude && req.longitude; })
        .map(function(req) { return [req.latitude, req.longitude]; });

    if (!points.length) return;

    hasFitInitialRequests = true;
    if (points.length === 1) {
        map.setView(points[0], 13);
        return;
    }

    map.fitBounds(L.latLngBounds(points), {
        paddingTopLeft: [380, 40],
        paddingBottomRight: [40, 40],
        maxZoom: 13
    });
}

function renderList(requests) {
    var list = document.getElementById('requestList');
    if (!requests.length) {
        list.innerHTML = '<div class="text-center py-4"><p class="text-muted">No requests in this area yet.</p></div>';
        return;
    }

    var html = '';
    requests.forEach(function(req) {
        var typeColor = req.request_type === 'service' ? '#E8913A' : '#5B9A6B';
        var typeLabel = req.request_type === 'service' ? '\uD83D\uDFE0 Need Help' : '\uD83D\uDFE2 Equipment';
        html += '<div class="wl-card mb-2" style="cursor:pointer;" onclick="focusRequest(' + req.id + ', ' + req.latitude + ', ' + req.longitude + ')">';
        html += '<div class="card-body p-3">';
        html += '<div class="d-flex justify-content-between align-items-start">';
        html += '<div><span class="badge" style="background:' + typeColor + ';font-size:0.7rem;">' + typeLabel + '</span>';
        if (req.is_certified) html += ' <span class="badge badge-certified" style="font-size:0.65rem;">\u2713</span>';
        html += '<h6 class="mt-1 mb-1" style="font-size:0.875rem;">' + escapeHtml(req.title) + '</h6>';
        html += '<p class="small text-muted mb-0">' + escapeHtml(req.city) + ' \u00B7 ' + req.create_at + '</p></div>';
        html += '<span class="badge" style="background:var(--color-bg-subtle);color:var(--color-text-secondary);font-size:0.7rem;">' + req.status + '</span>';
        html += '</div></div></div>';
    });
    list.innerHTML = html;
}

function showInfoWindow(req) {
    // Fetch full detail
    fetch('/respite/request/' + req.id)
        .then(function(r) { return r.json(); })
        .then(function(data) {
            var content = '<div style="min-width:250px;">';
            content += '<span class="badge mb-2" style="background:' + (data.request_type === 'service' ? '#E8913A' : '#5B9A6B') + ';">' + (data.request_type === 'service' ? '\uD83D\uDFE0 Need Help' : '\uD83D\uDFE2 Equipment') + '</span>';
            if (data.is_certified) content += ' <span class="badge badge-certified">\u2713 Verified</span>';
            content += '<h6>' + escapeHtml(data.title) + '</h6>';
            content += '<p class="small text-muted">' + escapeHtml(data.username) + ' \u00B7 ' + data.create_at + '</p>';
            if (data.description) content += '<p class="small">' + escapeHtml(data.description) + '</p>';
            if (data.time_limit) content += '<p class="small"><strong>Time:</strong> ' + escapeHtml(data.time_limit) + '</p>';
            if (data.acceptor_username) {
                content += '<p class="small"><strong>Status:</strong> Accepted by ' + escapeHtml(data.acceptor_username) + '</p>';
            }
            if (data.acceptor_contact) {
                content += renderContactBlock('Helper contact', data.acceptor_contact);
            }
            if (data.requester_contact) {
                content += renderContactBlock('Requester contact', data.requester_contact);
            }

            if (data.status === 'pending' && !data.is_requester && window.isCertified) {
                content += '<button class="btn btn-wl-primary btn-sm w-100 mt-2" onclick="acceptRequest(' + data.id + ')">I Can Help</button>';
            } else if (data.can_complete) {
                content += '<button class="btn btn-sm w-100 mt-2" style="background:var(--color-success);color:white;" onclick="completeRequest(' + data.id + ')">Mark Completed</button>';
            } else if (!window.isCertified && data.status === 'pending') {
                content += '<button class="btn btn-sm w-100 mt-2" disabled style="opacity:0.5;">Certification Required</button>';
            }
            content += '</div>';

            L.popup({maxWidth: 300})
                .setLatLng([req.latitude, req.longitude])
                .setContent(content)
                .openOn(map);
        });
}

function renderContactBlock(title, contact) {
    var lines = [];
    if (contact.phone) lines.push('Phone: ' + escapeHtml(contact.phone));
    if (contact.email) lines.push('Email: ' + escapeHtml(contact.email));
    if (!lines.length) lines.push('No contact details on profile.');
    return '<div class="small mt-2 p-2" style="background:var(--color-bg-subtle);border-radius:var(--radius-sm);">' +
        '<strong>' + escapeHtml(title) + '</strong><br>' +
        '<span>' + escapeHtml(contact.username || '') + '</span><br>' +
        lines.join('<br>') +
        '</div>';
}

function focusRequest(id, lat, lng) {
    if (lat && lng) {
        map.setView([lat, lng], 15);
        var req = allRequests.find(function(r) { return r.id === id; });
        if (req) showInfoWindow(req);
    }
}

function filterPins(type, btn) {
    document.querySelectorAll('[data-filter]').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    loadRequests(type);
}

// Radius zoom presets
function setRadiusZoom(km, btn) {
    // Update active state on radius buttons
    if (btn) {
        btn.parentElement.querySelectorAll('.wl-tag').forEach(function(b) { b.classList.remove('active'); });
        btn.classList.add('active');
    }
    var zoom = radiusZoomMap[km] || 13;
    map.setZoom(zoom);
}

// Type selector for create modal
function selectReqType(type, el) {
    document.querySelectorAll('.type-option').forEach(function(opt) {
        opt.style.borderColor = 'var(--color-border)';
        opt.classList.remove('active');
    });
    el.style.borderColor = 'var(--color-primary)';
    el.classList.add('active');
    el.querySelector('input[type="radio"]').checked = true;

    var serviceFields = document.getElementById('serviceFields');
    var equipmentFields = document.getElementById('equipmentFields');
    if (type === 'service') {
        serviceFields.style.display = 'block';
        equipmentFields.style.display = 'none';
    } else {
        serviceFields.style.display = 'none';
        equipmentFields.style.display = 'block';
    }
}

function toggleSidebar() {
    var sidebar = document.getElementById('mapSidebar');
    var toggle = document.getElementById('sidebarToggle');
    sidebar.classList.toggle('collapsed');
    toggle.style.display = sidebar.classList.contains('collapsed') ? 'block' : 'none';
    setTimeout(function() { map.invalidateSize(); }, 350);
}

// Mobile bottom sheet drag behavior
function initMobileBottomSheet() {
    if (window.innerWidth >= 768) return;
    var sidebar = document.getElementById('mapSidebar');
    if (!sidebar) return;

    var startY = 0, startHeight = 0, isDragging = false;

    sidebar.addEventListener('touchstart', function(e) {
        // Only start drag from the top area (handle)
        var rect = sidebar.getBoundingClientRect();
        var touchY = e.touches[0].clientY;
        if (touchY - rect.top > 40) return; // only drag from handle area
        isDragging = true;
        startY = e.touches[0].clientY;
        startHeight = sidebar.offsetHeight;
        sidebar.style.transition = 'none';
    }, { passive: true });

    sidebar.addEventListener('touchmove', function(e) {
        if (!isDragging) return;
        var deltaY = startY - e.touches[0].clientY;
        var newHeight = Math.max(60, Math.min(window.innerHeight * 0.85, startHeight + deltaY));
        sidebar.style.maxHeight = newHeight + 'px';
    }, { passive: true });

    sidebar.addEventListener('touchend', function() {
        if (!isDragging) return;
        isDragging = false;
        sidebar.style.transition = 'max-height 0.3s ease';
        var currentHeight = sidebar.offsetHeight;
        // Snap to open or closed
        if (currentHeight < 120) {
            sidebar.style.maxHeight = '60px';
            sidebar.classList.add('collapsed');
        } else {
            sidebar.style.maxHeight = '50vh';
            sidebar.classList.remove('collapsed');
        }
        setTimeout(function() { map.invalidateSize(); }, 350);
    });
}

function submitRequest() {
    var reqType = document.querySelector('input[name="req_type"]:checked');
    var type = reqType ? reqType.value : 'service';
    var category;

    if (type === 'equipment') {
        var equipCat = document.getElementById('reqEquipCategory');
        category = equipCat ? equipCat.value : 'other';
    } else {
        category = document.getElementById('reqCategory').value;
    }

    var data = {
        request_type: type,
        title: document.getElementById('reqTitle').value,
        description: document.getElementById('reqDesc').value,
        category: category,
        city: document.getElementById('reqCity').value,
        time_limit: type === 'service' ? document.getElementById('reqTime').value : '',
        latitude: map.getCenter().lat,
        longitude: map.getCenter().lng
    };

    fetch('/respite/create', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    }).then(function(r) { return r.json(); }).then(function(res) {
        if (res.success) {
            bootstrap.Modal.getInstance(document.getElementById('createRequestModal')).hide();
            showToast('Request posted successfully!', 'success');
            loadRequests();
            // Clear form
            document.getElementById('reqTitle').value = '';
            document.getElementById('reqDesc').value = '';
            document.getElementById('reqCity').value = '';
            var reqTime = document.getElementById('reqTime');
            if (reqTime) reqTime.value = '';
        } else {
            showToast(res.error || 'Failed to create request.', 'error');
        }
    });
}

function acceptRequest(id) {
    if (!confirm('Are you sure you want to accept this request?')) return;
    fetch('/respite/request/' + id + '/accept', { method: 'POST' })
        .then(function(r) { return r.json(); })
        .then(function(res) {
            if (res.success) {
                showToast('Request accepted. Contact details are available in the request card.', 'success');
                map.closePopup();
                loadRequests();
            } else {
                showToast(res.error, 'error');
            }
        });
}

function completeRequest(id) {
    fetch('/respite/request/' + id + '/complete', { method: 'POST' })
        .then(function(r) { return r.json(); })
        .then(function(res) {
            if (res.success) {
                showToast('Request marked as completed!', 'success');
                map.closePopup();
                loadRequests();
            } else {
                showToast(res.error, 'error');
            }
        });
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Add CSS for pin pulse animation
var style = document.createElement('style');
style.textContent = '@keyframes pulse{0%,100%{transform:scale(1);opacity:1}50%{transform:scale(1.3);opacity:0.7}} .marker-cluster-custom{background:transparent !important;}';
document.head.appendChild(style);

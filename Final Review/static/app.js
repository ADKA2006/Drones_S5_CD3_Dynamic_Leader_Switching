const socket = io();
const $ = (id) => document.getElementById(id);

let drones = [];
let latestTelemetry = {};
let toastTimer;

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;'
    }[ch]));
}

function colorCss(rgb) {
    if (!Array.isArray(rgb) || rgb.length < 3) return '#ffffff';
    return `rgb(${rgb.slice(0, 3).map(
        v => Math.round(Math.max(0, Math.min(1, Number(v) || 0)) * 255)
    ).join(',')})`;
}

function toast(message) {
    const el = $('toast');
    el.textContent = message;
    el.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('show'), 3200);
}

function setMessage(id, message, error = false) {
    const el = $(id);
    el.textContent = message;
    el.classList.toggle('error', error);
}

function selectedDrone() {
    return drones.find(d => d.drone_id === $('droneSelect').value);
}

socket.on('connect', () => {
    $('serverStatus').textContent = 'Dashboard connected';
    document.querySelector('.pulse').style.background = 'var(--green)';
    loadDrones();
});

socket.on('disconnect', () => {
    $('serverStatus').textContent = 'Reconnecting…';
    document.querySelector('.pulse').style.background = 'var(--red)';
});

socket.on('drone_list', renderDrones);

socket.on('drone_registered', info => {
    toast(`Connected: ${info.drone_id}`);
});

socket.on('control_points_saved', info => {
    setMessage('editorMessage', info.message);
    loadDrones();
});

socket.on('drone_deleted', info => {
    toast(`Deleted ${info.drone_id} and its stored telemetry.`);
    loadDrones();
});

socket.on('server_error', info => {
    setMessage('editorMessage', info.message || 'Server error', true);
    toast(info.message || 'Server error');
});

socket.on('telemetry_update', info => {
    renderTelemetry(info.drone_id, info.payload);
});

socket.on('plot_ready', info => {
    const gallery = $('plotGallery');
    const empty = gallery.querySelector('.empty-state');

    if (empty) empty.remove();

    const card = document.createElement('article');
    card.className = 'plot-card';

    const title = document.createElement('h3');
    title.textContent = info.title;

    const img = document.createElement('img');
    img.src = `${info.url}?v=${Date.now()}`;
    img.alt = info.title;

    const link = document.createElement('a');
    link.href = info.url;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = 'Open saved PNG';

    card.append(title, img, link);
    gallery.prepend(card);

    setMessage('plotMessage', `Generated and saved ${info.filename}`);
    toast(`${info.title} generated.`);

    document.querySelectorAll('.plot-button').forEach(b => {
        b.disabled = false;
    });
});

socket.on('plot_error', info => {
    setMessage('plotMessage', info.message || 'Could not generate plot.', true);

    document.querySelectorAll('.plot-button').forEach(b => {
        b.disabled = false;
    });
});

async function loadDrones() {
    try {
        const response = await fetch('/api/drones');

        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }

        renderDrones(await response.json());
    } catch (err) {
        toast('Could not load drone list: ' + err.message);
    }
}

function renderDrones(list) {
    const previous = $('droneSelect').value;
    drones = Array.isArray(list) ? list : [];

    $('totalCount').textContent = drones.length;
    $('connectedCount').textContent =
        drones.filter(d => d.status === 'connected').length;
    $('disconnectedCount').textContent =
        drones.filter(d => d.status !== 'connected').length;

    const select = $('droneSelect');

    select.innerHTML =
        '<option value="">Select a drone…</option>' +
        drones.map(d =>
            `<option value="${escapeHtml(d.drone_id)}">${escapeHtml(d.label)} (${escapeHtml(d.status)})</option>`
        ).join('');

    if (drones.some(d => d.drone_id === previous)) {
        select.value = previous;
    }

    const listEl = $('droneList');

    if (!drones.length) {
        listEl.innerHTML =
            '<div class="empty-state">No drone records yet. Start a Webots controller to register a drone.</div>';
    } else {
        listEl.innerHTML = drones.map(d => `
            <article class="drone-card">
                <div class="drone-card-head">
                    <div>
                        <div class="drone-name">
                            <i class="color-dot" style="background:${colorCss(d.color)}"></i>
                            ${escapeHtml(d.label)}
                        </div>
                        <div class="drone-id">${escapeHtml(d.drone_id)}</div>
                    </div>
                    <span class="drone-status ${d.status === 'connected' ? 'connected' : 'disconnected'}">
                        ${d.status === 'connected' ? 'CONNECTED' : 'REMOVED / OFFLINE'}
                    </span>
                </div>
                <div class="drone-meta">
                    Last seen: ${escapeHtml(d.last_seen_text || 'Never')}
                    · ${Array.isArray(d.control_points) ? d.control_points.length : 0} saved control points
                </div>
                <div class="drone-actions">
                    <button class="button secondary" data-select="${escapeHtml(d.drone_id)}">Edit path</button>
                    <button class="button secondary" data-delete="${escapeHtml(d.drone_id)}">Delete record</button>
                </div>
            </article>
        `).join('');
    }

    listEl.querySelectorAll('[data-select]').forEach(btn => {
        btn.addEventListener('click', () => {
            select.value = btn.dataset.select;
            loadSelectedPoints();
            $('controlPoints').scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
        });
    });

    listEl.querySelectorAll('[data-delete]').forEach(btn => {
        btn.addEventListener('click', () => {
            const did = btn.dataset.delete;

            if (confirm(`Permanently delete ${did} and all its stored telemetry? This cannot be undone.`)) {
                socket.emit('deleteDrone', { drone_id: did });
            }
        });
    });

    updateSelectedLabel();

    const selected = selectedDrone();

    if (selected && document.activeElement !== $('controlPoints')) {
        loadSelectedPoints(false);
    }
}

function updateSelectedLabel() {
    const d = selectedDrone();

    $('selectedDroneLabel').textContent = d
        ? `${d.label} · ${d.status}`
        : 'Select a drone';
}

function loadSelectedPoints(showMessage = true) {
    const d = selectedDrone();
    updateSelectedLabel();

    if (!d) return;

    $('controlPoints').value =
        (d.control_points || []).map(p => p.join(', ')).join('\n');

    $('degreeInput').value = d.degree ?? 3;

    if (showMessage) {
        setMessage('editorMessage', `Loaded saved points for ${d.label}.`);
    }
}

$('droneSelect').addEventListener('change', () => loadSelectedPoints());
$('refreshBtn').addEventListener('click', loadDrones);
$('restorePointsBtn').addEventListener('click', () => loadSelectedPoints());

$('savePointsBtn').addEventListener('click', () => {
    const d = selectedDrone();

    if (!d) {
        setMessage('editorMessage', 'Select a drone first.', true);
        return;
    }

    const lines = $('controlPoints').value
        .split(/\r?\n/)
        .map(s => s.trim())
        .filter(Boolean);

    const points = [];

    for (let i = 0; i < lines.length; i++) {
        const values = lines[i]
            .split(/[\s,;]+/)
            .filter(Boolean)
            .map(Number);

        if (values.length !== 3 || values.some(v => !Number.isFinite(v))) {
            setMessage(
                'editorMessage',
                `Invalid row ${i + 1}. Use three finite numbers: x, y, z.`,
                true
            );
            return;
        }

        points.push(values);
    }

    const degree = Number($('degreeInput').value);

    if (!Number.isInteger(degree) || degree < 1 || points.length < degree + 1) {
        setMessage(
            'editorMessage',
            'Degree must be an integer ≥ 1 and you need at least degree + 1 points.',
            true
        );
        return;
    }

    setMessage('editorMessage', 'Saving path…');

    socket.emit('setControlPoints', {
        drone_id: d.drone_id,
        control_points: points,
        degree
    });
});

document.querySelectorAll('.plot-button').forEach(btn => {
    btn.addEventListener('click', () => {
        btn.disabled = true;

        setMessage('plotMessage', `Generating ${btn.textContent}…`);

        const selected = $('droneSelect').value;

        socket.emit('generatePlot', {
            plot_type: btn.dataset.plot,
            drone_ids: selected ? [selected] : null
        });
    });
});

function renderTelemetry(droneId, payload) {
    latestTelemetry[droneId] = payload;

    const entries = Object.entries(latestTelemetry).slice(-8);

    $('sampleCount').textContent = 'Live';

    const feed = $('telemetryFeed');

    feed.innerHTML = entries.map(([id, p]) => {
        const n = key =>
            Number.isFinite(Number(p[key]))
                ? Number(p[key]).toFixed(2)
                : '—';

        return `
            <article class="telemetry-item">
                <strong>${escapeHtml(id)} · t=${escapeHtml(p.t ?? p.time ?? '—')} s</strong>
                <span>X: ${n('x')} m · Y: ${n('y')} m · Z: ${n('z')} m</span>
                <span>Tracking error: ${n('tracking_error')} m · Clearance: ${n('obstacle_clearance')} m</span>
                <span>Leader: ${escapeHtml(p.leader_id ?? '—')}</span>
            </article>
        `;
    }).join('');
}

socket.on("leader_update", (data) => {
    const leader = data.leader_id ?? "No leader";

    const element = document.getElementById("leader-status");
    if (element) {
        element.textContent = `Current Leader: ${leader}`;
    }

    console.log("Leader changed:", data);
});
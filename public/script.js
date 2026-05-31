const uploadArea     = document.getElementById('upload-area');
const uploadInput    = document.getElementById('upload-input');
const statusEl       = document.getElementById('status');
const previewSection = document.getElementById('preview-section');
const previewTitle   = document.getElementById('preview-title');
const eventsContainer = document.getElementById('events-container');
const downloadBtn    = document.getElementById('download-btn');

let icsText = null;

// ── Drag and drop ──────────────────────────────────────────
uploadArea.addEventListener('dragover', e => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

['dragleave', 'dragend'].forEach(evt =>
    uploadArea.addEventListener(evt, () => uploadArea.classList.remove('drag-over'))
);

uploadArea.addEventListener('drop', e => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showError('Please drop a PDF file.');
        return;
    }
    convert(file);
});

uploadInput.addEventListener('change', e => {
    const file = e.target.files[0];
    if (file) convert(file);
    uploadInput.value = '';
});

downloadBtn.addEventListener('click', () => {
    if (!icsText) return;
    const blob = new Blob([icsText], { type: 'text/calendar' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href     = url;
    a.download = 'schedule.ics';
    a.click();
    URL.revokeObjectURL(url);
});

// ── Network ────────────────────────────────────────────────
async function convert(file) {
    showLoading('Converting your schedule…');

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/convert', { method: 'POST', body: formData });

        if (!response.ok) {
            let detail = response.statusText;
            try { detail = (await response.json()).detail || detail; } catch (_) {}
            showError(`Error: ${detail}`);
            return;
        }

        icsText = await response.text();
        hideStatus();
        renderPreview(parseICS(icsText));
    } catch (_) {
        showError('Could not reach the server. Make sure the server is running.');
    }
}

// ── Status ─────────────────────────────────────────────────
function showLoading(msg) {
    statusEl.className = 'status loading';
    statusEl.innerHTML = `<div class="spinner"></div><span>${msg}</span>`;
    previewSection.classList.add('hidden');
    icsText = null;
}

function showError(msg) {
    statusEl.className = 'status error';
    statusEl.textContent = `⚠ ${msg}`;
}

function hideStatus() { statusEl.className = 'status hidden'; }

// ── ICS parser ─────────────────────────────────────────────
function parseICS(text) {
    // Unfold continuation lines (RFC 5545: CRLF/LF + SPACE/TAB)
    const unfolded = text.replace(/\r?\n[ \t]/g, '');
    const lines = unfolded.split(/\r?\n/);
    const events = [];
    let cur = null;

    for (const line of lines) {
        if (line === 'BEGIN:VEVENT') { cur = {}; continue; }
        if (line === 'END:VEVENT')   { if (cur) events.push(cur); cur = null; continue; }
        if (!cur) continue;
        const ci = line.indexOf(':');
        if (ci === -1) continue;
        // Strip parameters (e.g. DTSTART;TZID=... → DTSTART)
        cur[line.slice(0, ci).split(';')[0]] = line.slice(ci + 1);
    }
    return events;
}

// ── Palette ────────────────────────────────────────────────
const PALETTE = [
    { bg: '#dbeafe', border: '#2563eb', text: '#1e40af' },
    { bg: '#ede9fe', border: '#7c3aed', text: '#5b21b6' },
    { bg: '#ccfbf1', border: '#0d9488', text: '#134e4a' },
    { bg: '#fce7f3', border: '#db2777', text: '#831843' },
    { bg: '#fef3c7', border: '#d97706', text: '#78350f' },
    { bg: '#dcfce7', border: '#16a34a', text: '#14532d' },
    { bg: '#ffedd5', border: '#ea580c', text: '#7c2d12' },
    { bg: '#e0e7ff', border: '#4338ca', text: '#312e81' },
];

const DAYS      = ['MO', 'TU', 'WE', 'TH', 'FR'];
const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
const PX_PER_MIN = 1.5; // 90px per hour

// ── Main renderer ──────────────────────────────────────────
function renderPreview(events) {
    const courseColors = new Map();
    let colorIdx = 0;

    const byDay  = { MO: [], TU: [], WE: [], TH: [], FR: [] };
    const onetime = [];

    for (const ev of events) {
        const { course } = parseSummary(ev.SUMMARY || '');
        if (!courseColors.has(course))
            courseColors.set(course, PALETTE[colorIdx++ % PALETTE.length]);
        const color = courseColors.get(course);

        if (ev.RRULE) {
            const m = ev.RRULE.match(/BYDAY=([^;]+)/);
            if (m) m[1].split(',').forEach(d => { if (byDay[d]) byDay[d].push({ ev, color }); });
        } else {
            onetime.push({ ev, color });
        }
    }

    // Time range from all recurring events
    let minMin = Infinity, maxMin = -Infinity, hasRecurring = false;
    for (const dayEvs of Object.values(byDay)) {
        for (const { ev } of dayEvs) {
            hasRecurring = true;
            minMin = Math.min(minMin, dtMinutes(ev.DTSTART));
            maxMin = Math.max(maxMin, dtMinutes(ev.DTEND));
        }
    }
    if (!hasRecurring) { minMin = 8 * 60; maxMin = 18 * 60; }

    const gridStart = Math.floor(minMin / 60) * 60;
    const gridEnd   = (Math.ceil(maxMin / 60) + 1) * 60;

    const count = courseColors.size;
    previewTitle.innerHTML =
        `Your Schedule <span class="event-count">${count} course${count !== 1 ? 's' : ''}</span>`;

    eventsContainer.innerHTML = '';
    eventsContainer.appendChild(buildLegend(courseColors));
    if (hasRecurring) eventsContainer.appendChild(buildCalendar(byDay, gridStart, gridEnd));
    if (onetime.length) eventsContainer.appendChild(buildOnetimeSection(onetime));

    previewSection.classList.remove('hidden');
}

// ── Legend ─────────────────────────────────────────────────
function buildLegend(courseColors) {
    const wrap = el('div', 'cal-legend');
    for (const [course, color] of courseColors) {
        const item = el('div', 'legend-item');
        const dot  = el('span', 'legend-dot');
        dot.style.background = color.border;
        item.appendChild(dot);
        item.appendChild(document.createTextNode(course));
        wrap.appendChild(item);
    }
    return wrap;
}

// ── Weekly calendar ────────────────────────────────────────
function buildCalendar(byDay, gridStart, gridEnd) {
    const gridHeight = (gridEnd - gridStart) * PX_PER_MIN;

    const scroll = el('div', 'cal-scroll');
    const cal    = el('div', 'calendar');

    // Header row
    const header = el('div', 'cal-header');
    header.appendChild(el('div', 'cal-header-gutter'));
    DAY_NAMES.forEach(name => {
        const d = el('div', 'cal-day-label');
        d.textContent = name;
        header.appendChild(d);
    });
    cal.appendChild(header);

    // Body
    const body = el('div', 'cal-body');
    body.style.height = `${gridHeight}px`;

    // Time gutter
    const timeCol = el('div', 'cal-time-col');
    timeCol.style.height = `${gridHeight}px`;
    for (let m = gridStart; m <= gridEnd; m += 60) {
        const lbl = el('div', 'cal-time-label');
        lbl.style.top = `${(m - gridStart) * PX_PER_MIN}px`;
        lbl.textContent = fmtHour(m);
        timeCol.appendChild(lbl);
    }
    body.appendChild(timeCol);

    // Day columns
    DAYS.forEach(day => {
        const col = el('div', 'cal-day-col');
        col.style.height = `${gridHeight}px`;

        // Grid lines every 30 min
        for (let m = gridStart; m < gridEnd; m += 30) {
            const line = el('div', m % 60 === 0 ? 'cal-hour-line' : 'cal-half-line');
            line.style.top = `${(m - gridStart) * PX_PER_MIN}px`;
            col.appendChild(line);
        }

        // Events
        (byDay[day] || []).forEach(({ ev, color }) =>
            col.appendChild(buildCalEvent(ev, color, gridStart))
        );

        body.appendChild(col);
    });

    cal.appendChild(body);
    scroll.appendChild(cal);
    return scroll;
}

function buildCalEvent(ev, color, gridStart) {
    const { course, type } = parseSummary(ev.SUMMARY || '');
    const startMin = dtMinutes(ev.DTSTART);
    const endMin   = dtMinutes(ev.DTEND);
    const top      = (startMin - gridStart) * PX_PER_MIN;
    const height   = Math.max((endMin - startMin) * PX_PER_MIN, 18);

    const abbr = { Lecture: 'Lec', Discussion: 'Dis', Lab: 'Lab',
                   Final: 'Final', Midterm: 'Mid' }[type] || type;

    const div = el('div', 'cal-event');
    div.style.cssText += `top:${top}px;height:${height}px;` +
        `background-color:${color.bg};border-left-color:${color.border};color:${color.text};`;

    const nameEl = el('span', 'cal-event-course');
    nameEl.textContent = course;
    div.appendChild(nameEl);

    if (height >= 32) {
        const typeEl = el('span', 'cal-event-type');
        typeEl.textContent = abbr;
        div.appendChild(typeEl);
    }
    if (height >= 52) {
        const timeEl = el('span', 'cal-event-time');
        timeEl.textContent = `${formatTime(ev.DTSTART)}–${formatTime(ev.DTEND)}`;
        div.appendChild(timeEl);
    }
    return div;
}

// ── One-time events (finals / midterms) ────────────────────
function buildOnetimeSection(events) {
    // Deduplicate: one card per unique SUMMARY
    const seen = new Set();
    const deduped = events.filter(({ ev }) => {
        const k = ev.SUMMARY || '';
        if (seen.has(k)) return false;
        seen.add(k);
        return true;
    });

    const section = el('div', 'onetime-section');
    const title   = el('h3', 'onetime-title');
    title.textContent = 'Exams';
    section.appendChild(title);

    const list = el('div', 'onetime-list');
    for (const { ev, color } of deduped) {
        const { course, type } = parseSummary(ev.SUMMARY || '');

        const item = el('div', 'onetime-item');
        item.style.borderLeftColor = color.border;

        const name = el('div', 'onetime-name');
        name.style.color = color.border;
        name.textContent = `${course} ${type}`;

        const loc     = ev.LOCATION ? ` · ${ev.LOCATION.trim()}` : '';
        const details = el('div', 'onetime-details');
        details.textContent =
            `${formatDate(ev.DTSTART)} · ${formatTime(ev.DTSTART)}–${formatTime(ev.DTEND)}${loc}`;

        item.appendChild(name);
        item.appendChild(details);
        list.appendChild(item);
    }
    section.appendChild(list);
    return section;
}

// ── Helpers ────────────────────────────────────────────────
function parseSummary(summary) {
    for (const t of ['Lecture', 'Discussion', 'Lab', 'Final', 'Midterm']) {
        if (summary.endsWith(` ${t}`))
            return { course: summary.slice(0, -(t.length + 1)), type: t };
    }
    return { course: summary, type: 'Other' };
}

function dtMinutes(dtStr = '') {
    const t = dtStr.indexOf('T');
    if (t === -1) return 0;
    return parseInt(dtStr.slice(t + 1, t + 3), 10) * 60
         + parseInt(dtStr.slice(t + 3, t + 5), 10);
}

function formatTime(dtStr = '') {
    const t = dtStr.indexOf('T');
    if (t === -1) return '';
    const h = parseInt(dtStr.slice(t + 1, t + 3), 10);
    const m = dtStr.slice(t + 3, t + 5);
    return `${h % 12 || 12}:${m} ${h >= 12 ? 'PM' : 'AM'}`;
}

function formatDate(dtStr = '') {
    const mo = parseInt(dtStr.slice(4, 6), 10);
    const d  = parseInt(dtStr.slice(6, 8), 10);
    const y  = dtStr.slice(0, 4);
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul',
                    'Aug','Sep','Oct','Nov','Dec'];
    return `${months[mo - 1]} ${d}, ${y}`;
}

function fmtHour(totalMin) {
    const h = totalMin / 60;
    if (h === 0)  return '12 AM';
    if (h === 12) return '12 PM';
    return h < 12 ? `${h} AM` : `${h - 12} PM`;
}

function el(tag, cls) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    return e;
}

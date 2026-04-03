"""Jinja2 template strings for the Claudio web app."""

BASE = """<!doctype html>
<html lang="en" data-theme="system">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}Claudio{% endblock %}</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNiAxNiI+PHJlY3Qgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiByeD0iMyIgZmlsbD0iIzdjNmFmNyIvPjxwYXRoIGQ9Ik0xMS4yIDUuM0E0LjIgNC4yIDAgMTAxMS4yIDEwLjciIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBmaWxsPSJub25lIi8+PC9zdmc+">
<script>
  // Apply saved theme + layout before render to avoid flash
  (function () {
    var t = localStorage.getItem('claudio-theme') || 'system';
    document.documentElement.dataset.theme = t;
    var l = localStorage.getItem('claudio-layout') || 'tiles';
    document.documentElement.dataset.layout = l;
  })();
</script>
<style>
  /* ── Dark (default) ─────────────────────────────────────────── */
  :root {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #22263a;
    --border: #2e3350;
    --text: #e2e4ef;
    --muted: #7a7f99;
    --accent: #7c6af7;
    --accent2: #5a9cf5;
    --user-bg: #1e2640;
    --asst-bg: #151820;
    --tool-bg: #181c2e;
    --green: #4ade80;
  }

  /* ── Light overrides ────────────────────────────────────────── */
  :root[data-theme="light"] {
    --bg: #f5f7fa;
    --surface: #ffffff;
    --surface2: #eef0f6;
    --border: #d8dbe8;
    --text: #1a1d27;
    --muted: #6b7080;
    --accent: #6c5ce7;
    --accent2: #2563eb;
    --user-bg: #eef2ff;
    --asst-bg: #f5f7fa;
    --tool-bg: #eef0f6;
    --green: #16a34a;
  }

  /* ── System: respect prefers-color-scheme ───────────────────── */
  @media (prefers-color-scheme: light) {
    :root[data-theme="system"] {
      --bg: #f5f7fa;
      --surface: #ffffff;
      --surface2: #eef0f6;
      --border: #d8dbe8;
      --text: #1a1d27;
      --muted: #6b7080;
      --accent: #6c5ce7;
      --accent2: #2563eb;
      --user-bg: #eef2ff;
      --asst-bg: #f5f7fa;
      --tool-bg: #eef0f6;
      --green: #16a34a;
    }
  }

  /* ── Base styles ────────────────────────────────────────────── */
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; line-height: 1.6; }
  a { color: var(--accent2); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* ── Nav ────────────────────────────────────────────────────── */
  .nav { background: var(--surface); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 100; }
  .nav-inner { max-width: 1100px; margin: 0 auto; padding: 10px 24px; display: flex; align-items: center; gap: 14px; }
  .nav-brand { font-weight: 700; font-size: 16px; color: var(--accent); letter-spacing: 0.5px; text-decoration: none; }
  .nav-brand span { color: var(--muted); font-weight: 400; }
  .nav-brand:hover { text-decoration: none; }
  .search-wrap { flex: 1; max-width: 400px; }
  .search-wrap input { width: 100%; background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; padding: 6px 12px; color: var(--text); font-size: 13px; outline: none; transition: border-color 0.15s; }
  .search-wrap input:focus { border-color: var(--accent); }
  .nav-spacer { flex: 1; }

  /* Theme toggle + GitHub icon */
  .theme-btn { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; color: var(--muted); cursor: pointer; font-size: 13px; padding: 4px 10px; display: flex; align-items: center; gap: 5px; white-space: nowrap; transition: border-color 0.15s, color 0.15s; }
  .theme-btn:hover { border-color: var(--accent); color: var(--text); }
  .github-btn { display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; color: var(--muted); transition: border-color 0.15s, color 0.15s; flex-shrink: 0; }
  .github-btn:hover { border-color: var(--accent); color: var(--text); text-decoration: none; }

  /* ── Index ──────────────────────────────────────────────────── */
  .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
  .project-group { margin-bottom: 20px; }
  .project-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .project-name { font-size: 13px; font-weight: 600; color: var(--muted); font-family: monospace; }
  .project-count { font-size: 12px; color: var(--muted); }
  /* ── Session list — shared ──────────────────────────────────── */
  .session-card { background: var(--surface); border: 1px solid var(--border); display: flex; transition: border-color 0.15s, box-shadow 0.15s; cursor: pointer; }
  .session-card:hover { border-color: var(--accent); box-shadow: 0 2px 12px rgba(0,0,0,0.15); }
  .session-title { font-size: 13px; font-weight: 500; line-height: 1.4; overflow: hidden; }
  .session-meta { display: flex; align-items: center; }
  .badge-msgs { background: var(--surface2); border-radius: 4px; padding: 2px 7px; font-size: 11px; color: var(--muted); }
  .badge-cost { background: var(--surface2); border-radius: 4px; padding: 2px 7px; font-size: 11px; color: var(--green); font-variant-numeric: tabular-nums; }
  .ts { font-size: 11px; color: var(--muted); }
  /* ── Rows layout (default) ──────────────────────────────────── */
  :root[data-layout="rows"] .session-list { display: flex; flex-direction: column; gap: 6px; }
  :root[data-layout="rows"] .session-card { flex-direction: row; align-items: center; gap: 12px; padding: 11px 16px; border-radius: 8px; }
  :root[data-layout="rows"] .session-title { flex: 1; white-space: nowrap; text-overflow: ellipsis; }
  :root[data-layout="rows"] .session-meta { flex-shrink: 0; gap: 12px; }
  :root[data-layout="rows"] .ts { min-width: 110px; text-align: right; }
  /* ── Tiles layout ───────────────────────────────────────────── */
  :root[data-layout="tiles"] .session-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }
  :root[data-layout="tiles"] .session-card { flex-direction: column; gap: 10px; padding: 16px; border-radius: 10px; min-height: 100px; }
  :root[data-layout="tiles"] .session-title { display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; flex: 1; }
  :root[data-layout="tiles"] .session-meta { margin-top: auto; }
  :root[data-layout="tiles"] .badge-msgs,
  :root[data-layout="tiles"] .badge-cost,
  :root[data-layout="tiles"] .ts { display: none; }
  .meta-compact { display: none; font-size: 11px; color: var(--muted); }
  :root[data-layout="tiles"] .meta-compact { display: block; }

  /* ── Transcript ─────────────────────────────────────────────── */
  .transcript { display: flex; flex-direction: column; }
  .msg { padding: 16px 20px; border-bottom: 1px solid var(--border); }
  .msg-user { background: var(--user-bg); }
  .msg-assistant { background: var(--asst-bg); }
  .msg-header { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
  .role-label { font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; padding: 2px 7px; border-radius: 4px; }
  .role-user { background: #2e3a5a; color: #93b4f5; }
  .role-assistant { background: #2a2040; color: #a98cf7; }
  :root[data-theme="light"] .role-user,
  :root[data-theme="system"] .role-user { background: #dbeafe; color: #1d4ed8; }
  :root[data-theme="light"] .role-assistant,
  :root[data-theme="system"] .role-assistant { background: #ede9fe; color: #6d28d9; }
  @media (prefers-color-scheme: light) {
    :root[data-theme="system"] .role-user { background: #dbeafe; color: #1d4ed8; }
    :root[data-theme="system"] .role-assistant { background: #ede9fe; color: #6d28d9; }
  }
  .msg-ts { font-size: 11px; color: var(--muted); }
  .msg-body { font-size: 13px; white-space: pre-wrap; word-break: break-word; line-height: 1.75; }
  .tool-use { background: var(--tool-bg); border: 1px solid var(--border); border-radius: 6px; padding: 8px 12px; margin-top: 8px; font-family: monospace; font-size: 12px; }
  .tool-name { color: var(--accent); font-weight: 600; margin-bottom: 4px; }
  .tool-input { color: var(--muted); white-space: pre-wrap; max-height: 120px; overflow: auto; }

  /* ── Session header ─────────────────────────────────────────── */
  .session-hdr { background: var(--surface); border-bottom: 1px solid var(--border); padding: 16px 24px; }
  .session-hdr h1 { font-size: 17px; font-weight: 600; margin-bottom: 6px; }
  .session-hdr-meta { display: flex; gap: 16px; flex-wrap: wrap; font-size: 12px; color: var(--muted); }
  .session-hdr-meta span { display: flex; align-items: center; gap: 4px; }

  /* ── Layout ─────────────────────────────────────────────────── */
  .layout { display: grid; grid-template-columns: 1fr 260px; min-height: calc(100vh - 116px); }
  .main-panel { border-right: 1px solid var(--border); overflow: auto; }
  .side-panel { padding: 16px; overflow: auto; }
  .side-section { margin-bottom: 24px; }
  .side-section h3 { font-size: 11px; font-weight: 700; letter-spacing: 0.9px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
  .history-item { font-size: 12px; padding: 5px 0; border-bottom: 1px solid var(--border); color: var(--text); font-family: monospace; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .todo-item { font-size: 12px; padding: 4px 0; border-bottom: 1px solid var(--border); }
  .todo-item.done { color: var(--muted); text-decoration: line-through; }
  .todo-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; flex-shrink: 0; }
  .status-completed { background: var(--green); }
  .status-in_progress { background: var(--accent); }
  .status-pending { background: var(--border); }
  .pr-link { font-size: 12px; background: var(--surface2); border-radius: 6px; padding: 6px 10px; margin-bottom: 14px; }

  /* Copy-path */
  .copy-path { cursor: pointer; border-radius: 4px; padding: 1px 4px; transition: background 0.15s; }
  .copy-path:hover { background: var(--surface2); }

  /* Copied tooltip */
  .copy-tip {
    position: fixed; z-index: 9999; pointer-events: none;
    background: var(--accent); color: #fff;
    font-size: 11px; font-weight: 600; letter-spacing: 0.3px;
    padding: 4px 10px; border-radius: 5px;
    opacity: 0; transform: translateX(-50%) translateY(2px);
    transition: opacity 0.12s ease, transform 0.12s ease;
  }
  .copy-tip.show { opacity: 1; transform: translateX(-50%) translateY(0); }

  /* Search highlight */
  mark { background: rgba(124, 106, 247, 0.28); color: inherit; border-radius: 2px; padding: 0 1px; }
  :root[data-theme="light"] mark { background: rgba(108, 92, 231, 0.18); }
  @media (prefers-color-scheme: light) { :root[data-theme="system"] mark { background: rgba(108, 92, 231, 0.18); } }

  .hidden { display: none !important; }
  @media (max-width: 700px) { .layout { grid-template-columns: 1fr; } .side-panel { border-top: 1px solid var(--border); } }
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a class="nav-brand" href="/">claudio<span>.app</span></a>
    {% block nav_extra %}{% endblock %}
    <div class="nav-spacer"></div>
    <button class="theme-btn" id="layout-btn" title="Toggle layout" onclick="cycleLayout()">
      <span id="layout-icon">≡</span>
      <span id="layout-label">rows</span>
    </button>
    <button class="theme-btn" id="theme-btn" title="Toggle theme" onclick="cycleTheme()">
      <span id="theme-icon">💻</span>
      <span id="theme-label">system</span>
    </button>
    <a class="github-btn" href="https://github.com/shahfazal/claudio" target="_blank" rel="noopener noreferrer" title="View on GitHub">
      <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
    </a>
  </div>
</nav>
{% block body %}{% endblock %}

<script>
const THEMES = [
  { key: 'system', icon: '💻', label: 'system' },
  { key: 'light',  icon: '☀️',  label: 'light'  },
  { key: 'dark',   icon: '🌙', label: 'dark'   },
];

function applyTheme(key) {
  document.documentElement.dataset.theme = key;
  localStorage.setItem('claudio-theme', key);
  const t = THEMES.find(x => x.key === key) || THEMES[0];
  document.getElementById('theme-icon').textContent = t.icon;
  document.getElementById('theme-label').textContent = t.label;
}

function cycleTheme() {
  const current = localStorage.getItem('claudio-theme') || 'system';
  const idx = THEMES.findIndex(x => x.key === current);
  const next = THEMES[(idx + 1) % THEMES.length].key;
  applyTheme(next);
}

// Sync button labels on load
applyTheme(localStorage.getItem('claudio-theme') || 'system');

const LAYOUTS = [
  { key: 'rows',  icon: '≡', label: 'rows'  },
  { key: 'tiles', icon: '⊞', label: 'tiles' },
];

function applyLayout(key) {
  document.documentElement.dataset.layout = key;
  localStorage.setItem('claudio-layout', key);
  const idx = LAYOUTS.findIndex(x => x.key === key);
  const next = LAYOUTS[(idx + 1) % LAYOUTS.length];
  document.getElementById('layout-icon').textContent = next.icon;
  document.getElementById('layout-label').textContent = next.label;
}

function cycleLayout() {
  const current = localStorage.getItem('claudio-layout') || 'rows';
  const idx = LAYOUTS.findIndex(x => x.key === current);
  applyLayout(LAYOUTS[(idx + 1) % LAYOUTS.length].key);
}

applyLayout(localStorage.getItem('claudio-layout') || 'tiles');

// ── Copy-to-clipboard with floating tooltip ───────────────────
const _tip = Object.assign(document.createElement('div'), { className: 'copy-tip', textContent: 'Copied!' });
document.body.appendChild(_tip);
let _tipTimer;

function showCopyTip(el) {
  const r = el.getBoundingClientRect();
  _tip.style.left = (r.left + r.width / 2) + 'px';
  _tip.style.top  = (r.top - 30 + window.scrollY) + 'px';
  _tip.classList.remove('show');
  void _tip.offsetWidth; // force reflow so transition re-fires
  _tip.classList.add('show');
  clearTimeout(_tipTimer);
  _tipTimer = setTimeout(() => _tip.classList.remove('show'), 1500);
}

function execCopy(path) {
  const ta = Object.assign(document.createElement('textarea'), { value: path });
  ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0';
  document.body.appendChild(ta);
  ta.focus(); ta.select();
  try { document.execCommand('copy'); } catch (_) {}
  ta.remove();
}

document.addEventListener('click', e => {
  const el = e.target.closest('[data-path]');
  if (!el) return;
  const path = el.dataset.path;
  navigator.clipboard.writeText(path)
    .then(() => showCopyTip(el))
    .catch(() => { execCopy(path); showCopyTip(el); });
});
</script>
</body>
</html>"""

INDEX_TMPL = """\
{% extends "base.html" %}
{% block nav_extra %}
<div class="search-wrap">
  <input type="text" id="search" placeholder="Search sessions…" autofocus>
</div>
<span id="stats" style="font-size:12px;color:var(--muted)">{{ total }} sessions · {{ n_projects }} projects</span>
{% endblock %}

{% block body %}
<div class="container">
  {% for group in groups %}
  <div class="project-group" data-project="{{ group.label | lower }}" data-raw-project="{{ group.label }}">
    <div class="project-header">
      <span class="project-name copy-path" data-path="{{ group.cwd }}" title="Click to copy full path">{{ group.label }}</span>
      <span class="project-count">{{ group.sessions | length }} session{{ 's' if group.sessions | length != 1 }}</span>
    </div>
    <div class="session-list">
      {% for s in group.sessions %}
      <div class="session-card"
           data-title="{{ s.title | lower }}"
           data-raw-title="{{ s.title }}"
           onclick="location.href='{{ url_for('session_view', session_id=s.session_id) }}'">
        <span class="session-title">{{ s.title }}</span>
        <div class="session-meta">
          <span class="badge-msgs">{{ s.message_count }} msg{{ 's' if s.message_count != 1 }}</span>
          {% if s.cost_unknown %}<span class="badge-cost" style="color:var(--muted)">≈ ?</span>
          {% elif s.cost_usd %}<span class="badge-cost">{{ fmt_cost(s.cost_usd) }}</span>{% endif %}
          <span class="ts">{{ fmt_ts(s.started_at) }}</span>
          <span class="meta-compact">{{ s.message_count }} msg{{ 's' if s.message_count != 1 }}{% if s.cost_unknown %} · ≈ ?{% elif s.cost_usd %} · {{ fmt_cost(s.cost_usd) }}{% endif %}{% if s.started_at %} · {{ fmt_ts(s.started_at) }}{% endif %}</span>
        </div>
      </div>
      {% endfor %}
    </div>
  </div>
  {% endfor %}
</div>

<script>
const search = document.getElementById('search');
const statsEl = document.getElementById('stats');
const TOTAL_SESSIONS = {{ total }};
const TOTAL_PROJECTS = {{ n_projects }};

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function highlight(text, q) {
  if (!q) return esc(text);
  const lo = text.toLowerCase();
  let out = '', i = 0;
  while (i < text.length) {
    const j = lo.indexOf(q, i);
    if (j < 0) { out += esc(text.slice(i)); break; }
    out += esc(text.slice(i, j)) + '<mark>' + esc(text.slice(j, j + q.length)) + '</mark>';
    i = j + q.length;
  }
  return out;
}

search.addEventListener('input', () => {
  const q = search.value.toLowerCase().trim();

  document.querySelectorAll('.session-card').forEach(card => {
    const title = card.dataset.title || '';
    const proj  = card.closest('.project-group')?.dataset.project || '';
    const match = !q || title.includes(q) || proj.includes(q);
    card.classList.toggle('hidden', !match);
    card.querySelector('.session-title').innerHTML = highlight(card.dataset.rawTitle || title, q);
  });

  let visibleSessions = 0, visibleProjects = 0;
  document.querySelectorAll('.project-group').forEach(g => {
    const visible = [...g.querySelectorAll('.session-card')].some(c => !c.classList.contains('hidden'));
    g.classList.toggle('hidden', !visible);
    if (visible) {
      visibleProjects++;
      visibleSessions += [...g.querySelectorAll('.session-card')].filter(c => !c.classList.contains('hidden')).length;
      g.querySelector('.project-name').innerHTML = highlight(g.dataset.rawProject || '', q);
    }
  });

  if (q) {
    statsEl.textContent = `${visibleSessions} session${visibleSessions !== 1 ? 's' : ''} · ${visibleProjects} project${visibleProjects !== 1 ? 's' : ''}`;
  } else {
    statsEl.textContent = `${TOTAL_SESSIONS} sessions · ${TOTAL_PROJECTS} projects`;
  }
});
</script>
{% endblock %}
"""

SESSION_TMPL = """\
{% extends "base.html" %}
{% block nav_extra %}
<a href="{{ url_for('index') }}" style="font-size:13px;color:var(--muted)">← all sessions</a>
{% endblock %}

{% block body %}
<div class="session-hdr">
  <h1>{{ title }}</h1>
  <div class="session-hdr-meta">
    {% if session.cwd %}<span>📁 <span class="copy-path" data-path="{{ session.cwd }}" title="Click to copy full path">{{ strip_home(session.cwd) }}</span></span>{% endif %}
    <span>🕐 {{ fmt_ts(session.started_at) }}
      {%- if session.ended_at and session.ended_at != session.started_at %} → {{ fmt_ts(session.ended_at) }}{% endif %}
    </span>
    <span>💬 {{ session.message_count }} messages</span>
    {% if session.model %}<span style="font-family:monospace">{{ session.model }}</span>{% endif %}
    {% if session.cost_unknown %}<span>≈ unknown model</span>
    {% elif session.cost_usd %}<span>≈ {{ fmt_cost(session.cost_usd) }}</span>{% endif %}
    <span style="font-family:monospace;font-size:11px">{{ session.session_id }}</span>
  </div>
</div>

<div class="layout">
  <div class="main-panel">
    <div class="transcript">
      {% for msg in session.messages %}{% if not msg.is_sidechain %}
      <div class="msg msg-{{ msg.role }}">
        <div class="msg-header">
          <span class="role-label role-{{ msg.role }}">{{ msg.role }}</span>
          <span class="msg-ts">{{ fmt_ts(msg.timestamp) }}</span>
        </div>
        {% if msg.text %}<div class="msg-body">{{ msg.text }}</div>{% endif %}
        {% for tool in msg.tool_uses %}
        <div class="tool-use">
          <div class="tool-name">⚡ {{ tool.name }}</div>
          <div class="tool-input">{{ tool.input | tojson(indent=2) if tool.input else '' }}</div>
        </div>
        {% endfor %}
      </div>
      {% endif %}{% endfor %}
    </div>
  </div>

  <div class="side-panel">
    {% if session.pr_link %}
    <div class="pr-link">🔗 <a href="{{ session.pr_link }}" target="_blank" rel="noopener noreferrer">Pull Request</a></div>
    {% endif %}

    {% if todos %}
    <div class="side-section">
      <h3>Todos ({{ todos | length }})</h3>
      {% for todo in todos %}
      <div class="todo-item {{ 'done' if todo.status == 'completed' else '' }}">
        <span class="todo-dot status-{{ todo.status }}"></span>{{ todo.content }}
      </div>
      {% endfor %}
    </div>
    {% endif %}

    {% if history %}
    <div class="side-section">
      <h3>Command history</h3>
      {% for h in history[:50] %}{% if h.display %}
      <div class="history-item" title="{{ h.display }}">{{ h.display }}</div>
      {% endif %}{% endfor %}
    </div>
    {% endif %}
  </div>
</div>
{% endblock %}
"""

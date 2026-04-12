"""Jinja2 template strings for the Claudio web app."""

from markupsafe import Markup


def brain_icon(size: int = 11) -> Markup:
    """Side-profile brain SVG icon (PD licence, icooon-mono via svgrepo.com)."""
    # fill="currentColor" on the group inherits the parent element's CSS color,
    # so the icon automatically themes with the badge/heading it sits in.
    return Markup(
        f'<svg width="{size}" height="{size}" viewBox="0 0 512 512" '
        f'aria-hidden="true" style="vertical-align:-2px" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<g fill="currentColor">'
        f'<path d="M502.472,256.833c-6.491-61.075-40.69-110.46-86.082-144.101c-45.887-34.04-103.296-52.724-157.675-52.76'
        f"c-56.443,0.009-91.262,7.173-114.312,17.082c-22.776,9.644-33.774,22.98-39.813,30.843"
        f"c-24.68,4.029-49.262,18.348-68.77,38.697C15.107,168.343,0.054,197.423,0,229.381"
        f"c0,34.97,8.112,64.52,24.299,86.498c14.354,19.596,35.288,32.472,60.207,37.148"
        f"c1.638,9.456,5.56,20.003,13.672,29.647c8.412,10.06,19.888,17.383,33.454,22.032"
        f"c13.584,4.675,29.329,6.836,47.234,6.853h75.084c1.85,4.729,4.108,9.236,7.217,13.213"
        f"c7.642,9.785,18.649,16.656,31.834,20.96c13.248,4.33,28.859,6.288,46.995,6.296"
        f"c8.909,0,17.348-0.407,24.512-0.752h0.026c5.136-0.274,9.555-0.469,12.698-0.469"
        f"c9.466,0,18.526-2.302,26.318-6.819c7.793-4.498,14.257-11.166,18.676-19.357"
        f"c2.232-4.154,3.702-8.51,4.8-12.902c16.727-3.126,30.604-9.236,41.407-17.028"
        f"c12.663-9.121,21.367-20.11,27.283-30.09c11.556-19.552,16.267-41.247,16.285-61.384"
        f"C511.982,286.064,508.511,270.08,502.472,256.833z M475.862,352.849"
        f"c-4.649,7.837-11.352,16.241-20.916,23.121c-9.581,6.872-22.041,12.38-39.06,14.319"
        f"l-9.519,1.072l-0.7,9.555c-0.292,4.127-1.576,8.767-3.737,12.76"
        f"c-2.506,4.578-5.835,7.962-9.918,10.335c-4.1,2.356-9.006,3.71-14.78,3.718"
        f"c-4.073,0-8.714,0.24-13.858,0.496l1.922-0.088l-1.914,0.088"
        f"c-7.145,0.355-15.178,0.736-23.386,0.736c-21.943,0.035-38.299-3.356-48.747-8.864"
        f"c-5.251-2.736-9.06-5.906-11.884-9.511c-2.807-3.622-4.711-7.74-5.782-12.884"
        f"l-1.904-9.218h-92.812c-16.01,0-29.302-1.992-39.725-5.578"
        f"c-10.44-3.622-17.94-8.678-23.28-15.054c-6.96-8.306-9.024-17.32-9.289-25.237"
        f"l-0.31-10.077l-10.024-1.044C72.72,328.914,55.354,318.97,42.86,302.18"
        f"c-12.424-16.815-19.791-41.3-19.791-72.798c-0.054-24.422,11.874-48.474,29.443-66.875"
        f"c17.463-18.454,40.46-30.674,59.419-32.463l4.348-0.452l2.966-3.206"
        f"c1.328-1.452,2.382-2.851,3.294-4.002c5.986-7.474,12.114-15.806,31.002-24.139"
        f"c18.845-8.156,50.652-15.222,105.174-15.213c49.076-0.036,102.278,17.232,143.932,48.217"
        f"c41.726,31.046,71.78,75.153,77.094,129.578l0.203,2.098l0.922,1.887"
        f'c4.844,9.776,8.094,23.608,8.066,38.414C488.932,319.776,484.992,337.451,475.862,352.849z"/>'
        f'<path d="M357.042,146.417h24.059c5.172,0,9.378-4.242,9.378-9.573c0-5.215-4.206-9.43-9.378-9.43h-24.059'
        f'c-5.331,0-9.555,4.216-9.555,9.43C347.488,142.175,351.711,146.417,357.042,146.417z"/>'
        f'<path d="M244.21,237.307c0,5.287,4.25,9.564,9.501,9.564c5.162,0,9.475-4.276,9.475-9.564v-51.82'
        f"c0-2.399,0.709-2.958,0.886-3.179c3.02-2.966,14.274-2.966,22.164-2.966l0.301,0.106h62.226"
        f"c1.204,0,2.48-0.106,3.906-0.106c5.012-0.221,11.202-0.434,13.796,2.072c1.647,1.611,2.604,5.19,2.604,9.988"
        f"v31.809v1.416c-0.204,6.544-0.24,17.56,7.128,25.042c2.869,2.958,8.2,6.464,16.896,6.464h48.89"
        f"c5.136,0,9.352-4.233,9.352-9.555c0-5.198-4.216-9.519-9.352-9.519h-48.89l-3.418-0.806"
        f"c-1.736-1.797-1.621-8.332-1.621-11.467v-33.385c0-10.307-2.886-18.277-8.394-23.599"
        f"c-8.484-8.138-20.022-7.801-27.629-7.483c-1.258,0-2.302,0.045-3.268,0.045h-31.364"
        f"c0.372-2.622,0.372-5.26,0.274-7.633v-27.602c0-5.189-4.268-9.476-9.448-9.476"
        f"c-5.286,0-9.43,4.286-9.43,9.476v27.752c0,2.222,0,5.738-0.47,6.65c0,0-1.301,0.832-6.314,0.832"
        f"c-1.442,0-2.992,0-4.684,0c-12.92-0.16-27.778-0.204-36.615,8.474"
        f'c-2.887,2.922-6.5,8.208-6.5,16.648V237.307z"/>'
        f'<path d="M213.677,159.709c5.304,0,9.555-4.348,9.555-9.528v-13.594h15.93c5.154,0,9.413-4.268,9.413-9.554'
        f"c0-5.162-4.259-9.493-9.413-9.493h-15.93v-10.467c0-5.233-4.251-9.528-9.555-9.528"
        f'c-5.154,0-9.413,4.294-9.413,9.528v43.108C204.264,155.361,208.523,159.709,213.677,159.709z"/>'
        f'<path d="M110.841,173.682h39.468c6.438-0.229,12.565-0.229,15.452,2.807c2.559,2.498,3.967,8.111,3.967,16.17'
        f"v37.051c0,5.242,4.233,9.546,9.581,9.546c5.154,0,9.458-4.303,9.458-9.546v-7.882h14.886"
        f"c5.251,0,9.44-4.277,9.44-9.51c0-5.251-4.188-9.599-9.44-9.599h-14.886v-10.06"
        f"c0-13.672-3.135-23.351-9.626-29.736c-8.421-8.448-19.8-8.368-28.877-8.288h-39.423"
        f'c-5.384,0-9.511,4.312-9.511,9.475C101.33,169.387,105.457,173.682,110.841,173.682z"/>'
        f'<path d="M135.892,229.099c0-5.251-4.365-9.555-9.483-9.555H59.791c-5.26,0-9.555,4.304-9.555,9.555'
        f"c0,5.233,4.295,9.528,9.555,9.528h24.148v17.339c0,5.286,4.188,9.519,9.386,9.519"
        f'c5.402,0,9.59-4.233,9.59-9.519v-17.339h23.494C131.527,238.627,135.892,234.331,135.892,229.099z"/>'
        f'<path d="M194.576,291.412c1.665,0,3.242,0,4.649,0h76.704c17.498,0,30.772-4.64,39.6-13.884'
        f"c13.566-14.363,12.619-35.634,11.919-49.687c-0.124-2.683-0.248-5.206-0.248-7.323"
        f"c0-5.296-4.25-9.51-9.608-9.51c-5.18,0-9.368,4.215-9.368,9.51c0,2.408,0.124,5.171,0.248,8.111"
        f"c0.584,12.256,1.24,27.337-6.854,35.873c-4.941,5.26-13.682,7.89-25.689,7.89h-76.704"
        f"c-1.337,0-2.7,0-4.348,0c-15.133-0.23-40.584-0.638-56.753,15.319"
        f"c-9.068,8.944-13.681,21.545-13.681,37.396c0,5.153,4.17,9.52,9.484,9.52"
        f"c5.18,0,9.51-4.366,9.51-9.52c0-10.768,2.594-18.579,8.049-23.918"
        f'C161.935,290.934,181.612,291.235,194.576,291.412z"/>'
        f'<path d="M323.96,332.616c0-5.162-4.171-9.502-9.475-9.502H194.107c-5.19,0-9.538,4.34-9.538,9.502'
        f"c0,5.268,4.348,9.519,9.538,9.519h36.81v18.985c0,5.323,4.225,9.502,9.458,9.502"
        f'c5.251,0,9.493-4.179,9.493-9.502v-18.985h64.617C319.788,342.135,323.96,337.884,323.96,332.616z"/>'
        f'<path d="M377.887,370.065h-4.471v-17.693c0-5.384-4.18-9.528-9.475-9.528c-5.26,0-9.502,4.145-9.502,9.528'
        f"v17.693h-32.941c-5.242,0-9.502,4.241-9.502,9.528c0,5.224,4.26,9.448,9.502,9.448h56.39"
        f'c5.208,0,9.484-4.224,9.484-9.448C387.371,374.305,383.095,370.065,377.887,370.065z"/>'
        f'<path d="M421.579,323.114v-15.523h3.419c5.357,0,9.599-4.17,9.599-9.43c0-5.251-4.242-9.555-9.599-9.555'
        f"h-66.459c-5.225,0-9.511,4.304-9.511,9.555c0,5.26,4.286,9.43,9.511,9.43h43.983v15.523"
        f'c0,5.358,4.313,9.502,9.556,9.502C417.311,332.616,421.579,328.472,421.579,323.114z"/>'
        f'<path d="M451.333,347.909h-24.042c-5.304,0-9.546,4.18-9.546,9.467c0,5.286,4.241,9.43,9.546,9.43h24.042'
        f'c5.33,0,9.616-4.144,9.616-9.43C460.95,352.089,456.663,347.909,451.333,347.909z"/>'
        f"</g></svg>"
    )


def pie_icon(size: int = 13) -> Markup:
    """Chart-pie SVG icon (Lucide, ISC licence). stroke="currentColor" for theming.

    # Copyright (c) 2022 Lucide Contributors -- ISC Licence
    """
    return Markup(
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'aria-hidden="true" style="vertical-align:-2px" '
        f'xmlns="http://www.w3.org/2000/svg" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>'
        f'<path d="M22 12A10 10 0 0 0 12 2v10z"/>'
        f'</svg>'
    )


def archive_icon(size: int = 11) -> Markup:
    """File-archive (zip) SVG icon (Lucide, ISC licence). stroke="currentColor" for theming.

    # Copyright (c) 2022 Lucide Contributors, ISC Licence
    """
    return Markup(
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'aria-hidden="true" style="vertical-align:-2px" '
        f'xmlns="http://www.w3.org/2000/svg" fill="none" '
        f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M13.659 22H18a2 2 0 0 0 2-2V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6a2 2 0 0 0-2 2v11.5"/>'
        f'<path d="M14 2v5a1 1 0 0 0 1 1h5"/>'
        f'<path d="M8 12v-1"/>'
        f'<path d="M8 18v-2"/>'
        f'<path d="M8 7V6"/>'
        f'<circle cx="8" cy="20" r="2"/>'
        f"</svg>"
    )


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
    --muted: #8c91ad;
    --accent: #8778f7;
    --accent2: #5a9cf5;
    --user-bg: #1e2640;
    --asst-bg: #151820;
    --tool-bg: #181c2e;
    --green: #4ade80;
    --grid-color: #2e3350;
  }

  /* ── Light overrides ────────────────────────────────────────── */
  :root[data-theme="light"] {
    --bg: #f5f7fa;
    --surface: #ffffff;
    --surface2: #eef0f6;
    --border: #d8dbe8;
    --text: #1a1d27;
    --muted: #636877;
    --accent: #6055d8;
    --accent2: #2563eb;
    --user-bg: #eef2ff;
    --asst-bg: #f5f7fa;
    --tool-bg: #eef0f6;
    --green: #16a34a;
    --grid-color: rgba(0,0,0,0.06);
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
      --grid-color: rgba(0,0,0,0.06);
    }
  }

  /* ── Base styles ────────────────────────────────────────────── */
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 14px; line-height: 1.6; scrollbar-gutter: stable; }
  a { color: var(--accent2); text-decoration: none; }
  a:hover { text-decoration: none; }

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
  .stats-btn { text-decoration: none; }
  .stats-btn:hover { text-decoration: none; }

  /* ── Index ──────────────────────────────────────────────────── */
  .container { max-width: 1100px; margin: 0 auto; padding: 24px; }
  .project-group { margin-bottom: 20px; }
  .project-header { display: flex; align-items: baseline; gap: 10px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }
  .project-name { font-size: 13px; font-weight: 600; color: var(--muted); font-family: monospace; }
  .project-count { font-size: 12px; color: var(--muted); }
  /* ── Session list: shared ──────────────────────────────────── */
  .session-card { background: var(--surface); border: 1px solid var(--border); display: flex; transition: border-color 0.15s, box-shadow 0.15s; cursor: pointer; text-decoration: none; color: inherit; }
  .session-card:hover { border-color: var(--accent); box-shadow: 0 2px 12px rgba(0,0,0,0.15); text-decoration: none; }
  .session-title { font-size: 13px; font-weight: 500; line-height: 1.4; overflow: hidden; }
  .session-meta { display: flex; align-items: center; }
  .badge-msgs { background: var(--surface2); border-radius: 4px; padding: 2px 7px; font-size: 11px; color: var(--muted); }
  .badge-cost { background: var(--surface2); border-radius: 4px; padding: 2px 7px; font-size: 11px; color: var(--green); font-variant-numeric: tabular-nums; }
  .badge-mem { font-size: 11px; color: var(--accent); text-decoration: none; }
  .badge-mem:hover { text-decoration: none; }
  .badge-compact { font-size: 11px; color: var(--muted); }
  .ts { font-size: 11px; color: var(--muted); }

  /* ── Memory ─────────────────────────────────────────────────── */
  .mem-type { border-radius: 3px; padding: 1px 5px; font-size: 10px; font-weight: 700; letter-spacing: 0.4px; text-transform: uppercase; flex-shrink: 0; }
  .mem-type-user      { background: rgba(90,156,245,0.15); color: var(--accent2); }
  .mem-type-feedback  { background: rgba(245,158,11,0.15);  color: #f59e0b; }
  .mem-type-project   { background: rgba(74,222,128,0.15);  color: var(--green); }
  .mem-type-reference { background: rgba(167,139,250,0.15); color: var(--accent); }
  :root[data-theme="light"] .mem-type-feedback { color: #92400e; }
  :root[data-theme="light"] .mem-type-project  { color: #166534; }
  @media (prefers-color-scheme: light) {
    :root[data-theme="system"] .mem-type-feedback { color: #92400e; }
    :root[data-theme="system"] .mem-type-project  { color: #166534; }
  }
  .mem-item { padding: 5px 0; border-bottom: 1px solid var(--border); display: flex; flex-direction: column; gap: 3px; }
  .mem-item-header { display: flex; align-items: center; gap: 6px; }
  .mem-item-name { font-size: 12px; font-weight: 500; }
  .mem-item-desc { font-size: 11px; color: var(--muted); padding-left: 2px; }
  .mem-view-all { display: block; font-size: 11px; color: var(--accent2); margin-top: 8px; }
  /* Memory full page */
  .mem-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; }
  .mem-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  .mem-card-name { font-size: 14px; font-weight: 600; }
  .mem-card-desc { font-size: 12px; color: var(--muted); margin-bottom: 10px; }
  .mem-card-body { font-size: 13px; white-space: pre-wrap; line-height: 1.75; background: var(--surface2); border-radius: 6px; padding: 10px 14px; word-break: break-word; }
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
  .side-section h2 { font-size: 11px; font-weight: 700; letter-spacing: 0.9px; text-transform: uppercase; color: var(--muted); margin-bottom: 8px; }
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

  /* ── Health banner ──────────────────────────────────────────── */
  .health-banner { padding: 10px 24px; font-size: 13px; }
  .health-banner-warning { background: #78350f22; border-bottom: 1px solid #92400e44; color: #92400e; }
  .health-banner-error   { background: #7f1d1d22; border-bottom: 1px solid #991b1b44; color: #991b1b; }
  :root[data-theme="dark"] .health-banner-warning { background: #78350f33; border-color: #92400e66; color: #fbbf24; }
  :root[data-theme="dark"] .health-banner-error   { background: #7f1d1d33; border-color: #991b1b66; color: #f87171; }
  @media (prefers-color-scheme: dark) {
    :root[data-theme="system"] .health-banner-warning { background: #78350f33; border-color: #92400e66; color: #fbbf24; }
    :root[data-theme="system"] .health-banner-error   { background: #7f1d1d33; border-color: #991b1b66; color: #f87171; }
  }
  .health-banner-inner { max-width: 1100px; margin: 0 auto; display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
  .health-banner-icon { flex-shrink: 0; font-size: 15px; }
  .health-banner-messages { flex: 1; display: flex; flex-direction: column; gap: 2px; }
  .health-banner-link { font-size: 12px; font-weight: 600; white-space: nowrap; color: inherit; border: 1px solid currentColor; border-radius: 4px; padding: 2px 8px; opacity: 0.8; }
  .health-banner-link:hover { opacity: 1; text-decoration: none; }
  .health-banner-dismiss { background: none; border: none; cursor: pointer; color: inherit; font-size: 14px; opacity: 0.6; padding: 0 4px; }
  .health-banner-dismiss:hover { opacity: 1; }

  /* ── Health page ────────────────────────────────────────────── */
  .health-card { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; }
  .health-card-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
  .health-status-ok      { color: var(--green); font-size: 16px; }
  .health-status-warning { color: #f59e0b; font-size: 16px; }
  .health-status-error   { color: #ef4444; font-size: 16px; }
  .health-check-label { font-size: 13px; font-weight: 600; }
  .health-check-msg { font-size: 12px; color: var(--muted); margin-top: 2px; }
  .health-check-detail { font-size: 12px; color: var(--muted); margin-top: 4px; font-family: monospace; }
  .health-overall { display: inline-block; padding: 3px 10px; border-radius: 5px; font-size: 13px; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 20px; }
  .health-overall-ok      { background: rgba(74,222,128,0.15); color: var(--green); }
  .health-overall-warning { background: rgba(245,158,11,0.15); color: #f59e0b; }
  .health-overall-error   { background: rgba(239,68,68,0.15);  color: #ef4444; }

  /* ── First-launch modal ─────────────────────────────────────── */
  .modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 24px; }
  .modal-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 28px 32px; max-width: 460px; width: 100%; }
  .modal-box h2 { font-size: 17px; font-weight: 700; margin-bottom: 16px; color: var(--text); }
  .modal-box p { font-size: 13px; color: var(--muted); margin-bottom: 14px; line-height: 1.6; }
  .modal-checklist { list-style: none; margin-bottom: 20px; display: flex; flex-direction: column; gap: 6px; }
  .modal-checklist li { font-size: 13px; color: var(--text); display: flex; align-items: baseline; gap: 8px; }
  .modal-checklist li::before { content: "✓"; color: var(--green); font-weight: 700; flex-shrink: 0; }
  .modal-actions { display: flex; gap: 10px; }
  .modal-btn-primary { background: var(--accent); color: #fff; border: none; border-radius: 6px; padding: 8px 18px; font-size: 13px; font-weight: 600; cursor: pointer; }
  .modal-btn-primary:hover { opacity: 0.9; }
  .modal-btn-link { background: none; border: none; color: var(--accent2); font-size: 13px; cursor: pointer; padding: 8px 4px; }
  .modal-btn-link:hover { text-decoration: underline; }
</style>
</head>
<body>
<nav class="nav">
  <div class="nav-inner">
    <a class="nav-brand" href="/">claudio<span>.app</span></a>
    {% block nav_extra %}{% endblock %}
    <div class="nav-spacer"></div>
    <a class="theme-btn" href="/export/sessions.json" download title="Export all sessions as JSON">↓ export</a>
    <button class="theme-btn" id="layout-btn" title="Toggle layout" onclick="cycleLayout()">
      <span id="layout-icon">≡</span>
      <span id="layout-label">rows</span>
    </button>
    <button class="theme-btn" id="theme-btn" title="Toggle theme" onclick="cycleTheme()">
      <span id="theme-icon">💻</span>
      <span id="theme-label">system</span>
    </button>
    <a class="theme-btn stats-btn" href="{{ url_for('stats') }}" title="Usage statistics">{{ pie_icon(13) }} stats</a>
    <a class="github-btn" href="https://github.com/shahfazal/claudio" target="_blank" rel="noopener noreferrer" title="View on GitHub">
      <svg viewBox="0 0 16 16" width="16" height="16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
    </a>
  </div>
</nav>
{% if health and health.status in ('warning', 'error') %}
<div class="health-banner health-banner-{{ health.status }}" role="alert" aria-live="polite" id="health-banner">
  <div class="health-banner-inner">
    <span class="health-banner-icon">{% if health.status == 'error' %}❌{% else %}⚠️{% endif %}</span>
    <div class="health-banner-messages">
      {% for key, check in health.checks.items() %}{% if not check.ok %}<div>{{ check.message }}</div>{% endif %}{% endfor %}
    </div>
    <a class="health-banner-link" href="/health">Details</a>
    <button class="health-banner-dismiss" onclick="document.getElementById('health-banner').remove()" aria-label="Dismiss">✕</button>
  </div>
</div>
{% endif %}
<main>{% block body %}{% endblock %}</main>

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

document.addEventListener('click', e => {
  const el = e.target.closest('[data-path]');
  if (!el) return;
  // navigator.clipboard requires a secure context (HTTPS or localhost).
  // Fail silently if unavailable: no false "Copied!" tooltip.
  navigator.clipboard.writeText(el.dataset.path)
    .then(() => showCopyTip(el))
    .catch(() => {});
});

// ── First-launch modal ────────────────────────────────────────
(function () {
  const KEY = 'claudio-first-launch-acknowledged';
  if (localStorage.getItem(KEY)) return;
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.id = 'first-launch-modal';
  overlay.innerHTML = `
    <div class="modal-box" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <h2 id="modal-title">Welcome to Claudio v0.4</h2>
      <p>Claudio reads local Claude Code session files from <code style="font-size:12px;background:var(--surface2);padding:1px 5px;border-radius:3px">~/.claude/</code>. This is fragile, it may break if Claude Code updates its file format.</p>
      <ul class="modal-checklist">
        <li>Health check runs on every page load</li>
        <li>Export saves your session data as portable JSON</li>
        <li>Pricing config lives in ~/.claudio/pricing.json. Edit this file to update rates.</li>
      </ul>
      <div class="modal-actions">
        <button class="modal-btn-primary" onclick="dismissModal()">I Understand</button>
        <a class="modal-btn-link" href="/health" onclick="localStorage.setItem('claudio-first-launch-acknowledged','true')">View Health Status</a>
      </div>
    </div>`;
  document.body.appendChild(overlay);
  window.dismissModal = function () {
    localStorage.setItem(KEY, 'true');
    document.getElementById('first-launch-modal').remove();
  };
})();
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
      {% if group.memory_count %}<a class="badge-mem" href="{{ url_for('project_memory', project_slug=group.slug) }}">{{ brain_icon(11) }} {{ group.memory_count }} memor{{ 'ies' if group.memory_count != 1 else 'y' }}</a>{% endif %}
      {%- set total_compact = group.sessions | map(attribute='compact_count') | map('default', 0) | sum %}
      {% if total_compact %}<span class="badge-compact" title="Total compactions across all sessions">{{ archive_icon(11) }} {{ total_compact }} compaction{{ 's' if total_compact != 1 }}</span>{% endif %}
    </div>
    <div class="session-list">
      {% for s in group.sessions %}
      <a class="session-card"
         href="{{ url_for('session_view', session_id=s.session_id) }}"
         data-title="{{ s.title | lower }}"
         data-raw-title="{{ s.title }}">
        <span class="session-title">{{ s.title }}</span>
        <div class="session-meta">
          <span class="badge-msgs">{{ s.message_count }} msg{{ 's' if s.message_count != 1 }}</span>
          {% if s.cost_unknown %}<span class="badge-cost" style="color:var(--muted)">≈ ?</span>
          {% elif s.cost_usd %}<span class="badge-cost">{{ fmt_cost(s.cost_usd) }}</span>{% endif %}
          <span class="ts">{{ fmt_ts(s.started_at) }}</span>
          <span class="meta-compact">{{ s.message_count }} msg{{ 's' if s.message_count != 1 }}{% if s.cost_unknown %} · ≈ ?{% elif s.cost_usd %} · {{ fmt_cost(s.cost_usd) }}{% endif %}{% if s.compact_count %} · {{ archive_icon(10) }} {{ s.compact_count }}×{% endif %}{% if s.started_at %} · {{ fmt_ts(s.started_at) }}{% endif %}</span>
        </div>
      </a>
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
    // highlight() calls esc() on all user content before inserting <mark> tags. XSS safe.
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
{% block title %}{{ title }} - claudio{% endblock %}
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
    {% if session.compact_count %}<span title="Times this session was compacted">{{ archive_icon(12) }} compacted {{ session.compact_count }}×</span>{% endif %}
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

    {% if memory.files %}
    <div class="side-section">
      <h2>{{ brain_icon(11) }} Memory ({{ memory.files | length }})</h2>
      {% for m in memory.files %}
      <div class="mem-item">
        <div class="mem-item-header">
          {% if m.type %}<span class="mem-type mem-type-{{ m.type }}">{{ m.type }}</span>{% endif %}
          <span class="mem-item-name">{{ m.name }}</span>
        </div>
        {% if m.description %}<div class="mem-item-desc">{{ m.description }}</div>{% endif %}
      </div>
      {% endfor %}
      <a class="mem-view-all" href="{{ url_for('project_memory', project_slug=session.project_slug) }}">View full memory →</a>
    </div>
    {% endif %}

    {% if todos %}
    <div class="side-section">
      <h2>Todos ({{ todos | length }})</h2>
      {% for todo in todos %}
      <div class="todo-item {{ 'done' if todo.status == 'completed' else '' }}">
        <span class="todo-dot status-{{ todo.status }}"></span>{{ todo.content }}
      </div>
      {% endfor %}
    </div>
    {% endif %}

    {% if history %}
    <div class="side-section">
      <h2>Command history</h2>
      {% for h in history[:50] %}{% if h.display %}
      <div class="history-item" title="{{ h.display }}">{{ h.display }}</div>
      {% endif %}{% endfor %}
    </div>
    {% endif %}
  </div>
</div>
{% endblock %}
"""

MEMORY_TMPL = """\
{% extends "base.html" %}
{% block title %}memory - claudio{% endblock %}
{% block nav_extra %}
<a href="{{ url_for('index') }}" style="font-size:13px;color:var(--muted)">← all sessions</a>
{% endblock %}

{% block body %}
<div class="session-hdr">
  <h1>Project Memory</h1>
  <div class="session-hdr-meta">
    <span>📁 {{ label }}</span>
    <span>{{ brain_icon(13) }} {{ memory.count }} memor{{ 'ies' if memory.count != 1 else 'y' }}</span>
  </div>
</div>

<div class="container" style="max-width:860px;padding-top:24px">
  {% for m in memory.files %}
  <div class="mem-card">
    <div class="mem-card-header">
      {% if m.type %}<span class="mem-type mem-type-{{ m.type }}">{{ m.type }}</span>{% endif %}
      <span class="mem-card-name">{{ m.name }}</span>
    </div>
    {% if m.description %}<div class="mem-card-desc">{{ m.description }}</div>{% endif %}
    {% if m.body %}<div class="mem-card-body">{{ m.body }}</div>{% endif %}
  </div>
  {% endfor %}

  {% if not memory.files %}
  <p style="color:var(--muted);font-size:13px">No memory files found for this project.</p>
  {% endif %}
</div>
{% endblock %}
"""

HEALTH_TMPL = """\
{% extends "base.html" %}
{% block title %}Health — Claudio{% endblock %}
{% block nav_extra %}
<a href="{{ url_for('index') }}" style="font-size:13px;color:var(--muted)">← all sessions</a>
{% endblock %}

{% block body %}
<div class="container" style="max-width:860px;padding-top:24px">
  <h1 style="font-size:20px;font-weight:700;margin-bottom:8px">Claudio Health Status</h1>
  <span class="health-overall health-overall-{{ health.status }}">{{ health.status.upper() }}</span>

  {% set check = health.checks.claude_dir %}
  <div class="health-card">
    <div class="health-card-header">
      <span class="health-status-{{ 'ok' if check.ok else 'error' }}">{{ '✓' if check.ok else '✗' }}</span>
      <span class="health-check-label">Claude Directory</span>
    </div>
    <div class="health-check-msg">{{ check.message }}</div>
    {% if check.missing %}
    <div class="health-check-detail">Missing: {{ check.missing | join(', ') }}</div>
    {% endif %}
  </div>

  {% set check = health.checks.schema %}
  <div class="health-card">
    <div class="health-card-header">
      <span class="health-status-{{ 'ok' if check.ok else 'error' }}">{{ '✓' if check.ok else '✗' }}</span>
      <span class="health-check-label">Session Schema</span>
    </div>
    <div class="health-check-msg">{{ check.message }}</div>
    {% if check.total_count %}
    <div class="health-check-detail">Sessions found: {{ check.total_count }}</div>
    {% endif %}
  </div>

  {% set check = health.checks.pricing %}
  <div class="health-card">
    <div class="health-card-header">
      <span class="health-status-{{ 'ok' if check.ok else 'warning' }}">{{ '✓' if check.ok else '⚠' }}</span>
      <span class="health-check-label">Pricing Configuration</span>
    </div>
    <div class="health-check-msg">{{ check.message }}</div>
    {% if check.last_updated %}
    <div class="health-check-detail">Last updated: {{ check.last_updated }}{% if check.days_old is not none %} ({{ check.days_old }} days ago){% endif %}</div>
    {% endif %}
  </div>

  <div style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap">
    <a href="https://github.com/shahfazal/claudio/issues" target="_blank" rel="noopener noreferrer"
       style="font-size:12px;color:var(--accent2)">Report compatibility issue →</a>
    <a href="https://www.anthropic.com/pricing" target="_blank" rel="noopener noreferrer"
       style="font-size:12px;color:var(--accent2)">Check Anthropic pricing →</a>
  </div>
</div>{% endblock %}
"""

STATS_TMPL = """\
{% extends "base.html" %}
{% block title %}stats - claudio{% endblock %}
{% block nav_extra %}
<a href="{{ url_for('index') }}" style="font-size:13px;color:var(--muted)">← all sessions</a>
{% endblock %}

{% block body %}
<style>
  .stats-container { max-width: 1100px; margin: 0 auto; padding: 16px 24px; }

  /* Stats cards row -- centered */
  .stats-summary { display: flex; gap: 16px; margin-bottom: 0; flex-wrap: wrap; justify-content: center; }
  .stat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px 24px; min-width: 140px; }
  .stat-value { font-size: 24px; font-weight: 700; color: var(--text); font-variant-numeric: tabular-nums; }
  .stat-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; margin-top: 4px; }

  /* Filter card (5th card, behaves as toggle button) */
  .filter-card { cursor: pointer; text-align: center; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px 24px; min-width: 140px; font-family: inherit; transition: border-color 0.15s; }
  .filter-card:hover { border-color: var(--accent); }
  .filter-card[aria-expanded="true"] { border-color: var(--accent); }
  .filter-card-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; }
  .filter-chevron { font-size: 14px; color: var(--muted); transition: transform 0.2s; display: block; }
  .filter-card[aria-expanded="true"] .filter-chevron { transform: rotate(180deg); }

  /*
   * Filter panel slide-open animation.
   *
   * `display` cannot be transitioned, so the panel stays as `display:flex`
   * at all times. Hiding is achieved with `max-height:0` + `overflow:hidden`
   * + `opacity:0`. Opening animates to a generous `max-height` ceiling
   * (300px) so the transition runs against a known value -- the actual panel
   * height is shorter, which is fine. If the panel content ever grows past
   * 300px this value must be increased.
   *
   * `padding` and `margin-top` are co-animated so the panel doesn't appear
   * to "jump" off the cards when it opens.
   */
  .filter-panel { position: relative; display: flex; gap: 32px; flex-wrap: wrap; align-items: flex-start; background: var(--surface); border: 1px solid transparent; border-radius: 10px; padding: 0 24px; margin-top: 0; max-height: 0; overflow: hidden; opacity: 0; transition: max-height 0.28s ease, opacity 0.2s ease, padding 0.28s ease, margin-top 0.28s ease, border-color 0.2s ease; }
  .filter-panel.is-open { max-height: 300px; opacity: 1; padding: 20px 24px; margin-top: 12px; border-color: var(--border); }
  .filter-close { position: absolute; top: 10px; right: 12px; background: none; border: none; cursor: pointer; color: var(--muted); display: flex; flex-direction: column; align-items: center; gap: 1px; padding: 2px 4px; font-family: inherit; transition: color 0.15s; }
  .filter-close:hover { color: var(--text); }
  .filter-close-x { font-size: 16px; line-height: 1; }
  .filter-close-hint { font-size: 9px; text-transform: uppercase; letter-spacing: 0.4px; }
  .filter-section { display: flex; flex-direction: column; gap: 10px; }
  .filter-section-label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; }
  .preset-row { display: flex; gap: 8px; flex-wrap: wrap; }
  .preset-btn { background: transparent; border: 1px solid var(--border); border-radius: 20px; color: var(--muted); cursor: pointer; font-size: 12px; padding: 4px 14px; font-family: inherit; transition: border-color 0.15s, color 0.15s, background 0.15s; }
  .preset-btn:hover { border-color: var(--accent); color: var(--accent); }
  .preset-btn[aria-checked="true"] { background: var(--accent); border-color: var(--accent); color: var(--bg); font-weight: 600; }
  .custom-range-form { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .custom-range-form label { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; }
  .custom-range-form input[type=date] { background: var(--surface2); border: 1px solid var(--border); border-radius: 6px; color: var(--text); font-size: 12px; padding: 4px 8px; outline: none; transition: border-color 0.15s; font-family: inherit; color-scheme: dark; }
  .custom-range-form input[type=date]:focus { border-color: var(--accent); }
  .custom-range-form input[type=date]::-webkit-calendar-picker-indicator { filter: invert(0.5); cursor: pointer; }
  :root[data-theme="light"] .custom-range-form input[type=date] { color-scheme: light; }
  @media (prefers-color-scheme: light) { :root[data-theme="system"] .custom-range-form input[type=date] { color-scheme: light; } }
  .apply-btn { background: var(--accent); border: 1px solid var(--accent); border-radius: 4px; color: var(--bg); cursor: pointer; font-size: 11px; padding: 4px 12px; font-family: inherit; transition: opacity 0.15s; font-weight: 600; }
  .apply-btn:hover:not(:disabled) { opacity: 0.85; }
  .apply-btn:disabled { opacity: 0.35; cursor: not-allowed; }
  .filter-error { font-size: 12px; color: #e05252; margin-top: 6px; }

  /* Heatmap hero */
  .heatmap-card { margin-top: 18px; margin-bottom: 14px; overflow-x: auto; }

  /* Empty state overlay */
  .cost-grid-wrap { position: relative; }
  .cost-grid-blur, .ghost-blur { filter: blur(4px); pointer-events: none; user-select: none; opacity: 0.5; }
  .empty-overlay { position: absolute; inset: 0; z-index: 10; display: flex; align-items: center; justify-content: center; }
  .empty-msg { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px 32px; font-size: 13px; color: var(--muted); box-shadow: 0 8px 32px rgba(0,0,0,0.3); }

  /* Cost charts 2-column */
  .cost-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
  .chart-card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px 20px; min-height: 140px; }
  .chart-card h2 { font-size: 12px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase; color: var(--muted); margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
  .range-btn { background: var(--surface2); border: 1px solid var(--border); border-radius: 4px; color: var(--muted); cursor: pointer; font-size: 11px; padding: 2px 8px; font-family: inherit; transition: border-color 0.15s, color 0.15s, background 0.15s; }
  .range-btn:hover { border-color: var(--accent); color: var(--accent); }
  .range-btn.active { background: var(--accent); border-color: var(--accent); color: var(--bg); font-weight: 600; }
  .chart-empty { color: var(--muted); font-size: 12px; padding: 20px 0; }
  .heat-tooltip { position: fixed; background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px; font-size: 11px; color: var(--text); pointer-events: none; z-index: 1000; line-height: 1.5; opacity: 0; transition: opacity 0.1s; }

  @media (max-width: 700px) { .cost-grid { grid-template-columns: 1fr; } }
</style>

<div class="stats-container">

  <!-- Stats cards (centered) + filter toggle -->
  <div class="stats-summary">
    <div class="stat-card">
      <div class="stat-value">{{ total_sessions }}</div>
      <div class="stat-label">sessions</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ fmt_cost(total_cost) if total_cost else '-' }}</div>
      <div class="stat-label">total cost</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ fmt_cost(avg_cost) if avg_cost else '-' }}</div>
      <div class="stat-label">avg cost / session</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">{{ total_messages }}</div>
      <div class="stat-label">messages</div>
    </div>
    <button class="filter-card" id="filterToggle"
            aria-expanded="false" aria-controls="filterPanel">
      <span class="filter-card-label">filter</span>
      <span class="filter-chevron" aria-hidden="true">&#9662;</span>
    </button>
  </div>

  <!-- Filter panel (hidden by default, opened by filter card) -->
  <div id="filterPanel" class="filter-panel"
       role="region" aria-label="Date filter">
    <button class="filter-close" id="filterClose" aria-label="Close filter panel">
      <span class="filter-close-x">&#215;</span>
      <span class="filter-close-hint">esc</span>
    </button>
    <div class="filter-section">
      <div class="filter-section-label">Quick filter</div>
      <div class="preset-row" role="radiogroup" aria-label="Date preset">
        <button class="preset-btn" role="radio" aria-checked="false" data-preset="all">All time</button>
        <button class="preset-btn" role="radio" aria-checked="false" data-preset="7">Last 7 days</button>
        <button class="preset-btn" role="radio" aria-checked="false" data-preset="30">Last 30 days</button>
        <button class="preset-btn" role="radio" aria-checked="false" data-preset="90">Last 90 days</button>
      </div>
    </div>
    <div class="filter-section">
      <div class="filter-section-label">Custom range</div>
      <form class="custom-range-form" method="get"
            action="{{ url_for('stats') }}" id="customRangeForm">
        <label for="from-date">from</label>
        <input type="date" id="from-date" name="from" value="{{ from_str }}">
        <label for="to-date">to</label>
        <input type="date" id="to-date" name="to" value="{{ to_str }}">
        <button type="submit" class="apply-btn" id="applyBtn" disabled>apply</button>
      </form>
      <div role="alert" class="filter-error" id="filterError" hidden></div>
    </div>
  </div>

  <!-- Activity heatmap (hero, full width) -->
  {% if total_sessions > 0 or ghost_payload %}
  <div class="chart-card heatmap-card{% if total_sessions == 0 %} ghost-blur{% endif %}">
    <h2>Activity heatmap</h2>
    {% if total_sessions > 0 %}
    <div style="display:flex;justify-content:center;margin-bottom:12px">
      <span class="range-group">
        <button class="heat-btn range-btn active" data-mode="cost">cost</button>
        <button class="heat-btn range-btn" data-mode="count">sessions</button>
        <button class="heat-btn range-btn" data-mode="both">both</button>
      </span>
    </div>
    {% endif %}
    <div id="heatmapChart" role="img" aria-label="Activity heatmap"></div>
  </div>
  {% endif %}

  <!-- Cost charts (2-column grid) -->
  <div class="cost-grid-wrap">
    {% if total_sessions == 0 %}
    <div class="empty-overlay">
      <div class="empty-msg">No session data for this period.</div>
    </div>
    {% endif %}
    <div class="cost-grid{% if total_sessions == 0 %} cost-grid-blur{% endif %}">

      <div class="chart-card">
        <h2>Cost by project</h2>
        {% if total_sessions > 0 and payload.by_project %}
        <canvas id="projectChart" aria-label="Cost by project bar chart"></canvas>
        {% elif total_sessions > 0 %}
        <p class="chart-empty">No cost data available.</p>
        {% elif ghost_payload and ghost_payload.by_project %}
        <canvas id="projectChart" aria-label="Cost by project bar chart"></canvas>
        {% endif %}
      </div>

      <div class="chart-card">
        <h2>Top sessions by cost
          {% if total_sessions > 0 %}
          <button id="costToggle" class="range-btn" style="margin-left:auto">show all</button>
          {% endif %}
        </h2>
        {% if total_sessions > 0 and payload.top_by_cost %}
        <canvas id="costChart" aria-label="Top sessions by cost bar chart"></canvas>
        {% elif total_sessions > 0 %}
        <p class="chart-empty">No cost data available.</p>
        {% elif ghost_payload and ghost_payload.top_by_cost %}
        <canvas id="costChart" aria-label="Top sessions by cost bar chart"></canvas>
        {% endif %}
      </div>

    </div>
  </div>

</div>

<!-- Filter panel JS (always loaded, independent of session count) -->
<script>(function () {
  var toggle   = document.getElementById('filterToggle');
  var panel    = document.getElementById('filterPanel');
  var errBox   = document.getElementById('filterError');
  var fromEl   = document.getElementById('from-date');
  var toEl     = document.getElementById('to-date');
  var applyBtn = document.getElementById('applyBtn');
  var FROM_STR = '{{ from_str }}';
  var TO_STR   = '{{ to_str }}';

  function isOpen() { return panel.classList.contains('is-open'); }
  function openPanel()  {
    panel.classList.add('is-open');
    toggle.setAttribute('aria-expanded', 'true');
  }
  function closePanel() {
    panel.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
    toggle.focus();
  }

  toggle.addEventListener('click', function () {
    if (isOpen()) closePanel(); else openPanel();
  });

  document.addEventListener('click', function (e) {
    if (isOpen() && !panel.contains(e.target) && e.target !== toggle) closePanel();
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && isOpen()) { e.stopPropagation(); closePanel(); }
  });

  /* Preset buttons */
  var presets = Array.prototype.slice.call(document.querySelectorAll('.preset-btn'));

  // Uses local date components rather than toISOString() (which gives UTC
  // midnight and can produce the wrong date in timezones behind UTC).
  function padded(d) {
    var mm = d.getMonth() + 1, dd = d.getDate();
    return d.getFullYear() + '-' + (mm < 10 ? '0' : '') + mm + '-' + (dd < 10 ? '0' : '') + dd;
  }

  function detectPreset() {
    if (!FROM_STR && !TO_STR) return 'all';
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var days = [7, 30, 90];
    for (var i = 0; i < days.length; i++) {
      var from = new Date(today);
      from.setDate(from.getDate() - days[i]);
      if (FROM_STR === padded(from) && TO_STR === padded(today)) return String(days[i]);
    }
    return 'custom';
  }

  var activePreset = detectPreset();
  presets.forEach(function (btn) {
    btn.setAttribute('aria-checked', btn.dataset.preset === activePreset ? 'true' : 'false');
  });

  presets.forEach(function (btn) {
    btn.addEventListener('click', function () {
      presets.forEach(function (b) { b.setAttribute('aria-checked', 'false'); });
      btn.setAttribute('aria-checked', 'true');

      var preset = btn.dataset.preset;
      var url = '/stats';
      if (preset !== 'all') {
        var today = new Date(); today.setHours(0, 0, 0, 0);
        var from  = new Date(today); from.setDate(from.getDate() - parseInt(preset, 10));
        url = '/stats?from=' + padded(from) + '&to=' + padded(today);
      }
      sessionStorage.setItem('claudio.fpOpen', '1');
      setTimeout(function () { window.location.href = url; }, 300);
    });
  });

  /* Custom range form */
  function checkApply() {
    applyBtn.disabled = !fromEl.value || !toEl.value;
  }
  fromEl.addEventListener('input', function () { errBox.hidden = true; checkApply(); });
  toEl.addEventListener('input',   function () { errBox.hidden = true; checkApply(); });
  checkApply();

  /* Open native date picker on full-field click, not just the calendar icon */
  [fromEl, toEl].forEach(function (el) {
    el.addEventListener('click', function () { try { el.showPicker(); } catch (e) {} });
  });

  document.getElementById('customRangeForm').addEventListener('submit', function (e) {
    if (fromEl.value && toEl.value && fromEl.value > toEl.value) {
      e.preventDefault();
      errBox.textContent = 'Start date must be before end date';
      errBox.hidden = false;
      return;
    }
    sessionStorage.setItem('claudio.fpOpen', '1');
  });

  document.getElementById('filterClose').addEventListener('click', closePanel);

  /* Reopen panel if it was open before a filter navigation, or a custom range is active */
  if (FROM_STR || TO_STR || sessionStorage.getItem('claudio.fpOpen')) {
    sessionStorage.removeItem('claudio.fpOpen');
    openPanel();
  }
})();
</script>

{% if total_sessions > 0 or ghost_payload %}
<script src="{{ url_for('static', filename='js/chart.umd.min.js') }}"></script>
<script src="{{ url_for('static', filename='js/d3.min.js') }}"></script>
<script>
const PAYLOAD = {{ (payload if total_sessions > 0 else ghost_payload) | tojson }};

function cssVar(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }

// Theme-sensitive vars -- re-read on each theme change
let _accent, _accent2, _muted, _text, _border, _fillAlpha, _gridColor;
function readVars() {
  _accent    = cssVar('--accent');
  _accent2   = cssVar('--accent2');
  _muted     = cssVar('--muted');
  _text      = cssVar('--text');
  _border    = cssVar('--border');
  _gridColor = cssVar('--grid-color');
  const th   = document.documentElement.dataset.theme;
  const light = th === 'light' || (th === 'system' && window.matchMedia('(prefers-color-scheme: light)').matches);
  // Appended as two hex digits to a 6-digit hex accent color (#rrggbbaa).
  // This requires all --accent/--accent2 values to be 6-digit hex strings.
  _fillAlpha = light ? '66' : 'bb';
}
readVars();

Chart.defaults.color = _muted;
Chart.defaults.borderColor = _gridColor;
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif';
Chart.defaults.font.size = 11;

// Chart instances (module-level so the theme observer can update them)
let projectChartInst, costChartInst;

// ── Cost by project ───────────────────────────────────────────
if (document.getElementById('projectChart')) {
  projectChartInst = new Chart(document.getElementById('projectChart'), {
    type: 'bar',
    data: {
      labels: PAYLOAD.by_project.map(p => p.label),
      datasets: [{ data: PAYLOAD.by_project.map(p => p.cost_usd), backgroundColor: _accent2 + _fillAlpha, borderColor: _accent2, borderWidth: 1 }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: items => PAYLOAD.by_project[items[0].dataIndex].label,
            label: item => {
              const p = PAYLOAD.by_project[item.dataIndex];
              return ['$' + item.raw.toFixed(4), p.count + ' session' + (p.count === 1 ? '' : 's')];
            }
          }
        }
      },
      scales: {
        x: { grid: { color: _gridColor }, beginAtZero: true, ticks: { callback: v => '$' + v.toFixed(2) } },
        y: { grid: { display: false } }
      }
    }
  });
}

// ── Top sessions by cost ──────────────────────────────────────
if (document.getElementById('costChart')) {
  let showAll = false;
  function renderCost(all) {
    const items = all ? PAYLOAD.top_by_cost : PAYLOAD.top_by_cost.slice(0, 10);
    const labels = items.map(s => s.title.length > 40 ? s.title.slice(0, 40) + '\u2026' : s.title);
    if (costChartInst) costChartInst.destroy();
    costChartInst = new Chart(document.getElementById('costChart'), {
      type: 'bar',
      data: { labels, datasets: [{ data: items.map(s => s.cost_usd), backgroundColor: _accent + _fillAlpha, borderColor: _accent, borderWidth: 1 }] },
      options: {
        indexAxis: 'y',
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: ctxItems => items[ctxItems[0].dataIndex].title,
              label: item => '$' + item.raw.toFixed(4)
            }
          }
        },
        scales: {
          x: { grid: { color: _gridColor }, beginAtZero: true, ticks: { callback: v => '$' + v.toFixed(2) } },
          y: { grid: { display: false } }
        },
        onClick: (event, elements) => {
          if (elements.length > 0) {
            window.location.href = '/session/' + items[elements[0].index].session_id;
          }
        },
        onHover: (event, elements) => {
          event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
        }
      }
    });
  }
  renderCost(false);
  const toggle = document.getElementById('costToggle');
  if (PAYLOAD.top_by_cost.length <= 10) {
    toggle.style.display = 'none';
  } else {
    toggle.addEventListener('click', () => {
      showAll = !showAll;
      toggle.textContent = showAll ? 'top 10' : 'show all';
      renderCost(showAll);
    });
  }
}

// ── Activity heatmap (D3) ─────────────────────────────────────
let repaintHeatmap;
(function () {
  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const CELL = 24, GAP = 3, COLS = 24, ROWS = 7;
  const M = { top: 26, right: 20, bottom: 10, left: 50 };

  const matrix = {};
  PAYLOAD.sessions_raw.forEach(s => {
    if (!s.ts_ms) return;
    const d = new Date(s.ts_ms);
    const hour = d.getHours();
    const jsDay = d.getDay();
    const day = jsDay === 0 ? 6 : jsDay - 1;
    const key = day + '-' + hour;
    if (!matrix[key]) matrix[key] = { count: 0, cost: 0 };
    matrix[key].count++;
    matrix[key].cost += s.cost_usd || 0;
  });

  const cells = [];
  for (let day = 0; day < ROWS; day++) {
    for (let hour = 0; hour < COLS; hour++) {
      const m = matrix[day + '-' + hour] || { count: 0, cost: 0 };
      cells.push({ day, hour, count: m.count, cost: m.cost });
    }
  }

  const costMax  = d3.max(cells, d => d.cost)  || 1;
  const countMax = d3.max(cells, d => d.count) || 1;

  let costScale  = d3.scaleSequentialPow().exponent(0.4).domain([0, costMax]);
  let countScale = d3.scaleSequentialPow().exponent(0.4).domain([0, countMax]);

  function buildScales() {
    const s2 = cssVar('--surface2');
    costScale.interpolator(d3.interpolate(s2, cssVar('--accent2')));
    countScale.interpolator(d3.interpolate(s2, cssVar('--accent')));
  }
  buildScales();

  const svgW = M.left + COLS * (CELL + GAP) - GAP + M.right;
  const svgH = M.top  + ROWS * (CELL + GAP) - GAP + M.bottom;

  const svg = d3.select('#heatmapChart')
    .append('svg')
    .attr('width', svgW)
    .attr('height', svgH)
    .style('display', 'block')
    .style('margin', '0 auto');

  const g = svg.append('g')
    .attr('transform', 'translate(' + M.left + ',' + M.top + ')');

  const xlabels = g.selectAll('.hlx')
    .data(d3.range(0, 24, 2))
    .join('text')
    .attr('class', 'hlx')
    .attr('x', d => d * (CELL + GAP) + CELL / 2)
    .attr('y', -8)
    .attr('text-anchor', 'middle')
    .attr('font-size', 10)
    .attr('fill', _muted)
    .text(d => d + 'h');

  const ylabels = g.selectAll('.hly')
    .data(DAYS)
    .join('text')
    .attr('class', 'hly')
    .attr('x', -8)
    .attr('y', (d, i) => i * (CELL + GAP) + CELL / 2)
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'middle')
    .attr('font-size', 10)
    .attr('fill', _muted)
    .text(d => d);

  const tip = d3.select('body').append('div').attr('class', 'heat-tooltip');

  let heatMode = 'cost';

  const cellSel = g.selectAll('.hcell')
    .data(cells)
    .join('rect')
    .attr('class', 'hcell')
    .attr('x', d => d.hour * (CELL + GAP))
    .attr('y', d => d.day  * (CELL + GAP))
    .attr('width', CELL)
    .attr('height', CELL)
    .attr('rx', 3)
    .attr('stroke', _border)
    .attr('stroke-width', 0.5)
    .on('mouseover', function (event, d) {
      let val;
      if (heatMode === 'both') {
        val = '$' + d.cost.toFixed(4) + ' &nbsp;&middot;&nbsp; ' + d.count + ' session' + (d.count !== 1 ? 's' : '');
      } else if (heatMode === 'cost') {
        val = '$' + d.cost.toFixed(4);
      } else {
        val = d.count + ' session' + (d.count !== 1 ? 's' : '');
      }
      tip.style('opacity', 1)
         .html(DAYS[d.day] + ' ' + d.hour + 'h &nbsp;&middot;&nbsp; ' + val);
    })
    .on('mousemove', function (event) {
      tip.style('left', (event.clientX + 14) + 'px')
         .style('top',  (event.clientY - 36) + 'px');
    })
    .on('mouseout', function () { tip.style('opacity', 0); });

  const labelSel = g.selectAll('.hclabel')
    .data(cells)
    .join('text')
    .attr('class', 'hclabel')
    .attr('x', d => d.hour * (CELL + GAP) + CELL / 2)
    .attr('y', d => d.day  * (CELL + GAP) + CELL / 2)
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .attr('font-size', 9)
    .attr('fill', _text)
    .attr('pointer-events', 'none')
    .style('opacity', 0)
    .text(d => d.count > 0 ? d.count : '');

  function paintCells(mode) {
    const s2 = cssVar('--surface2');
    if (mode === 'both') {
      cellSel.attr('fill', d => d.cost > 0 ? costScale(d.cost) : s2);
      labelSel.style('opacity', d => d.count > 0 ? 1 : 0);
    } else {
      const scale = mode === 'cost' ? costScale : countScale;
      cellSel.attr('fill', d => d[mode] > 0 ? scale(d[mode]) : s2);
      labelSel.style('opacity', 0);
    }
  }

  paintCells(heatMode);

  document.querySelectorAll('.heat-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      heatMode = btn.dataset.mode;
      document.querySelectorAll('.heat-btn').forEach(b =>
        b.classList.toggle('active', b.dataset.mode === heatMode)
      );
      paintCells(heatMode);
    });
  });

  repaintHeatmap = function () {
    buildScales();
    xlabels.attr('fill', cssVar('--muted'));
    ylabels.attr('fill', cssVar('--muted'));
    cellSel.attr('stroke', cssVar('--border'));
    labelSel.attr('fill', cssVar('--text'));
    paintCells(heatMode);
  };
})();

// ── Theme observer: update charts + heatmap on theme toggle ──
new MutationObserver(() => {
  readVars();
  Chart.defaults.color = _muted;
  Chart.defaults.borderColor = _gridColor;

  function retheme(chart, bgColor, borderColor) {
    if (!chart) return;
    chart.data.datasets.forEach(ds => {
      ds.backgroundColor = bgColor;
      ds.borderColor = borderColor;
    });
    if (chart.options.scales) {
      Object.values(chart.options.scales).forEach(s => {
        if (s.grid && s.grid.color !== undefined) s.grid.color = _gridColor;
      });
    }
    chart.update('none');
  }

  retheme(projectChartInst, _accent2 + _fillAlpha, _accent2);
  retheme(costChartInst,    _accent  + _fillAlpha, _accent);

  if (repaintHeatmap) repaintHeatmap();
}).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
</script>
{% endif %}
{% endblock %}
"""

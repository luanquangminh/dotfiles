#!/usr/bin/env python3
"""Claude Code status line: claude-hud plugin + service status line + aligned gauges.

Reads the official statusline JSON on stdin (code.claude.com/docs/en/statusline), runs the
newest installed claude-hud plugin for the header and activity lines, then inserts:
  line 2   ● Claude ok · All Systems Operational          (status.claude.com, cached 5 min)
  gauges   Context / Session (5h) / Weekly (7d) / Spend   (20-cell bars, threshold colors)
Any failure falls back to the plugin's own output. Never blocks on the network.
"""
import glob, json, os, re, subprocess, sys, time

HOME = os.path.expanduser("~")
CACHE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "claude-hud-status.json")
STATUS_URL = "https://status.claude.com/api/v2/status.json"
BAR = 20
C = {  # Tokyo Night
    "ctx": "#7aa2f7", "use": "#bb9af7", "warn": "#e0af68", "crit": "#f7768e",
    "ok": "#9ece6a", "info": "#7dcfff", "empty": "#3b4261", "label": "#565f89", "text": "#a9b1d6",
}
RESET, DIM, BOLD = "\x1b[0m", "\x1b[2m", "\x1b[1m"
CONFIG_SRC = os.path.join(HOME, ".config/claude-hud/config.json")   # tracked in dotfiles
CONFIG_DST = os.path.join(os.environ.get("CLAUDE_CONFIG_DIR", os.path.join(HOME, ".claude")),
                          "plugins/claude-hud/config.json")          # what the plugin reads


def sync_config():
    """The plugin opens its config with O_NOFOLLOW, so a dotfiles symlink is ignored.
    Keep the real file equal to the tracked source instead."""
    try:
        with open(CONFIG_SRC) as f:
            want = f.read()
        if os.path.islink(CONFIG_DST):
            os.unlink(CONFIG_DST)
        have = open(CONFIG_DST).read() if os.path.exists(CONFIG_DST) else None
        if have != want:
            os.makedirs(os.path.dirname(CONFIG_DST), exist_ok=True)
            with open(CONFIG_DST, "w") as f:
                f.write(want)
    except Exception:
        pass


def fg(hex_):
    r, g, b = int(hex_[1:3], 16), int(hex_[3:5], 16), int(hex_[5:7], 16)
    return f"\x1b[38;2;{r};{g};{b}m"


def version_key(path):
    return [int(x) if x.isdigit() else 0 for x in os.path.basename(path.rstrip("/")).split(".")]


def run_plugin(raw):
    dirs = glob.glob(os.path.join(HOME, ".claude/plugins/cache/claude-hud/claude-hud/*/"))
    dirs = [d for d in dirs if os.path.isfile(os.path.join(d, "dist/index.js"))]
    if not dirs:
        return ["claude-hud plugin not found"]
    newest = max(dirs, key=version_key)
    out = subprocess.run(["node", os.path.join(newest, "dist/index.js")], input=raw,
                         capture_output=True, text=True, timeout=10).stdout
    return out.rstrip("\n").split("\n") if out.strip() else []


def refresh_status():
    try:
        fresh = os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 300
    except OSError:
        fresh = False
    if not fresh:
        subprocess.Popen(
            ["bash", "-c", f"curl -s -m 4 '{STATUS_URL}' -o '{CACHE}.tmp' && mv -f '{CACHE}.tmp' '{CACHE}'"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def status_line():
    try:
        st = json.load(open(CACHE)).get("status", {})
    except Exception:
        return None
    ind = st.get("indicator", "")
    desc = st.get("description", "")
    state = {"none": ("ok", C["ok"]), "minor": ("degraded", C["warn"]), "major": ("incident", C["crit"]),
             "critical": ("incident", C["crit"]), "maintenance": ("maintenance", C["info"])}.get(ind)
    if not state:
        return None
    word, color = state
    tail = f" {fg(C['label'])}·{RESET} {fg(C['text'])}{desc}{RESET}" if desc else ""
    return f"{fg(color)}●{RESET} {fg(C['text'])}Claude{RESET} {fg(color)}{word}{RESET}{tail}"


def fmt_tokens(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}k"
    return str(n)


def fmt_reset(ts):
    if not ts:
        return ""
    if ts > 1e12:
        ts /= 1000
    left = int(ts - time.time())
    if left <= 0:
        return "resets now"
    d, h, m = left // 86400, left % 86400 // 3600, left % 3600 // 60
    if d:
        return f"resets in {d}d {h}h"
    if h:
        return f"resets in {h}h {m}m"
    return f"resets in {m}m"


def gauge(label, pct, base, detail):
    pct = max(0.0, min(100.0, float(pct)))
    filled = round(pct / 100 * BAR)
    color = C["crit"] if pct >= 85 else C["warn"] if pct >= 60 else base
    bar = f"{fg(color)}{'━' * filled}{fg(C['empty'])}{'━' * (BAR - filled)}{RESET}"
    tail = f"  {fg(C['label'])}{detail}{RESET}" if detail else ""
    return f"{fg(C['label'])}{label:<8}{RESET} {bar} {BOLD}{fg(color)}{pct:>3.0f}%{RESET}{tail}"


def gauges(data):
    lines = []
    cw = data.get("context_window") or {}
    pct = cw.get("used_percentage")
    cur = cw.get("current_usage") or {}
    used = sum(cur.get(k) or 0 for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    size = cw.get("context_window_size") or 0
    if pct is None and size and used:
        pct = used * 100 / size
    if pct is not None:
        detail = f"{fmt_tokens(used)} / {fmt_tokens(size)}" if size and used else ""
        lines.append(gauge("Context", pct, C["ctx"], detail))
    rl = data.get("rate_limits") or {}
    for key, label, note in (("five_hour", "Session", "5h window"), ("seven_day", "Weekly", "7d window"),
                             ("spend_limit", "Spend", "")):
        win = rl.get(key) or {}
        p = win.get("used_percentage")
        if p is None:
            continue
        reset = fmt_reset(win.get("resets_at"))
        detail = " · ".join(x for x in (reset, note) if x)
        lines.append(gauge(label, p, C["use"], detail))
    return lines


def main():
    raw = sys.stdin.read()
    sync_config()
    plugin = run_plugin(raw)
    try:
        data = json.loads(raw) if raw.strip() else {}
        refresh_status()
        extra = []
        st = status_line()
        if st:
            extra.append(st)
        extra += gauges(data)
        out = plugin[:1] + extra + plugin[1:] if plugin else extra
    except Exception:
        out = plugin
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

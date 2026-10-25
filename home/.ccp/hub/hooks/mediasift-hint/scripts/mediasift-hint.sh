#!/bin/bash
# mediasift-hint — UserPromptSubmit
# When a prompt names a video/audio file or a YouTube/Vimeo link, tell the agent to run
# `mediasift see` (and whether a card is cached). Silent otherwise, and silent if mediasift
# is not installed: a hint must never block a prompt. Looks in ~/.local/bin, then the mise shim,
# then PATH. Source: samhvw8/mediasift (hook.py).
F="$HOME/.local/bin/mediasift"
[ -x "$F" ] || F="$HOME/.local/share/mise/shims/mediasift"
[ -x "$F" ] || F="$(command -v mediasift 2>/dev/null)"
[ -n "$F" ] && [ -x "$F" ] || { cat >/dev/null; exit 0; }
exec "$F" hook

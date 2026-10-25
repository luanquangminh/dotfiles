#!/bin/bash
# tmux-remind — PreToolUse (Bash)
# When a long-running command (installs, tests, builds, docker) runs outside tmux,
# add a one-line hint to use tmux. Never blocks. Silent inside tmux or for other commands.
input=$(cat)
[ -n "$TMUX" ] && exit 0
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0
printf '%s' "$cmd" | grep -Eq '(^|[;&| ])(npm (install|test)|pnpm (install|test)|yarn (install|test)|bun (install|test)|cargo build|make|docker|pytest|vitest|playwright)([ ;&|]|$)' || exit 0
cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"[tmux-remind] This command can run long and the session is not inside tmux. Prefer `tmux new -d -s dev '<command>'` (attach: `tmux attach -t dev`) so it survives and its output stays readable."}}
JSON

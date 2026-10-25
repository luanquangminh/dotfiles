#!/bin/bash
# tmux-dev-guard — PreToolUse (Bash)
# Block a dev server (npm/pnpm/yarn/bun dev) started outside tmux, so its logs stay
# reachable. Exit 2 = block; the stderr text is shown to the agent. Silent inside tmux,
# when the command already wraps itself in tmux, and for every other command.
input=$(cat)
[ -n "$TMUX" ] && exit 0
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null) || exit 0
printf '%s' "$cmd" | grep -Eq '(^|[;&| ])(npm run dev|pnpm( run)? dev|yarn dev|bun run dev)([ ;&|]|$)' || exit 0
case "$cmd" in *tmux*) exit 0;; esac
cat >&2 <<EOF2
[tmux-dev-guard] BLOCKED: a dev server must run inside tmux so its logs stay reachable.
Run it as:  tmux new-session -d -s dev '$cmd'
Read logs:  tmux capture-pane -p -t dev | tail -50
EOF2
exit 2

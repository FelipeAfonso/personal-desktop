# Repo rules for agents

## No PRs here: ask before merging to main

Override of the global worktree & branching discipline for this repo: don't
open PRs. Work on a branch or worktree as usual, push it, then report what
changed and ask Felipe for permission to merge to main. Merge only after he
says yes. After merging, use `./export_current --agents-only` for changes
limited to `agents/`; use `./export_current` when deploying other configs,
`bin/`, or systemd units.

# Miskatonic operations

Read this for desktop configuration, system packages, or secrets. This is
CachyOS with Hyprland on Wayland. It has a display, browser, and audio, but
reboots and may be offline. Persistent work belongs on rlyeh.

The tracked configuration is `~/code/personal/personal-desktop`. Read its
repository rules before editing. `./export_current` copies configuration to
the machine; `./import_current` copies live state and package/service lists
back into the checkout. Inspect an import's diff before committing it.

For agent changes, use `./export_current --agents-only`. This installs the
global prompts, references, skills, and hook scripts without exporting the
other desktop settings. Shared sources live in personal-server and are
copied with its `scripts/sync-agent-prompts.py`; read `maintenance.md` when
changing them. Never edit the generated instruction files directly.

System packages use pacman or paru, subject to the task's authorization.
sudo asks for Felipe's password. Agent CLIs are Bun globals in `~/.bun/bin`
so T3's updater can manage them without root; do not reinstall them via
pacman. Protect T3 Code's AppImage launcher, service, relay, port, and `~/.t3`.

`secrets-pull` decrypts the private sops/age repository into
`~/.config/zsh/.secrets.env`, which the shell loads. That file is gitignored
and mode 0600. Do not print or commit secrets. Agent CLIs and `gh` have been
configured here; verify access when needed.

For remote operations, read `fleet.md`. Rlyeh's checkout is
`~/code/personal/personal-server`, including when reached over SSH. It uses
NixOS and must be changed through its flake, not through imperative installs.

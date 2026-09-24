# Miskatonic

This is Felipe's CachyOS desktop, with Hyprland and a real display. It is not
always online. Keep persistent and scheduled work on rlyeh.

- Never kill or modify `t3code.service`, its relay, port 3773, or `~/.t3`.
- Configuration lives in `~/code/personal/personal-desktop`. Read the repo's
  instructions before changes or deployment. Use `./export_current --agents-only`
  for agent files; a full export also changes unrelated desktop settings.
- sudo needs Felipe's password. Do not assume unattended root. Agent CLIs
  are Bun globals; do not reinstall them through pacman.
- Put clones under `~/code/personal/`, `~/code/work/<client>/`, or `~/code/stuff/`.
- Bind previews to `0.0.0.0` and provide
  `http://miskatonic.bass-pirarucu.ts.net:<port>`.
- Remote reads are allowed. Changes to another machine must be included in
  the task. Never enable Tailscale Funnel or change tailnet membership or
  ACLs unless Felipe explicitly requests it.

Read `~/.agents/references/miskatonic.md` before system or secrets work.

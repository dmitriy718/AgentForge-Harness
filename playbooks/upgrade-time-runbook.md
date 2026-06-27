# Upgrade Time Runbook

## Preflight

1. Snapshot important project state.
2. Export package/tool versions.
3. Confirm backups for `Desktop`, `Downloads`, active repos, and secrets.
4. Run `checklists/system-health-check.md`.

## Upgrade Order

1. Firmware/dbx.
2. OS security updates.
3. Kernel and microcode.
4. Docker/container stack.
5. Language runtimes.
6. AI runtimes and models.
7. Editors/extensions.

## Postflight

1. Reboot after kernel, microcode, firmware, or dbx changes.
2. Check failed units.
3. Check Docker containers.
4. Run one smoke test per critical project.
5. Save handoff in `runs/YYYY-MM-DD-upgrade/`.


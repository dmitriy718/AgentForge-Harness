# System Diagnostic Report

Date: 2026-06-26  
Host: GT1  
User: dima  
OS: Linux Mint 22.3 `zena`, kernel `6.17.0-35-generic`  
Hardware: GEEKOM GT Mega, Intel Core Ultra 9 185H, 30 GiB RAM, Lexar SSD NQ7A1 2TB

## Executive Summary

The workstation is healthy and has strong CPU/RAM/storage headroom for development and local AI orchestration. The main issues found were operational, not hardware failure: undersized swap, oversized Docker build cache, stale systemd failure from a live-ISO service, old journal/cache growth, missing NVMe diagnostic tools, and a pending package/firmware update backlog.

## Changes Applied

- Expanded `/swapfile` from 2 GiB to 16 GiB.
- Set workstation sysctl tuning in `/etc/sysctl.d/99-dev-ai-workstation.conf`:
  - `vm.swappiness=10`
  - `vm.vfs_cache_pressure=50`
  - `fs.inotify.max_user_watches=1048576`
  - `fs.inotify.max_user_instances=2048`
- Added Docker log rotation config in `/etc/docker/daemon.json`.
- Removed old kernel autoremove candidates and `slirp4netns`.
- Vacuumed system journals to 500 MiB.
- Cleaned npm, pnpm, pip, and uv caches.
- Pruned Docker build cache.
- Ran filesystem trim.
- Disabled stale `casper-md5check.service`.
- Installed `smartmontools` and `nvme-cli`.
- Enabled SMART monitoring.
- Disabled unnecessary NVMe-over-Fabrics autoconnect units.
- Created `/home/dima/AI-Harness`.
- Created and validated Codex skill `~/.codex/skills/dmitriy-ai-harness`.
- Created executable helper `/home/dima/.local/bin/aih`.

## Before And After

| Metric | Before | After |
|---|---:|---:|
| Root filesystem used | 785 GiB | 633 GiB |
| Root filesystem usage | 45% | 36% |
| Root available | 997 GiB | 1.2 TiB |
| Inode usage | 16% | 13% |
| Swap size | 2 GiB | 16 GiB |
| Swap used | 1.6 GiB | 0 B |
| Docker build cache | 200.4 GiB | 0 B |
| Docker image size | 226 GiB | 67.89 GiB |
| Failed system units | 1 | 0 |
| Failed user units | 0 | 0 |
| Journal size | 1.3 GiB | capped to 500 MiB target |

## Hardware Health

- NVMe SMART overall health: PASSED.
- Critical warning: `0x00`.
- Available spare: 100%.
- Percentage used: 2%.
- Media/data integrity errors: 0.
- Error log entries: 0.
- Current NVMe temperature: 40 C.
- Data written: 14.1 TB.
- Power-on hours: 320.

Watch item: the NVMe reports 51 unsafe shutdowns, 19 warning-temperature minutes, and 29 critical-temperature minutes. There are no media errors, but this history argues for UPS/power stability and periodic thermal checks.

## Current Health Snapshot

- RAM available: 23 GiB.
- Swap available: 15 GiB.
- Root filesystem: 633 GiB used of 1.9 TiB.
- Docker containers: 12 running, all critical app containers healthy except `greenmail`, which reports running but does not expose a Docker healthcheck.
- No reboot-required marker.
- No held APT packages.
- APT dependency check passes.
- Recent journal errors in last 30 minutes: none.

## Remaining Issues

- 53 APT packages are upgradeable, including Intel microcode, Docker, containerd, browsers, qemu/libvirt, Terraform, XML/Perl security updates, and VS Code.
- Firmware updater reports high-urgency UEFI dbx updates available.
- Docker daemon config validates, but Docker must be restarted before log rotation settings apply to the daemon.
- Bluetooth generated many historical device registration errors earlier in the boot; no recent errors were seen.
- Development toolchain has path drift: Homebrew Node/Python are first, while nvm also provides Node 24 globals.
- No local model runtime is installed (`ollama`, `llama-cli`, `llama-server` missing).

## 15 Recommended Next Changes

1. Apply the 53 pending APT upgrades, then reboot if microcode/kernel/libvirt components require it.
2. Apply the high-urgency UEFI dbx update with `fwupdmgr`, then reboot.
3. Restart Docker during a planned maintenance window so `/etc/docker/daemon.json` log rotation takes effect.
4. Standardize the Node toolchain: either Homebrew Node 26 or nvm Node 24 as default, not both competing silently.
5. Install and configure a local model runtime, preferably starting with Ollama or llama.cpp, then evaluate with `AI-Harness/templates/02-local-model-eval.md`.
6. Add a model storage directory convention such as `/home/dima/models` with subfolders for `gguf`, `ollama`, `evals`, and `archives`.
7. Move large Desktop/Downloads project folders into a structured workspace and archive stale downloads.
8. Add Docker image retention policy for restore-drill images; image footprint is still 67.89 GiB.
9. Create a weekly `docker builder prune` and cache cleanup timer with conservative age limits.
10. Add a monthly SMART report timer that writes NVMe health snapshots into `AI-Harness/runs/system-health/`.
11. Investigate Bluetooth only if it recurs; likely harmless scan noise, but persistent recurrence should be fixed by clearing stale pairings or restarting bluetooth.
12. Add a UPS or power-loss mitigation plan because SMART shows 51 unsafe shutdowns.
13. Run a thermal stress check under sustained local model load; NVMe has historical critical-temperature time.
14. Audit always-on services: Docker, libvirt VM, Home Assistant, Tailscale, printers, Bluetooth, ModemManager, and Avahi; disable anything not actually used.
15. Build a local model benchmark set from your real work: code repair, OS diagnostics, repo review, long-context summarization, and safety/privacy prompts.


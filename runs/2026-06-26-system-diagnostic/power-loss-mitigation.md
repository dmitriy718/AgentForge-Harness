# Power Loss Mitigation

Reason: NVMe SMART reports 51 unsafe shutdowns.

## Done

- Installed NUT UPS tooling (`nut-client`, `nut-server`) so the workstation is ready for UPS monitoring.
- Left NUT services disabled until actual UPS hardware and driver values are known.
- SMART monthly snapshots are now enabled through `ai-harness-monthly-health.timer`.

## Hardware Action

Buy a USB UPS with Linux/NUT support. Recommended class for this machine: 900-1500 VA line-interactive UPS with USB HID support.

## Configuration When UPS Is Connected

1. Run `lsusb` and `sudo nut-scanner -U`.
2. Configure `/etc/nut/ups.conf` with the detected driver.
3. Set `/etc/nut/nut.conf` to `MODE=standalone`.
4. Enable `nut-server.service` and `nut-monitor.service`.
5. Test with `upsc <ups-name>`.

## Validation

Monthly health snapshots should show whether `Unsafe Shutdowns` increments. If it increments after UPS deployment, power policy is still wrong.

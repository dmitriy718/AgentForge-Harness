# System Health Check

## Baseline

```bash
uname -a
lsb_release -a 2>/dev/null || cat /etc/os-release
uptime
free -h
swapon --show
df -hT
df -ih
systemctl --failed --no-pager
journalctl -p 3 -b --no-pager -n 120
```

## Storage And Firmware

```bash
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS,FSUSE%,ROTA
sensors 2>/dev/null || true
fwupdmgr get-updates
sudo smartctl -a /dev/nvme0n1
```

## Development Footprint

```bash
docker system df
du -hxd1 ~ 2>/dev/null | sort -h | tail -40
du -hxd1 ~/.cache ~/.config ~/.local ~/.npm 2>/dev/null | sort -h | tail -80
```

## Package Health

```bash
sudo apt-get check
apt list --upgradable
apt-mark showhold
```


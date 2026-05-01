#!/usr/bin/env bash
# collect_linux.sh — Collect Linux server configuration for CIS compliance auditing.
#
# Run as root or with sudo for full output.
#
# Usage:
#   sudo bash scripts/collect_linux.sh > my_linux_config.txt
#   python src/agent.py --env linux --framework cis --input my_linux_config.txt

set -euo pipefail

echo "=== Linux Compliance Config Snapshot ==="
echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '"')"
echo "Kernel: $(uname -r)"
echo ""

echo "--- Filesystem mounts ---"
cat /proc/mounts 2>/dev/null || mount
echo ""

echo "--- SSHD config ---"
grep -v '^#' /etc/ssh/sshd_config 2>/dev/null | grep -v '^$' || echo "sshd_config not found"
echo ""

echo "--- Password policy (/etc/login.defs) ---"
grep -E "^PASS_(MAX_DAYS|MIN_DAYS|MIN_LEN|WARN_AGE)" /etc/login.defs 2>/dev/null
echo ""

echo "--- sudoers ---"
cat /etc/sudoers 2>/dev/null | grep -v '^#' | grep -v '^$'
echo ""

echo "--- Local users with UID 0 ---"
awk -F: '($3 == 0) {print $1}' /etc/passwd
echo ""

echo "--- Users with empty passwords ---"
awk -F: '($2 == "" || $2 == "!") {print $1}' /etc/shadow 2>/dev/null || echo "Requires root"
echo ""

echo "--- World-writable files (top 20) ---"
find / -xdev -type f -perm -0002 2>/dev/null | head -20 || echo "Skipped"
echo ""

echo "--- SUID/SGID files ---"
find / -xdev \( -perm -4000 -o -perm -2000 \) -type f 2>/dev/null | head -30 || echo "Skipped"
echo ""

echo "--- Running services ---"
if command -v systemctl &>/dev/null; then
  systemctl list-units --type=service --state=running --no-pager 2>/dev/null
else
  service --status-all 2>/dev/null || echo "systemctl/service not available"
fi
echo ""

echo "--- Kernel parameters (sysctl security-relevant) ---"
sysctl -a 2>/dev/null | grep -E "net.ipv4.ip_forward|net.ipv4.conf.all.accept_redirects|net.ipv4.conf.all.send_redirects|net.ipv4.conf.all.log_martians|kernel.randomize_va_space|fs.suid_dumpable" || echo "sysctl not available"
echo ""

echo "--- Firewall status ---"
if command -v ufw &>/dev/null; then
  ufw status verbose 2>/dev/null
elif command -v firewall-cmd &>/dev/null; then
  firewall-cmd --list-all 2>/dev/null
else
  iptables -L -n 2>/dev/null | head -40
fi
echo ""

echo "--- Listening ports ---"
ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || echo "ss/netstat not available"
echo ""

echo "--- Last logins ---"
last -n 20 2>/dev/null
echo ""

echo "--- Crontabs ---"
for user in $(cut -f1 -d: /etc/passwd 2>/dev/null); do
  crontab -u "$user" -l 2>/dev/null && echo "user: $user" || true
done
echo ""

echo "--- Audit daemon ---"
auditctl -s 2>/dev/null || echo "auditd: not running or not installed"
echo ""

echo "=== End of snapshot ==="

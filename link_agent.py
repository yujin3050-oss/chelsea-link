import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PORT = 8767
OUT_FILE = Path(__file__).resolve().parent / "links.json"
TUNNEL_LOG = Path("/Users/yujin3050/.claude/webchat/logs/cloudflared_8767.log")
TUNNEL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


PRIVATE_RE = re.compile(r"^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)")


def lan_ips():
    ips = []
    for iface in ("en0", "en1", "en2", "en3"):
        r = subprocess.run(["ipconfig", "getifaddr", iface], capture_output=True, text=True)
        ip = r.stdout.strip()
        if ip and PRIVATE_RE.match(ip) and ip not in ips:
            ips.append(ip)
    return ips


def tunnel_url():
    if not TUNNEL_LOG.exists():
        return ""
    found = TUNNEL_RE.findall(TUNNEL_LOG.read_text(encoding="utf-8", errors="ignore"))
    return found[-1] if found else ""


def write_once():
    data = {
        "port": PORT,
        "ips": lan_ips(),
        "tunnel": tunnel_url(),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    OUT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


if __name__ == "__main__":
    if "--loop" in sys.argv:
        while True:
            print(json.dumps(write_once(), ensure_ascii=False), flush=True)
            time.sleep(15)
    else:
        print(json.dumps(write_once(), ensure_ascii=False, indent=2))

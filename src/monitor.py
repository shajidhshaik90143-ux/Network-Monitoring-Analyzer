import os
import platform
import socket
import subprocess
import time
from collections import deque
from datetime import datetime

import psutil


class NetworkMonitor:
    """Collects local network telemetry and diagnostics."""

    def __init__(self, max_history=500):
        self.history = deque(maxlen=max_history)
        self.events = deque(maxlen=100)
        self._previous = psutil.net_io_counters()
        self._previous_time = time.monotonic()

    def _rate(self, current, previous, elapsed):
        if elapsed <= 0:
            return 0.0
        return max(0.0, (current - previous) / elapsed)

    def sample(self):
        now = time.monotonic()
        elapsed = max(now - self._previous_time, 0.001)
        current = psutil.net_io_counters()

        download_bps = self._rate(current.bytes_recv, self._previous.bytes_recv, elapsed)
        upload_bps = self._rate(current.bytes_sent, self._previous.bytes_sent, elapsed)

        self._previous = current
        self._previous_time = now

        stats = self.interface_details()
        up_count = sum(1 for x in stats if x["is_up"])

        try:
            active = len(psutil.net_connections(kind="inet"))
        except (psutil.AccessDenied, PermissionError):
            active = 0

        item = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "hostname": socket.gethostname(),
            "download_bps": round(download_bps, 2),
            "upload_bps": round(upload_bps, 2),
            "bytes_recv": current.bytes_recv,
            "bytes_sent": current.bytes_sent,
            "packets_recv": current.packets_recv,
            "packets_sent": current.packets_sent,
            "active_connections": active,
            "interfaces_up": up_count,
            "interfaces_total": len(stats),
            "uptime_seconds": self.uptime_seconds(),
        }
        self.history.append(item)

        if download_bps > 10_000_000:
            self.events.appendleft({
                "time": item["timestamp"],
                "type": "HIGH_TRAFFIC",
                "message": f"Download rate exceeded 10 MB/s ({download_bps/1_000_000:.2f} MB/s)"
            })
        return item

    def interface_details(self):
        counters = psutil.net_io_counters(pernic=True)
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        result = []

        for name, counter in counters.items():
            s = stats.get(name)
            addresses = []
            for addr in addrs.get(name, []):
                if getattr(addr, "address", None):
                    addresses.append(addr.address)

            result.append({
                "interface": name,
                "is_up": bool(s.isup) if s else False,
                "speed_mbps": getattr(s, "speed", 0) if s else 0,
                "mtu": getattr(s, "mtu", 0) if s else 0,
                "addresses": ", ".join(addresses),
                "bytes_sent": counter.bytes_sent,
                "bytes_recv": counter.bytes_recv,
                "packets_sent": counter.packets_sent,
                "packets_recv": counter.packets_recv,
                "errors_in": counter.errin,
                "errors_out": counter.errout,
                "drops_in": counter.dropin,
                "drops_out": counter.dropout,
            })
        return result

    def connections(self):
        rows = []
        try:
            conns = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, PermissionError):
            return rows

        for c in conns:
            laddr = ""
            raddr = ""
            if c.laddr:
                laddr = f"{c.laddr.ip}:{c.laddr.port}"
            if c.raddr:
                raddr = f"{c.raddr.ip}:{c.raddr.port}"

            rows.append({
                "family": str(c.family),
                "type": str(c.type),
                "status": c.status,
                "local": laddr,
                "remote": raddr,
                "pid": c.pid if c.pid else "",
            })
        return sorted(rows, key=lambda x: (x["status"], x["local"]))

    def ping(self, target, count=4):
        target = target.strip()
        if not target:
            return {"success": False, "target": target, "error": "Empty target"}

        system = platform.system().lower()
        command = ["ping"]
        if system == "windows":
            command += ["-n", str(count), target]
        else:
            command += ["-c", str(count), target]

        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=max(10, count * 3),
            )
            output = (completed.stdout or "") + (completed.stderr or "")
            received = 0
            for line in output.splitlines():
                lower = line.lower()
                if "reply from" in lower or "bytes from" in lower:
                    received += 1

            if system == "windows":
                loss = 100.0 if received == 0 else max(0.0, (count - received) / count * 100)
            else:
                loss = max(0.0, (count - received) / count * 100)

            return {
                "success": completed.returncode == 0,
                "target": target,
                "sent": count,
                "received": received,
                "loss_percent": loss,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "return_code": completed.returncode,
                "output": output[-4000:],
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False, "target": target, "sent": count,
                "received": 0, "loss_percent": 100.0,
                "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                "error": "Ping timed out"
            }
        except FileNotFoundError:
            return {
                "success": False, "target": target, "sent": count,
                "received": 0, "loss_percent": 100.0,
                "error": "System ping command not found"
            }

    def uptime_seconds(self):
        return max(0, time.time() - psutil.boot_time())

    def clear_history(self):
        self.history.clear()
        self.events.clear()

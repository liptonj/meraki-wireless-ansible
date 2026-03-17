#!/usr/bin/env python3
"""Local Meraki Dashboard webhook receiver for testing.

Run with:  make webhook-server
    or:    python scripts/webhook_receiver.py

Exposes POST /webhooks to receive Meraki Dashboard alerts.
Validates HMAC-SHA256 signatures when MERAKI_WEBHOOK_SECRET is set.
Saves every payload to webhook_logs/ for later inspection.
"""

import hashlib
import hmac
import json
import os
import socket
import sys
import base64
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

LOG_DIR = Path(__file__).resolve().parent.parent / "webhook_logs"
DEFAULT_PORT = 5005
MAX_BODY_BYTES = 1_048_576  # 1 MiB


def _load_env() -> None:
    """Load .env from project root if python-dotenv is available."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv  # noqa: PLC0415

        load_dotenv(env_path)
    except ImportError:
        pass


def _verify_hmac(body: bytes, secret: str, signature: str) -> bool:
    """Validate Meraki HMAC-SHA256 signature (base64-encoded)."""
    computed = base64.b64encode(
        hmac.new(secret.encode(), body, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(computed, signature)


def _pretty_payload(data: dict) -> str:
    """Return a human-friendly summary of a Meraki webhook payload."""
    lines = [
        f"  Alert Type   : {data.get('alertType', 'N/A')}",
        f"  Alert Level  : {data.get('alertLevel', 'N/A')}",
        f"  Occurred At  : {data.get('occurredAt', 'N/A')}",
        f"  Sent At      : {data.get('sentAt', 'N/A')}",
        f"  Organization : {data.get('organizationName', 'N/A')} ({data.get('organizationId', '')})",
        f"  Network      : {data.get('networkName', 'N/A')} ({data.get('networkId', '')})",
        f"  Device       : {data.get('deviceName', 'N/A')} ({data.get('deviceSerial', '')})",
    ]
    alert_data = data.get("alertData", {})
    if alert_data:
        lines.append(f"  Alert Data   : {json.dumps(alert_data, indent=4)}")
    return "\n".join(lines)


def _save_payload(data: dict, headers: dict) -> Path:
    """Persist the webhook payload + headers to a timestamped JSON file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%f")
    alert_type = data.get("alertType", "unknown").replace(" ", "_")
    filename = f"{ts}_{alert_type}.json"
    filepath = LOG_DIR / filename
    record = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "headers": headers,
        "payload": data,
    }
    filepath.write_text(json.dumps(record, indent=2, default=str))
    return filepath


class WebhookHandler(BaseHTTPRequestHandler):
    """HTTP handler for Meraki Dashboard webhooks."""

    secret: str = ""
    validator: str = ""

    def log_message(self, format_str: str, *args: object) -> None:
        """Prefix log lines with a timestamp."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        sys.stderr.write(f"[{ts}] {format_str % args}\n")

    def _send_json(self, code: int, body: dict) -> None:
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body).encode())

    def _headers_dict(self) -> dict:
        return {k: v for k, v in self.headers.items()}

    # -- GET -----------------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")

        if path in ("", "/"):
            self._send_json(200, {
                "service": "meraki-webhook-receiver",
                "status": "running",
                "endpoints": {
                    "POST /webhooks": "Receive Meraki Dashboard webhooks",
                    "GET  /webhooks": "List received webhook log files",
                    "GET  /":         "This status page",
                },
            })
            return

        if path == "/webhooks":
            files: list[str] = []
            if LOG_DIR.exists():
                files = sorted(f.name for f in LOG_DIR.glob("*.json"))
            self._send_json(200, {"log_count": len(files), "files": files[-50:]})
            return

        self._send_json(404, {"error": "not found"})

    # -- POST ----------------------------------------------------------------

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path.rstrip("/")
        if path != "/webhooks":
            self._send_json(404, {"error": "not found"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > MAX_BODY_BYTES:
            self._send_json(413, {"error": "payload too large"})
            return

        raw_body = self.rfile.read(content_length)

        # -- HMAC validation --------------------------------------------------
        sig_header = self.headers.get("X-Cisco-Meraki-Webhook-Signature", "")
        if self.secret:
            if not sig_header:
                print("\n\033[93m[WARN] No signature header — skipping HMAC check\033[0m")
            elif not _verify_hmac(raw_body, self.secret, sig_header):
                print("\n\033[91m[FAIL] HMAC signature mismatch!\033[0m")
                self._send_json(403, {"error": "invalid signature"})
                return
            else:
                print("\n\033[92m[OK]   HMAC signature verified\033[0m")
        elif sig_header:
            print("\n\033[93m[WARN] Signature present but no MERAKI_WEBHOOK_SECRET configured\033[0m")

        # -- Parse payload -----------------------------------------------------
        try:
            data = json.loads(raw_body)
        except (json.JSONDecodeError, ValueError):
            print(f"\n\033[91m[ERR]  Non-JSON body ({len(raw_body)} bytes)\033[0m")
            self._send_json(400, {"error": "invalid JSON"})
            return

        # -- Meraki validator handshake ----------------------------------------
        if data.get("sharedSecret"):
            print("\n\033[96m[INFO] Meraki validation request received\033[0m")
            if self.validator:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(self.validator.encode())
                print(f"       Responded with validator: {self.validator}")
                return
            print("       No MERAKI_WEBHOOK_VALIDATOR set — returning empty 200")
            self.send_response(200)
            self.end_headers()
            return

        # -- Log and display ---------------------------------------------------
        headers = self._headers_dict()
        saved = _save_payload(data, headers)

        border = "=" * 72
        print(f"\n\033[96m{border}\033[0m")
        print(f"\033[1m  WEBHOOK RECEIVED  —  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\033[0m")
        print(f"\033[96m{border}\033[0m")
        print(_pretty_payload(data))
        print(f"\n  Saved to: {saved.relative_to(Path.cwd())}")
        print(f"\033[96m{border}\033[0m\n")

        self._send_json(200, {"status": "received"})


def main() -> None:
    _load_env()

    port = int(os.environ.get("WEBHOOK_RECEIVER_PORT", DEFAULT_PORT))
    secret = os.environ.get("MERAKI_WEBHOOK_SECRET", "")
    validator = os.environ.get("MERAKI_WEBHOOK_VALIDATOR", "")

    WebhookHandler.secret = secret
    WebhookHandler.validator = validator

    server = HTTPServer(("0.0.0.0", port), WebhookHandler)
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    banner = f"""
╔══════════════════════════════════════════════════════════════════════╗
║  Meraki Dashboard Webhook Receiver                                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  Listening on    :  http://0.0.0.0:{port:<5}                          ║
║  Webhook URL     :  http://localhost:{port}/webhooks                  ║
║  HMAC Validation :  {"ENABLED (secret set)" if secret else "DISABLED (set MERAKI_WEBHOOK_SECRET)":42}║
║  Validator       :  {"SET" if validator else "NOT SET (set MERAKI_WEBHOOK_VALIDATOR)":42}║
║  Log directory   :  webhook_logs/                                  ║
║                                                                    ║
║  Expose to internet (for Dashboard testing):                       ║
║    make webhook-public   (Cloudflare Tunnel)                       ║
║                                                                    ║
║  Press Ctrl+C to stop                                              ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down webhook receiver...")
        server.server_close()


if __name__ == "__main__":
    main()

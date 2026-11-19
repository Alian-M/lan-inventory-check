#!/usr/bin/env python3
"""Compare live ARP entries against a Markdown network inventory."""
import re
import subprocess
import sys
from pathlib import Path


def parse_inventory(md_path: Path) -> dict[str, str]:
    known = {}
    ip_re = re.compile(r"\b(\d{1,3}(?:\.\d{1,3}){3})\b")
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and not line.startswith("| Device"):
            cols = [c.strip().strip("`") for c in line.strip("|").split("|")]
            if len(cols) >= 2:
                match = ip_re.search(cols[1])
                if match:
                    known[match.group(1)] = cols[0]
    return known


def get_arp_ips() -> set[str]:
    output = subprocess.check_output(["arp", "-a"], text=True)
    return set(re.findall(r"\((\d{1,3}(?:\.\d{1,3}){3})\)", output))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 lan_check.py <inventory.md>")
        sys.exit(1)

    known = parse_inventory(Path(sys.argv[1]))
    live = get_arp_ips()

    unknown = sorted(live - set(known.keys()))
    online_known = sorted(live & set(known.keys()))

    print(f"Known devices online ({len(online_known)}):")
    for ip in online_known:
        print(f"  - {known[ip]} ({ip})")

    print(f"\nUnlisted devices in ARP cache ({len(unknown)}):")
    for ip in unknown:
        print(f"  - {ip}")


if __name__ == "__main__":
    main()

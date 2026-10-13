"""Rewrite the Recent builds block in README.md from the tanayv.com feed."""

import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED = "https://tanayv.com/rss.xml"
COUNT = 5
README = Path(__file__).resolve().parents[2] / "README.md"
START, END = "<!-- BUILDS:START -->", "<!-- BUILDS:END -->"


def escape(text: str) -> str:
    return re.sub(r"([\[\]])", r"\\\1", " ".join(text.split()))


def builds() -> list[str]:
    req = urllib.request.Request(FEED, headers={"User-Agent": "tanayvenkata-readme"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    lines = []
    for item in root.iter("item"):  # the feed is newest first
        if "build" not in [c.text for c in item.findall("category")]:
            continue
        title, link = item.findtext("title", ""), item.findtext("link", "")
        desc = item.findtext("description", "")
        line = f"- **[{escape(title)}]({link})**"
        if desc:
            line += f" — {escape(desc)}"
        lines.append(line)
        if len(lines) == COUNT:
            break
    if not lines:
        raise SystemExit("No builds in the feed; leaving README alone.")
    return lines


def main() -> None:
    text = README.read_text()
    block = "\n".join([START, *builds(), END])
    new, n = re.subn(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if n != 1:
        raise SystemExit("Markers not found in README.md.")
    README.write_text(new)


if __name__ == "__main__":
    main()

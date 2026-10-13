"""Rewrite the tagline and Recent builds blocks in README.md from tanayv.com."""

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

SITE = "https://tanayv.com"
FEED = f"{SITE}/rss.xml"
COUNT = 5
README = Path(__file__).resolve().parents[2] / "README.md"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "tanayvenkata-readme"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def escape(text: str) -> str:
    return re.sub(r"([\[\]])", r"\\\1", " ".join(text.split()))


def tagline() -> list[str]:
    page = fetch(SITE).decode()
    match = re.search(r'<meta name="description" content="([^"]*)"', page)
    if not match or not match.group(1).strip():
        raise SystemExit("No description on the home page; leaving README alone.")
    return [escape(html.unescape(match.group(1)))]


def builds() -> list[str]:
    root = ET.fromstring(fetch(FEED))
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


def fill(text: str, name: str, lines: list[str]) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    block = "\n".join([start, *lines, end])
    new, n = re.subn(re.escape(start) + r".*?" + re.escape(end), lambda _: block, text, flags=re.S)
    if n != 1:
        raise SystemExit(f"{name} markers not found in README.md.")
    return new


def main() -> None:
    text = README.read_text()
    text = fill(text, "TAGLINE", tagline())
    text = fill(text, "BUILDS", builds())
    README.write_text(text)


if __name__ == "__main__":
    main()

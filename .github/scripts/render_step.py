"""Render repository-local step images as URLs that work in issue comments."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import quote

IMAGE_PATTERN = re.compile(r"\.\./images/([A-Za-z0-9._-]+)")


def render_step(content: str, repository: str, ref: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository must use the owner/name format")
    if not ref:
        raise ValueError("ref must not be empty")

    image_base = (
        f"https://raw.githubusercontent.com/{repository}/{quote(ref, safe='')}"
        "/.github/images"
    )
    return IMAGE_PATTERN.sub(lambda match: f"{image_base}/{match.group(1)}", content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("repository")
    parser.add_argument("ref")
    args = parser.parse_args()

    content = args.source.read_text(encoding="utf-8")
    rendered = render_step(content, args.repository, args.ref)
    args.destination.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()

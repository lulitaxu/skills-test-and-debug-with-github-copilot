"""Validate that the learner recorded evidence and a falsifiable hypothesis."""

from pathlib import Path
import re
import sys

NOTES = Path("DEBUGGING.md")
HEADINGS = ("What the code does", "Baseline evidence", "Hypothesis")


def section_body(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def main() -> int:
    if not NOTES.is_file():
        print("DEBUGGING.md is missing.")
        return 1

    text = NOTES.read_text(encoding="utf-8")
    failures = []
    for heading in HEADINGS:
        body = section_body(text, heading)
        visible_body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
        if len(visible_body) < 40:
            failures.append(f"Complete the '{heading}' section with specific evidence.")

    if "<!--" in text:
        failures.append("Remove all placeholder comments from DEBUGGING.md.")

    if failures:
        print("\n".join(failures))
        return 1

    print("Debugging notes contain an explanation, baseline evidence, and hypothesis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

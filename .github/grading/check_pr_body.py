"""Check that the pull request documents independent verification."""

import os
import re
import sys

REQUIRED_HEADINGS = ("Verification", "Copilot review")


def main() -> int:
    body = os.environ.get("PR_BODY", "")
    failures = []
    for heading in REQUIRED_HEADINGS:
        pattern = rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)"
        match = re.search(pattern, body, flags=re.MULTILINE | re.DOTALL | re.IGNORECASE)
        content = (
            re.sub(r"<!--.*?-->", "", match.group(1), flags=re.DOTALL).strip()
            if match
            else ""
        )
        if len(content) < 30:
            failures.append(
                f"Add concrete details under the '## {heading}' heading."
            )

    if failures:
        print("\n".join(failures))
        return 1
    print("Pull request documents test evidence and critical Copilot review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

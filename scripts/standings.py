"""Rebuild the Advent of Workflow standings table in README.md from the submission issues.

Rank is the number of distinct challenges passed. Equal passes share a rank (dense: 1, 1, 2)
and are listed by handle, ignoring case. Diagrid runs are shown but never affect order.
Only the text between the STANDINGS markers changes. The script never commits or pushes.

Usage:
    python3 scripts/standings.py [--exclude FILE] [--check] [--readme PATH]

--exclude  one GitHub handle per line: Diagrid staff and Dapr maintainers, listed with a
           dagger because they are not eligible for the LEGO sets
--check    change nothing; exit 1 if README.md is out of date

Requires Python 3.10+ and the gh CLI.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from holopin_awards import DELETED_LOGINS, REPO, _read_excluded, check_complete, parse_challenge

ISSUE_LIMIT = 1000
START = "<!-- STANDINGS:START -->"
END = "<!-- STANDINGS:END -->"
HEADER = "| Rank | Handle | Passes | Passed challenges | Diagrid runs |\n|---|---|---|---|---|\n"
EXAMPLE = ("| EXAMPLE | `example-handle` (not a real participant, format only) "
           "| 3 | [1](#) [3](#) [5](#) | 1 |\n")
FOOTNOTE = "† not eligible for the LEGO® Game Boy™ sets"


@dataclass(frozen=True)
class Row:
    rank: int
    login: str
    passes: int
    links: tuple[tuple[int, int], ...]
    diagrid_runs: int
    excluded: bool


def _labels(issue: dict) -> set[str]:
    return {label["name"] for label in issue.get("labels") or []}


def _login(issue: dict) -> str:
    return (issue.get("author") or {}).get("login") or ""


def _problem(issue: dict) -> str | None:
    labels = _labels(issue)
    if parse_challenge(issue.get("body", "")) is None:
        return "no challenge number 1-12"
    if _login(issue).lower() in DELETED_LOGINS:
        return "deleted account"
    if "pass" in labels and "fail" in labels:
        return "labelled both pass and fail"
    if "pass" in labels and "pending" in labels:
        return "labelled both pass and pending"
    if "pass" in labels and issue.get("state") == "OPEN":
        return "labelled pass but still open"
    return None


def find_problems(issues: list[dict]) -> list[tuple[int, str]]:
    """Issues the table cannot place, as (number, reason), sorted by number."""
    found = ((issue["number"], _problem(issue)) for issue in issues)
    return sorted((number, reason) for number, reason in found if reason)


def build_rows(issues: list[dict], excluded: set[str]) -> list[Row]:
    """Ranked standings rows from the passed submission issues."""
    excluded = {handle.lower() for handle in excluded}
    logins: dict[str, str] = {}
    # key -> challenge -> list of (closedAt, number, bonus)
    passed: dict[str, dict[int, list[tuple[str, int, bool]]]] = {}
    for issue in issues:
        labels = _labels(issue)
        if "pass" not in labels or _problem(issue):
            continue
        login = _login(issue)
        key = login.lower()
        logins.setdefault(key, login)
        challenge = parse_challenge(issue["body"])
        passed.setdefault(key, {}).setdefault(challenge, []).append(
            (issue.get("closedAt") or "", issue["number"], "bonus-confirmed" in labels))

    unranked = []
    for key, challenges in passed.items():
        links = tuple((c, min(entries)[1]) for c, entries in sorted(challenges.items()))
        runs = sum(any(bonus for _, _, bonus in entries) for entries in challenges.values())
        unranked.append((len(challenges), key, links, runs))
    unranked.sort(key=lambda item: (-item[0], item[1]))

    rows, rank, previous = [], 0, None
    for passes, key, links, runs in unranked:
        if passes != previous:
            rank, previous = rank + 1, passes
        rows.append(Row(rank, logins[key], passes, links, runs, key in excluded))
    return rows


def render_block(rows: list[Row]) -> str:
    """The text between the markers: the table, and the footnote if anyone is excluded."""
    if not rows:
        return "\n" + HEADER + EXAMPLE
    lines = []
    for row in rows:
        handle = f"[`{row.login}`](https://github.com/{row.login})" + (" †" if row.excluded else "")
        links = " ".join(f"[{c}](https://github.com/{REPO}/issues/{n})" for c, n in row.links)
        lines.append(f"| {row.rank} | {handle} | {row.passes} | {links} | {row.diagrid_runs} |\n")
    block = "\n" + HEADER + "".join(lines)
    if any(row.excluded for row in rows):
        block += f"\n{FOOTNOTE}\n"
    return block


def replace_block(readme: str, block: str) -> str:
    """README with the text between the markers replaced by block."""
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError(f"README must contain {START} and {END} exactly once each")
    start = readme.index(START) + len(START)
    end = readme.index(END)
    if end < start:
        raise ValueError(f"{END} comes before {START}")
    return readme[:start] + block + readme[end:]


def _fetch_issues() -> list[dict]:
    result = subprocess.run(
        ["gh", "issue", "list", "-R", REPO, "--label", "submission", "--state", "all",
         "--limit", str(ISSUE_LIMIT), "--json", "number,author,body,labels,state,closedAt"],
        check=True, capture_output=True, text=True)
    issues = json.loads(result.stdout)
    check_complete(issues, ISSUE_LIMIT)
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exclude", help="file with one excluded GitHub handle per line")
    parser.add_argument("--check", action="store_true", help="exit 1 if README.md is out of date")
    parser.add_argument("--readme", default=str(Path(__file__).resolve().parent.parent / "README.md"))
    args = parser.parse_args(argv)

    issues = _fetch_issues()
    for number, reason in find_problems(issues):
        print(f"PROBLEM  #{number}: {reason}", file=sys.stderr)

    path = Path(args.readme)
    current = path.read_text(encoding="utf-8")
    try:
        updated = replace_block(current, render_block(build_rows(issues, _read_excluded(args.exclude))))
    except ValueError as error:
        print(f"ERROR  {error}", file=sys.stderr)
        return 2
    if args.check:
        if updated != current:
            print("README.md standings are out of date", file=sys.stderr)
            return 1
        return 0
    if updated != current:
        path.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

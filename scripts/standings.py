"""Rebuild the Advent of Workflow standings table in README.md from the submission issues.

Rank is the number of distinct challenges passed. Equal passes share a rank (dense: 1, 1, 2)
and are listed by handle, ignoring case. Diagrid runs are shown but never affect order.
"""

from dataclasses import dataclass

from holopin_awards import DELETED_LOGINS, parse_challenge


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

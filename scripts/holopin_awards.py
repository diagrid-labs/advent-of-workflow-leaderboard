"""Catch-up check for the Advent of Workflow Holopin badge.

Badges are awarded during review, when a pass is a participant's twelfth. This script
finds every finisher, shows who has no award yet, and with --post awards the ones that
were missed. It never posts a second award: anyone with an award comment anywhere in the
repo is skipped, whether or not the bot replied.

Usage:
    python3 scripts/holopin_awards.py [--maintainers marcduiker] [--post]

Requires Python 3.10+ and the gh CLI, authenticated as a maintainer who is an admin or
owner of the diagrid Holopin organization.
"""

import argparse
import json
import re
import subprocess
import sys

REPO = "diagrid-labs/advent-of-workflow-leaderboard"
CHALLENGES = set(range(1, 13))
ISSUE_LIMIT = 1000
BOT_LOGINS = {"holopin-bot", "holopin-bot[bot]", "app/holopin-bot"}
DELETED_LOGINS = {"", "ghost"}

_CHALLENGE_RE = re.compile(r"^###\s*Challenge number\s*\n+\s*(\d+)\s*$", re.MULTILINE)


class IncompleteIssueList(Exception):
    """gh returned as many issues as the limit allows, so some may be missing."""


def parse_challenge(body: str) -> int | None:
    """The number under the form's "### Challenge number" heading, or None."""
    match = _CHALLENGE_RE.search(body or "")
    if not match:
        return None
    number = int(match.group(1))
    return number if number in CHALLENGES else None


def _login(issue: dict) -> str:
    return ((issue.get("author") or {}).get("login") or "").lower()


def find_finishers(issues: list[dict]) -> tuple[dict[str, int], list[int]]:
    """Map each finisher's handle to their final issue, and list unreadable issues.

    A finisher has passed all twelve distinct challenges. Their final issue is the passed
    issue closed last. Everyone is eligible, Diagrid staff and Dapr maintainers included. Issues with no
    readable challenge number, or by a deleted account, are unreadable.
    """
    passed: dict[str, set[int]] = {}
    last_closed: dict[str, tuple[str, int]] = {}
    unreadable = []
    for issue in issues:
        challenge = parse_challenge(issue.get("body", ""))
        handle = _login(issue)
        if challenge is None or handle in DELETED_LOGINS:
            unreadable.append(issue["number"])
            continue
        passed.setdefault(handle, set()).add(challenge)
        closed = (issue.get("closedAt") or "", issue["number"])
        if handle not in last_closed or closed > last_closed[handle]:
            last_closed[handle] = closed
    finishers = {
        handle: last_closed[handle][1]
        for handle, challenges in passed.items()
        if challenges == CHALLENGES
    }
    return finishers, sorted(unreadable)


def award_comment(handle: str) -> str:
    return f"@holopin-bot @{handle} Congratulations on passing the 12 challenges!"


def award_status(comments: list[dict], handle: str, maintainers: set[str]) -> str:
    """"awarded" if the bot replied for this handle, "comment-no-reply" if only a
    maintainer's award comment exists, otherwise "missing"."""
    handle = re.escape(handle.lower())
    maintainers = {m.lower() for m in maintainers}
    award_re = re.compile(rf"@holopin-bot\s+@{handle}(?![\w-])")
    reply_re = re.compile(rf"congratulations @{handle},")
    commented = False
    for comment in comments:
        author = _login(comment)
        body = (comment.get("body") or "").lower()
        if author in BOT_LOGINS and reply_re.search(body) and "https://holopin.io/claim/" in body:
            return "awarded"
        if author in maintainers and award_re.search(body):
            commented = True
    return "comment-no-reply" if commented else "missing"


def check_complete(issues: list, limit: int) -> None:
    if len(issues) >= limit:
        raise IncompleteIssueList(f"gh returned {len(issues)} issues, the limit; raise ISSUE_LIMIT")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--maintainers", default="marcduiker",
                        help="comma-separated handles whose award comments count")
    parser.add_argument("--post", action="store_true", help="post the missing award comments")
    return parser.parse_args(argv)


def _gh_json(args: list[str]):
    result = subprocess.run(["gh", *args], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def _read_excluded(path: str | None) -> set[str]:
    """Handles from an exclusion file. Used by standings.py for the LEGO sets, not for the badge."""
    if not path:
        return set()
    with open(path, encoding="utf-8-sig") as handle_file:
        lines = (line.split("#", 1)[0].strip() for line in handle_file)
        return {line.lstrip("@") for line in lines if line}


def _all_comments() -> list[dict]:
    """Every issue comment in the repo, as {"author": {"login"}, "body"}."""
    pages = _gh_json(["api", "--paginate", "--slurp", f"repos/{REPO}/issues/comments?per_page=100"])
    return [{"author": {"login": c["user"]["login"] if c.get("user") else ""}, "body": c.get("body")}
            for page in pages for c in page]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    maintainers = {m.strip() for m in args.maintainers.split(",") if m.strip()}

    issues = _gh_json(["issue", "list", "-R", REPO, "--label", "submission", "--label", "pass",
                       "--state", "all", "--limit", str(ISSUE_LIMIT),
                       "--json", "number,author,body,closedAt"])
    check_complete(issues, ISSUE_LIMIT)
    finishers, unreadable = find_finishers(issues)
    comments = _all_comments()

    for number in unreadable:
        print(f"UNREADABLE  #{number}: no challenge number 1-12, or a deleted account; check by hand")

    to_post, to_check = [], []
    for handle, final_issue in sorted(finishers.items()):
        status = award_status(comments, handle, maintainers)
        if status == "awarded":
            print(f"awarded     @{handle} (final issue #{final_issue})")
        elif status == "comment-no-reply":
            print(f"NO REPLY    @{handle} (final issue #{final_issue}): award comment posted, "
                  "but no bot reply; check by hand")
            to_check.append(handle)
        else:
            print(f"MISSING     @{handle} (final issue #{final_issue})")
            to_post.append((handle, final_issue))

    print(f"\n{len(finishers)} finishers, {len(to_post)} missing, {len(to_check)} without a bot reply, "
          f"{len(unreadable)} unreadable issues")

    if args.post:
        for handle, final_issue in to_post:
            subprocess.run(["gh", "issue", "comment", str(final_issue), "-R", REPO,
                            "--body", award_comment(handle)], check=True)
            print(f"posted      @{handle} on #{final_issue}")
    elif to_post:
        print("Dry run: nothing posted. Run again with --post to award the missing ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

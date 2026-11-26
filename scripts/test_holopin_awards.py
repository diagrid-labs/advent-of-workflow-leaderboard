import json
import unittest
from pathlib import Path

from holopin_awards import (
    IncompleteIssueList,
    award_comment,
    award_status,
    check_complete,
    find_finishers,
    parse_args,
    parse_challenge,
)

MAINTAINER_AWARD = {"author": {"login": "marcduiker"},
                    "body": "@holopin-bot @Alice Congratulations on passing the 12 challenges!"}
BOT_REPLY = {"author": {"login": "holopin-bot[bot]"},
             "body": "Congratulations @alice, the maintainer of this repository has issued you a badge! Here it is: https://holopin.io/claim/abc"}

ISSUES = json.loads((Path(__file__).parent / "fixtures" / "issues.json").read_text())


class ParseChallengeTest(unittest.TestCase):
    def test_parse_challenge_reads_form_value(self):
        self.assertEqual(parse_challenge("### Challenge number\n\n7\n\n### Link"), 7)

    def test_parse_challenge_rejects_missing_and_out_of_range(self):
        self.assertIsNone(parse_challenge("no number here"))
        self.assertIsNone(parse_challenge("### Challenge number\n\n13"))


class FindFinishersTest(unittest.TestCase):
    def test_finishers_need_all_twelve_distinct(self):
        finishers, unreadable = find_finishers(ISSUES)
        self.assertEqual(set(finishers), {"alice", "carol", "erin"})
        self.assertEqual((finishers["alice"], finishers["erin"]), (112, 405))
        self.assertNotIn("bob", finishers)
        self.assertNotIn("dave", finishers)

    def test_unreadable_issues_are_reported(self):
        _, unreadable = find_finishers(ISSUES)
        self.assertEqual(unreadable, [299])

    def test_staff_and_maintainers_get_the_badge_too(self):
        # Decided 26 November 2026: only the LEGO sets exclude anyone.
        with self.assertRaises(TypeError):
            find_finishers(ISSUES, excluded={"carol"})


class AwardCommentTest(unittest.TestCase):
    def test_award_comment_text(self):
        self.assertEqual(award_comment("alice"),
                         "@holopin-bot @alice Congratulations on passing the 12 challenges!")


class AwardStatusTest(unittest.TestCase):
    def test_bot_reply_means_awarded(self):
        self.assertEqual(award_status([MAINTAINER_AWARD, BOT_REPLY], "alice", {"marcduiker"}), "awarded")
        self.assertEqual(award_status([BOT_REPLY], "alice", set()), "awarded")

    def test_maintainer_comment_without_bot_reply_needs_a_check(self):
        self.assertEqual(award_status([MAINTAINER_AWARD], "alice", {"marcduiker"}), "comment-no-reply")

    def test_nothing_for_this_handle_means_missing(self):
        self.assertEqual(award_status([MAINTAINER_AWARD, BOT_REPLY], "erin", {"marcduiker"}), "missing")

    def test_award_comment_by_non_maintainer_does_not_count(self):
        comments = [{"author": {"login": "erin"},
                     "body": "@holopin-bot @erin Congratulations on passing the 12 challenges!"}]
        self.assertEqual(award_status(comments, "erin", {"marcduiker"}), "missing")

    def test_longer_handle_does_not_count_for_its_prefix(self):
        comments = [{"author": {"login": "marcduiker"},
                     "body": "@holopin-bot @anna Congratulations on passing the 12 challenges!"},
                    {"author": {"login": "holopin-bot"},
                     "body": "Congratulations @anna, the maintainer of this repository has issued you a badge! https://holopin.io/claim/x"}]
        self.assertEqual(award_status(comments, "ann", {"marcduiker"}), "missing")


class SafetyTest(unittest.TestCase):
    def test_issue_list_at_the_limit_is_rejected(self):
        with self.assertRaises(IncompleteIssueList):
            check_complete([{}] * 1000, limit=1000)
        check_complete([{}] * 999, limit=1000)

    def test_post_needs_no_exclusion_file(self):
        self.assertTrue(parse_args(["--post"]).post)
        with self.assertRaises(SystemExit):
            parse_args(["--post", "--exclude", "x.txt"])

    def test_deleted_accounts_are_never_finishers(self):
        ghosts = [{"number": 900 + c, "author": None if c % 2 else {"login": "ghost"},
                   "body": f"### Challenge number\n\n{c}\n", "closedAt": "2026-12-20T00:00:00Z"}
                  for c in range(1, 13)]
        finishers, unreadable = find_finishers(ghosts)
        self.assertEqual(finishers, {})
        self.assertEqual(unreadable, [901 + i for i in range(12)])


if __name__ == "__main__":
    unittest.main()

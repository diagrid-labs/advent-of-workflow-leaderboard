import json
import unittest
from pathlib import Path

from holopin_awards import already_awarded, award_comment, find_finishers, parse_challenge

ISSUES = json.loads((Path(__file__).parent / "fixtures" / "issues.json").read_text())


class ParseChallengeTest(unittest.TestCase):
    def test_parse_challenge_reads_form_value(self):
        self.assertEqual(parse_challenge("### Challenge number\n\n7\n\n### Link"), 7)

    def test_parse_challenge_rejects_missing_and_out_of_range(self):
        self.assertIsNone(parse_challenge("no number here"))
        self.assertIsNone(parse_challenge("### Challenge number\n\n13"))


class FindFinishersTest(unittest.TestCase):
    def test_finishers_need_all_twelve_distinct(self):
        finishers, unreadable = find_finishers(ISSUES, excluded={"carol"})
        self.assertEqual(finishers, {"alice": 112, "erin": 405})
        self.assertNotIn("bob", finishers)
        self.assertNotIn("dave", finishers)

    def test_unreadable_issues_are_reported(self):
        _, unreadable = find_finishers(ISSUES, excluded=set())
        self.assertEqual(unreadable, [299])

    def test_excluded_handle_gets_no_badge(self):
        finishers, _ = find_finishers(ISSUES, excluded={"Carol"})
        self.assertNotIn("carol", finishers)


class AwardCommentTest(unittest.TestCase):
    def test_award_comment_text(self):
        self.assertEqual(award_comment("alice"),
                         "@holopin-bot @alice Congratulations on passing the 12 challenges!")


class AlreadyAwardedTest(unittest.TestCase):
    def test_already_awarded_detects_maintainer_comment(self):
        comments = [{"author": {"login": "marcduiker"},
                     "body": "@holopin-bot @Alice Congratulations on passing the 12 challenges!"}]
        self.assertTrue(already_awarded(comments, "alice", {"marcduiker"}))
        self.assertFalse(already_awarded(comments, "erin", {"marcduiker"}))

    def test_already_awarded_detects_bot_reply(self):
        comments = [{"author": {"login": "holopin-bot"},
                     "body": "Congratulations @alice, the maintainer of this repository has issued you a badge! Here it is: https://holopin.io/claim/abc"}]
        self.assertTrue(already_awarded(comments, "alice", set()))

    def test_award_comment_by_non_maintainer_does_not_count(self):
        comments = [{"author": {"login": "erin"},
                     "body": "@holopin-bot @erin Congratulations on passing the 12 challenges!"}]
        self.assertFalse(already_awarded(comments, "erin", {"marcduiker"}))


if __name__ == "__main__":
    unittest.main()

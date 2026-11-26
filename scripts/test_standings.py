import json
import unittest
from pathlib import Path

from standings import build_rows, find_problems

ISSUES = json.loads((Path(__file__).parent / "fixtures" / "standings_issues.json").read_text())


class BuildRowsTest(unittest.TestCase):
    def setUp(self):
        self.rows = build_rows(ISSUES, excluded={"DAVE"})
        self.by_login = {r.login: r for r in self.rows}

    def test_dense_rank_and_case_insensitive_order(self):
        self.assertEqual([(r.rank, r.login) for r in self.rows],
                         [(1, "dave"), (2, "Alice"), (2, "bob"), (3, "carol"), (3, "erin")])

    def test_duplicate_pass_counts_once_and_links_first_closed(self):
        erin = self.by_login["erin"]
        self.assertEqual((erin.passes, erin.links, erin.diagrid_runs), (1, ((4, 301),), 1))

    def test_bonus_only_counts_on_passed_issues(self):
        self.assertNotIn("frank", self.by_login)
        self.assertEqual(self.by_login["Alice"].diagrid_runs, 1)
        self.assertEqual(self.by_login["bob"].diagrid_runs, 0)

    def test_links_are_in_challenge_order(self):
        self.assertEqual(self.by_login["dave"].links, ((1, 131), (2, 132), (3, 133)))

    def test_exclusion_ignores_case(self):
        self.assertTrue(self.by_login["dave"].excluded)
        self.assertFalse(self.by_login["bob"].excluded)

    def test_problem_issues_are_skipped(self):
        numbers = {n for r in self.rows for _, n in r.links}
        self.assertTrue(numbers.isdisjoint({401, 402, 403, 404, 405}))
        self.assertTrue({"gina", "ghost", "hank", "ivy", "jack"}.isdisjoint(self.by_login))

    def test_issue_order_does_not_matter(self):
        self.assertEqual(build_rows(list(reversed(ISSUES)), excluded={"DAVE"}), self.rows)


class FindProblemsTest(unittest.TestCase):
    def test_reports_each_problem_once(self):
        self.assertEqual([n for n, _ in find_problems(ISSUES)], [401, 402, 403, 404, 405])

    def test_reasons_name_the_problem(self):
        reasons = dict(find_problems(ISSUES))
        self.assertIn("challenge number", reasons[401])
        self.assertIn("deleted", reasons[402])
        self.assertIn("fail", reasons[403])
        self.assertIn("pending", reasons[404])
        self.assertIn("open", reasons[405])


if __name__ == "__main__":
    unittest.main()

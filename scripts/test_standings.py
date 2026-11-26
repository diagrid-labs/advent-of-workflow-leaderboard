import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import standings
from standings import build_rows, find_problems, main, render_block, replace_block

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


class RenderTest(unittest.TestCase):
    def test_no_rows_keeps_the_example_row(self):
        self.assertEqual(render_block([]), (
            "\n| Rank | Handle | Passes | Passed challenges | Diagrid runs |\n|---|---|---|---|---|\n"
            "| EXAMPLE | `example-handle` (not a real participant, format only) | 3 | [1](#) [3](#) [5](#) | 1 |\n"))

    def test_rows_replace_the_example_and_mark_excluded(self):
        block = render_block(build_rows(ISSUES, excluded={"dave"}))
        self.assertNotIn("EXAMPLE", block)
        self.assertIn("| 1 | [`dave`](https://github.com/dave) † | 3 |", block)
        self.assertIn("[4](https://github.com/diagrid-labs/advent-of-workflow-leaderboard/issues/301)", block)
        self.assertTrue(block.endswith("\n\n† not eligible for the LEGO® Game Boy™ sets\n"))

    def test_no_footnote_without_excluded_rows(self):
        self.assertNotIn("†", render_block(build_rows(ISSUES, excluded=set())))


README = "intro\n<!-- STANDINGS:START -->\nold\n<!-- STANDINGS:END -->\noutro\n"


class ReplaceBlockTest(unittest.TestCase):
    def test_only_the_block_changes(self):
        self.assertEqual(replace_block(README, "\nnew\n"),
                         "intro\n<!-- STANDINGS:START -->\nnew\n<!-- STANDINGS:END -->\noutro\n")

    def test_missing_duplicate_or_reversed_marker_raises(self):
        reversed_markers = "<!-- STANDINGS:END -->\n<!-- STANDINGS:START -->\n"
        for bad in ("no markers", README + "<!-- STANDINGS:START -->\n", reversed_markers):
            with self.assertRaises(ValueError):
                replace_block(bad, "\nnew\n")


class MainTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.readme = Path(self.dir.name) / "README.md"

    def tearDown(self):
        self.dir.cleanup()

    def run_main(self, *args, issues=ISSUES):
        with mock.patch.object(standings, "_fetch_issues", return_value=issues):
            return main(["--readme", str(self.readme), *args])

    def test_check_reports_difference_then_passes_after_write(self):
        self.readme.write_text(README)
        self.assertEqual(self.run_main("--check"), 1)
        self.assertEqual(self.readme.read_text(), README)
        self.assertEqual(self.run_main(), 0)
        self.assertIn("[`bob`](https://github.com/bob)", self.readme.read_text())
        self.assertEqual(self.run_main("--check"), 0)

    def test_marker_error_leaves_file_untouched_and_returns_2(self):
        self.readme.write_text("no markers here\n")
        self.assertEqual(self.run_main(), 2)
        self.assertEqual(self.readme.read_text(), "no markers here\n")

    def test_exclude_file_marks_handles(self):
        self.readme.write_text(README)
        excluded = Path(self.dir.name) / "excluded.txt"
        excluded.write_text("# staff\n@Dave\n")
        self.assertEqual(self.run_main("--exclude", str(excluded)), 0)
        self.assertIn("[`dave`](https://github.com/dave) †", self.readme.read_text())

    def test_issue_limit_reached_stops_with_2(self):
        self.readme.write_text(README)
        with mock.patch.object(standings.subprocess, "run") as run:
            run.return_value.stdout = json.dumps([{}] * standings.ISSUE_LIMIT)
            self.assertEqual(main(["--readme", str(self.readme), "--check"]), 2)
        self.assertEqual(self.readme.read_text(), README)

    def test_gh_failure_or_missing_returns_2_not_1(self):
        self.readme.write_text(README)
        for error in (subprocess.CalledProcessError(1, ["gh"]), FileNotFoundError("gh")):
            with mock.patch.object(standings.subprocess, "run", side_effect=error):
                self.assertEqual(main(["--readme", str(self.readme), "--check"]), 2)

    def test_crlf_readme_keeps_its_line_endings(self):
        crlf = README.replace("\n", "\r\n").encode()
        self.readme.write_bytes(crlf)
        self.assertEqual(self.run_main(), 0)
        data = self.readme.read_bytes()
        self.assertEqual(data.count(b"\r\n"), data.count(b"\n"))
        self.assertTrue(data.startswith(b"intro\r\n") and data.endswith(b"outro\r\n"))
        self.assertEqual(self.run_main("--check"), 0)

    def test_check_sees_a_line_ending_only_difference(self):
        self.readme.write_text(README)
        self.run_main()
        mixed = self.readme.read_bytes().replace(b"| 1 |", b"| 1 |", 1).replace(b"\n", b"\r\n", 1)
        self.readme.write_bytes(mixed)
        self.assertEqual(self.run_main("--check"), 1)

    def test_exclude_file_with_bom_still_marks_the_first_handle(self):
        self.readme.write_text(README)
        excluded = Path(self.dir.name) / "excluded.txt"
        excluded.write_bytes("\ufeffdave\r\n".encode("utf-8"))
        self.assertEqual(self.run_main("--exclude", str(excluded)), 0)
        self.assertIn("[`dave`](https://github.com/dave) †", self.readme.read_text())


if __name__ == "__main__":
    unittest.main()

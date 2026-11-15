# SUBMISSION-TEST: deferred verification for Task 3

**STAGING ONLY. Delete this file before the repo goes public.**

Task 3 Step 6 (dry-run a submission) could not be run because the GitHub repo does not exist yet. A human runs this checklist once, after the repo is created and before it is announced. Task 3 is not verified until every step below has its expected result.

## LAUNCH BLOCKERS (do before the repo goes public)

- [ ] **CODE_OF_CONDUCT.md reporting contact.** Replace the text `REPORTING CONTACT TO BE SET BEFORE LAUNCH` with a real, monitored address. Do not publish an address that does not exist: it would silently swallow conduct reports. Search the repo for `TO BE SET BEFORE LAUNCH` to confirm none remain.
- [ ] **README placeholders.** All resolved: review turnaround is 1 day, the limit is 1 resubmission per challenge, and the LEGO criteria are stated (most confirmed Diagrid runs, ties beyond two settled by random draw within that group). Confirm the only `TO BE SET BEFORE LAUNCH` text left in this repo is the code of conduct contact below.
- [ ] **Labels exist.** Create `submission`, `pending`, `pass`, `fail` and `bonus-confirmed` in this repo. The submission form applies `submission` and `pending` on creation, and a label it cannot find is silently dropped.
- [ ] **Registration form GitHub handle field is live.** Confirm it is live before the repo goes public. The handle is the only join between a submission and a registration, and a submission from an unregistered handle is accepted and chased rather than rejected. (No email is requested in the issue form, the README or the standings.)
- [ ] **Repo policy settings** (cannot be set from files):
  - Issues are enabled. Settings > General > Features > Issues, ticked.
  - Settings > Actions > General: no workflow runs on anything in this repo. There are no workflows here.
  - Branch protection on `main`: require a pull request, restrict who can push to maintainers, no force pushes, do not allow bypass. Only maintainers have write access; the standings table is edited by maintainers only.
- [ ] **Cover for 4 to 13 January 2027.** Name who handles moderation and review while submissions are closed and results are not yet out.
- [ ] Remove this file.

## Prerequisites

- The repo exists as `diagrid-labs/advent-of-workflow-leaderboard` with these files pushed to `main`, issues enabled and the labels above created.
- One non-maintainer GitHub account, called A below, with a public fork of `diagrid-labs/advent-of-workflow` holding a throwaway workflow app, and a screenshot image on disk.

## Part 1: the form is the only way in

1. As account A, open the repo and click **New issue**.
   - Expected: the chooser offers exactly one template, **Submission**, plus the three contact links. There is no "Open a blank issue" link.
2. Follow each contact link.
   - Expected: all three resolve — the landing page, the challenge repo, and the challenge repo's issues filtered to the `challenge` label.
3. As account A, try to reach `/issues/new` directly, without `/choose`.
   - Expected: GitHub redirects to the chooser. A blank issue cannot be opened.
4. As account A, open a pull request against this repo.
   - Expected: the pull request body is pre-filled with the redirect note telling participants to submit an issue instead. (Nothing blocks the PR automatically; a maintainer closes it with that pointer.)

## Part 2: a single submission

5. As account A, open the Submission form and submit it with every required field filled: challenge 1, a link to a directory in A's fork, the screenshot dragged into the screenshot box, a JSON output pasted into the workflow output box, no bonus, all four declaration boxes ticked.
   - Expected: the issue is created with the title prefix `Submission: challenge `, carrying the labels `submission` and `pending`. The screenshot renders inline in the issue body. No GitHub Action runs.
6. Read the created issue as a logged-out visitor.
   - Expected: the work link, the screenshot, the workflow output (rendered as a JSON code block) and the declarations are all visible. No email address appears anywhere in it.
7. As account A, try submitting the form again with the screenshot box empty, the workflow output box empty, or with a declaration box unticked.
   - Expected: GitHub refuses to submit and names the missing required field.
8. A maintainer reviews it, comments the verdict, swaps `pending` for `pass`, and closes the issue.
   - Expected: the issue is closed and labelled `submission`, `pass`.
9. The maintainer regenerates the standings table in README.md from the submission issues.
   - Expected: one row for A, passes 1, the Passed challenges cell linking to the issue from step 5, Diagrid runs 0. The EXAMPLE row is removed once real rows exist.

## Part 3: fail and resubmit on the same issue

10. Account A submits challenge 7. The maintainer reviews it, comments what is missing, swaps `pending` for `fail`, and leaves the issue **open**.
    - Expected: the issue stays open, labelled `submission`, `fail`. A's passes stay at 1 after the table is regenerated, and challenge 7 does not appear under Passed challenges.
11. Account A fixes the work and comments on that same issue that it is ready for another look.
    - Expected: the maintainer is notified by the comment. No second issue exists for challenge 7.
12. The maintainer removes `fail`, re-adds `pending`, re-reviews, sets `pass`, closes, and regenerates.
    - Expected: exactly one issue exists for A and challenge 7, and it is labelled `pass`. Passes is now 2.
13. Account A submits challenge 3 while challenge 7 was still open and failed.
    - Expected: both issues coexist with no interference. Gaps are accepted: A has 1, 3 and 7 with no 2.

## Part 4: guardrails and the bonus

14. Account A submits challenge 5 with a Diagrid bonus screenshot attached. The maintainer confirms the bonus, adds `bonus-confirmed`, sets `pass`, closes, and regenerates.
    - Expected: The Diagrid runs count becomes 1 for A. Passes and rank position are unchanged by it. A participant with fewer passes but more bonus runs still ranks below one with more passes.
15. Account A submits a challenge linking a **private** fork.
    - Expected: the reviewer cannot read it and asks A in a comment to make it public. The issue stays open and is not failed for this alone.
16. Account A edits their own issue body after the verdict is recorded.
    - Expected: the edit is possible (GitHub always allows it) and visible in the issue's edit history, which is why the verdict lives in a maintainer comment and a label rather than in the issue body.

## Clean up

17. Delete or close the test issues, remove their labels from the counts, and restore the README standings to the single EXAMPLE row.
    - Expected: no test submission issue is open, and the standings table shows only the EXAMPLE row.

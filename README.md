# Advent of Workflow: leaderboard

![The interior of North Pole Station: elves in silver jumpsuits working banks of 1950s mainframe consoles and green phosphor screens under a riveted glass dome, with the sleigh waiting on its launch cradle through the open hangar door](advent-of-workflow-hero.jpg)

Standings and submissions for [Advent of Workflow](https://diagrid.io/advent-of-workflow), twelve Dapr Workflow challenges run by [Diagrid](https://www.diagrid.io) and open to everyone! The challenges live in [`diagrid-labs/advent-of-workflow`](https://github.com/diagrid-labs/advent-of-workflow). This repo is where you submit and where the standings live.

Challenges drop on 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21 and 23 December 2026. Submissions close **24 December 2026, 23:59 CET**. Results are announced **28 December 2026**.

North Pole Station has run on TINSEL — Tracking, Inventory, Scheduling and Elf Logistics — since 1957, and the old mainframe is finally failing: it drops jobs halfway through and keeps no record that they ever started. It cannot be taken down for repair, because the launch window does not move. So the station is being rebuilt one subsystem at a time, as durable workflows, and that is what each challenge asks you to build. Read the full story [here](STORY.md).

## Standings

Rank is the number of challenges passed, and nothing else. Participants with the same number of passes share a rank and are listed alphabetically.

<!-- STANDINGS:START -->
| Rank | Handle | Passes | Passed challenges | Diagrid runs |
|---|---|---|---|---|
| EXAMPLE | `example-handle` (not a real participant, format only) | 3 | [1](#) [3](#) [5](#) | 1 |
<!-- STANDINGS:END -->

How to read it:

- **Passes**: challenges whose submission issue is labelled `pass`.
- **Passed challenges**: one link per passed challenge, to that challenge's submission issue.
- **Diagrid runs**: how many of the passed challenges also did the optional Diagrid step, with the evidence confirmed by the reviewer. It never affects the order: a Diagrid run earns no extra pass and cannot lift anyone above a participant with more passes. This is the column the two LEGO sets are decided on.

A maintainer regenerates the table from the submission issues. Do not edit it in a pull request.

## How to submit

A submission is **an issue in this repo**, not a pull request. You need your work in a public repo, a screenshot, and the output your workflow returned. Setup is described in the [challenge repo](https://github.com/diagrid-labs/advent-of-workflow).

1. Open the [submission form](https://github.com/diagrid-labs/advent-of-workflow-leaderboard/issues/new?template=submission.yml).
2. Fill in the challenge number, link your work, drag the screenshot into the screenshot box, and paste your workflow's output, including the numbers the challenge asks for. Add the optional Diagrid screenshot if you did the bonus step.
3. Submit the issue. The reviewer takes it from there.

**One issue per challenge.** Open a separate issue for each challenge you submit. Gaps are fine: do challenge 7 before challenge 1 if you like.

Submissions are matched to your registration on your GitHub handle, so register with the same handle you submit from. A submission from a handle that did not register is still accepted, and we will follow up. Your email address stays with your registration: never put it in an issue here, which is public and permanent.

### Link to your work

Your fork of [`diagrid-labs/advent-of-workflow`](https://github.com/diagrid-labs/advent-of-workflow), with one directory or branch per challenge. It must be **public** so the reviewer can read it, and it must stay public until results are announced on 28 December 2026. Link the directory or branch holding this challenge's app, not just the repo root.

### Evidence

The screenshot is the workflow run detail page in the Dapr Dev Dashboard for a Dapr OSS run, or the workflow diagram showing the activities in the Diagrid web console for a Diagrid run. Attach it to your submission issue by dragging the image into the screenshot box, so the evidence stays with the submission.

### Issues are the only thing you open here

The submission form is the only issue anyone can open in this repo, and participants do not open pull requests here. A pull request from a participant is closed with a pointer back to the submission form. Questions about a challenge go in a comment on that challenge's issue in the [challenge repo](https://github.com/diagrid-labs/advent-of-workflow), and everything about rules, prizes and registration is on the [landing page](https://diagrid.io/advent-of-workflow).

## Review

A reviewing agent checks the numbers in your workflow output, reads the repo you linked and your screenshot, and reports against the challenge's stated criteria. The maintainer ([@marcduiker](https://github.com/marcduiker)) confirms every verdict. Neither `dapr-skills` nor Diagrid is part of the pass criteria: a hand-built workflow running on Dapr OSS passes on the same terms as anything else.

The verdict is recorded as a label on your issue and as a comment explaining it:

- **`pass`** — the issue is closed and the standings are updated.
- **`fail`** — the issue stays **open**, labelled `fail`, with a comment saying what is missing.

**Resubmitting after a fail:** do not open a new issue. Fix your work and add a comment to the same issue saying it is ready for another look. The reviewer removes the `fail` label, sets `pending` again and re-reviews. You can resubmit until submissions close on 24 December 2026, 23:59 CET. Nothing is accepted after that.

- **Review turnaround:** 1 day
- **Limit on resubmissions per challenge:** 1 resubmission per challenge

## Prizes

- A digital **[Holopin](https://www.holopin.io/)** award for passing all twelve challenges. You can earn it on Dapr OSS alone.

  <img src="diagrid-advent-of-workflow-2026-small.png" alt="The Advent of Workflow 2026 Holopin: a pixel-art Dapr robot wearing glasses, framed by red and green workflow diagrams, with the Dapr and Diagrid logos above and the words Advent of Workflow 2026 below" width="220">

- Two **LEGO Game Boy** sets: These are awarded to whoever ran the most optional steps in the challenges that use Diagrid. If more than two participants have the same amount of Diagrid-based implementations, two random winners will be chosen from this group.

> Diagrid staff and Dapr maintainers are excluded from prizes. The full rules and the winner criteria are on the landing page.

## Community

Be kind. This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). The repo name carries no year on purpose, so a future run can reuse it.

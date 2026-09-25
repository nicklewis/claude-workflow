---
name: pr-overview-doc
description: Build and publish a reviewer overview document for a floxhub PR — an exhibits-led HTML companion to the diff, published to the gh-pages branch as pr-<number>.html and linked from the PR description. Use once a PR has been judged to clear the bar for one (CLAUDE.local.md states that bar); covers what the page contains, how it looks, and how it ships.
---

# PR reviewer overview documents

The bar for whether a PR gets one of these lives in the floxhub
`CLAUDE.local.md`: the PR has something to show that prose handles
poorly, and the exhibits have no more durable home in the repo. This
skill covers what to build once that question is settled.

## What the document is

The document is a companion the reviewer keeps open beside the diff, not
a second narrative read start to finish. Lead with the exhibits; keep
prose to captions and the minimum connective tissue between them. A
short orientation panel at the top is fine. Don't restate the PR
description, and don't include a commit-by-commit list or
verification/test-evidence sections — the PR page and CI already carry
those.

The document states it was prepared by Claude and points at the PR
description as the authoritative summary. It supplements the PR
description; it never replaces it.

## Form

One self-contained HTML file: inline CSS, no external assets, light and
dark via `prefers-color-scheme`.

Build the page with the frontend-design skill. The design goal is
attention, not decoration: use color, hierarchy, and theming to draw the
reader's eye to what matters and to keep a repetitive format from
glazing over. A look that fits the PR's subject matter is a good vehicle
for this; playfulness is welcome when it carries meaning (a stamp that
marks status, a redaction bar that is one), but silliness for its own
sake belongs in demo material, not review docs.

## Publishing

Commit the page to the `gh-pages` branch as `pr-<number>.html`, working
in a git worktree off `origin/gh-pages` so the feature-branch checkout
is undisturbed.

Then add the page link (`https://flox.github.io/floxhub/pr-<number>.html`)
at the top of the PR description. Make the link self-describing — a few
words on what the page contains ("chain-of-custody diagrams and the
classification table"), so a reviewer can decide whether to open it
without clicking.

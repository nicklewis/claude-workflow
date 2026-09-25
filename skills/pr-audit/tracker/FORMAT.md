# findings.json

The audit report as data, served by `server.py` behind `index.html`. One
file per PR lives at `~/pr-audits/<N>/findings.json`, and the tracker
writes the user's reviews beside it as `state.json`. `example-findings.json`
is a complete instance, and `server.py --check` enforces the shape below.

Markup: backticks are the only markup any string carries, and `index.html`
renders `` `x` `` as code. Avoid double quotes inside strings; use single
quotes.

## Top level

| field | holds |
| -- | -- |
| `pr` | `number`, `title`, `url`, `author`, `head` (short SHA the audit ran on), `ticket`, `ticket_url`, `audited` (date), `worktree`, `probe_file`, `probe_command` |
| `lead` | Non-empty list of `{heading, text}` paragraphs rendered above the verdict: what the change accomplishes; the mechanism it rests on; optionally what it leaves as it is. Written from the code and the tickets, never from the PR description; SKILL.md's Output section says what each paragraph carries |
| `verdict` | Section A's first sentence: the merge-relevant conclusion. `index.html` renders `risk_pointer` directly beneath it as the verdict's closing sentence |
| `limit_line` | What execution could not reach |
| `risk_pointer` | The risk profile: the level of risk of the change as a whole, low, medium, or high, and the facts that set it (what it can reach, whether it only adds, whether a failure would persist), in one or two sentences. The key keeps its older name so every existing audit still renders. Part of the verdict block at the top of the page, never a footer |
| `verdicts` | `{"A": [...], "B": [...]}` — the choices the user picks from per section. Defaults: A `Fix / Accept / Defer (ticket) / Not a defect / Unsure`; B `Keep / Change / Ask the author / Unsure` |
| `sections` | Exactly two, ids `A` then `B`, each with `title`, `blurb`, `groups` |

## Groups

Section A has groups `did-not-hold` then `held`; section B has `lead` then
`complete`. Group ids are fixed, and titles are free. Array order is the
report's order, because `index.html` renders arrays as given and never
sorts, so B's ordering rule from SKILL.md (what reading the PR will not
reveal first, durable before local, never by significance) rides on each
item's position.

## Items

Ids are `A1…`, `B1…`, unique across the file, numbered in array order.

Section A item:

| field | holds |
| -- | -- |
| `provenance` | `ran`, `read`, or `unverified` — exactly one |
| `evidence` | For `ran`, the probe function name or the command; for `read`, the `file:line`s; for `unverified`, what would settle it |
| `summary` | One line, the claim alone, in words that stand without `detail` |
| `detail` | The full finding: mechanism, cause, fix where obvious. A probe is named by its function and one clause of what it does at first mention |
| `refs` | `path:line` strings, may be empty |
| `links` | Ids of related items, may be omitted. A finding whose resolution is the user's to decide links to the B item that carries the decision |

Section B item:

| field | holds |
| -- | -- |
| `summary` | What the PR did, as an act with a location — never the construct's name alone |
| `turns_on` | The fact about the world the choice depends on, and the consequence of each way it could go |
| `grounded` | Where that fact is established — `file:line`, a ticket, a library's documented behavior — or `nothing found`, which is written only after searching tickets as well as the repo |
| `default` | What the artifact does now, and nothing more |
| `refs`, `links` | As for A. A decision that follows from an A finding links back to it |

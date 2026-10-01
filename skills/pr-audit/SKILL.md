---
name: pr-audit
description: Audit a pull request someone else wrote — verify correctness by executing it, then surface the decisions the user must judge personally, each marked with how it was established. Use when asked to review a PR and give findings; not when asked to explain or walk through a diff, which wants a narrated tour rather than a verdict.
argument-hint: "[PR number | PR URL | branch]"
allowed-tools: Read, Write, Grep, Glob, Bash, Agent
---

# PR audit

## Relationship to `/review`

Self-contained; nothing to inherit. The builtin `/review` is two `gh`
commands plus "provide a thorough code review", and its two standing
constraints — the PR's diff is the only scope, and nothing gets run — are
both ones this skill lifts deliberately. Defects live outside a diff more
often than inside it, and the central claim of the reporting structure
below is one you can only earn by executing the code.

If the user invoked `/review` in this session, its closing format block
(overview / quality / suggestions / issues; "concise but thorough, clear
sections and bullet points") is superseded by the Output section here.

## The partition

**You own correctness. The user owns significance.**

Correctness is recoverable from the artifact and testable by running it,
so it is yours: does this code do what it says, does it break something
outside the diff, do its stated claims match its behavior. Deliver a
verdict on that.

Significance is a property of the world — whether a scenario occurs,
whether a requirement is real, what a wrong guess costs in production.
CLAUDE.md's "Decisions under uncertainty" says you cannot assess those
and the user can. So for the second deliverable you locate decisions and
hand them over **unranked**. A ranked list of "the important decisions"
puts your invented ordering in the same confident register as your
verified findings, which is the exact failure the writing guidance exists
to prevent.

Why intent cannot be read out of the diff is in the "Context
serialization" section of ~/.claude/CLAUDE.md ("code serializes behavior
completely and intent not at all"); why decisions get routed to a human is
in its "Decisions under uncertainty" section. Do not restate either in your
output.

## When the author was an agent

Assume it was unless you know otherwise, and read the PR description
accordingly. An agent-written PR often contains its own decision report:
sections listing what it chose, what it deferred, what a reviewer should
be suspicious of.

That report is **evidence, not coverage**. The author held the intent
while generating, which makes the list credible about what it chose — and
gives it no vantage at all on what it chose without noticing. So audit the
list rather than reproducing it, and spend the effort on absences. An item
the author flagged is already in front of the user; an item the author
never saw is the one you add.

## Using subagents

Steps 2 through 5 fan out cleanly, because their units are independent:
one agent per touched service running that service's gates, one per
cross-boundary identifier to trace, one per claim in the description to
check, one to diff against prior art. Launch them in a single message so
they run concurrently.

**Every subagent must return findings already carrying a provenance token
(see Output), and every `ran:` finding must come back with its literal
command and the salient output.** Put that in the prompt. A subagent
returns prose, prose from a subagent arrives stripped of how it was
obtained, and without the command in hand you cannot tell a gate that was
run from a gate that was described — which is exactly the laundering this
skill exists to prevent. Treat an unmarked subagent claim as `unverified:`
regardless of how confident it reads, and re-run anything load-bearing
yourself.

**Delegate finding, never concluding.** The verdict, the ordering, and the
decision-versus-bug sort stay with you: they depend on the whole picture,
and a subagent holds one slice of it.

## 1. Gather

`gh pr view <N> --json title,body,author,baseRefName,headRefName,state,additions,deletions,changedFiles,labels`,
the commit list with messages, and `gh pr diff <N>`.

**Fetch the commissioning ticket, and every ticket the description argues
from.** "Closes HUB-170" points at the only statement of what the change
was supposed to do; without it you are checking the PR against itself,
and every absence you report is really "absent from the repo". Pull the
referenced ones too — a description that defers work to a sibling ticket,
or leans on a prior one for a premise, is making a claim the diff cannot
settle. Read their comments, not just their bodies.

Then take the three things the ticket body does not contain:

- **Its relations.** Fetch with relations included — they are metadata
  rather than prose, so a PR that never mentions them leaves you no
  pointer at all. Related tickets routinely hold the mechanism behind an
  assumption the change rests on, the provenance of a number the
  description cites, or work that would obviate something the PR defers.
  A related ticket the PR does not cite is the highest-yield thing in
  this step, precisely because nothing in the diff can lead you to it.
- **Its project.** What the change is part of decides how to read a
  deferral: work the project already tracks is a handoff, and work it
  does not is an orphan wearing the same words.
- **Its attachments.** A sibling or superseding PR on the same ticket
  means the diff you are auditing may not be the one that merges.
  Establish which artifact is live before spending the audit on it.

Read the description in full before reading code — step 4 checks its
claims, and they have to be loaded to be checked.

## 2. Run it

**Read CI first, and do not reproduce what it already reports.** A green
check on the head SHA settles the project's gates. Re-running them buys
nothing, costs wall-clock, and generates false alarms — a platform-gated
skip, a service the local box lacks — that then cost a paragraph to
explain away. Confirm CI ran on the head SHA, not an earlier push.

Run the gates yourself only where CI cannot answer:

- CI is red at a stage that short-circuits a later one, so failures exist
  that CI never reached and its logs cannot show.
- CI does not cover the path the change touches.
- The PR states a result CI did not produce.

**Spend execution on what CI by construction never does.** This is where
the `ran:` token earns its keep, and where every finding worth the audit
comes from:

- **Mutate and re-run.** Delete the guard, branch, or fixture detail the
  PR says is load-bearing, and check that exactly the claimed tests fail.
  It is the only way to tell a test that binds from one that passes for an
  unrelated reason.
- **Inject.** Add the thing a guard is supposed to catch and confirm it is
  caught. A guard's stated scope and its actual scope diverge silently.
- **Probe the dependency.** Read the installed library's real constants
  and branching rather than the behavior the PR describes. A range pin
  means the code and its docstring can drift apart between versions.
- **Measure.** Where the PR reasons from a number, produce the number.

Pull the branch into a worktree (CLAUDE.md governs the name), install
dependencies, and record the merge base — the probes need a working
checkout even when the gates are redundant.

**Never write that something passed unless you ran it.** This is the whole
basis of the user's trust in your half; one unearned "tests pass" costs
more than every finding you produce. Keep the literal record — command,
then outcome — as the evidence behind every `ran:` marker.

## 3. Read past the diff

Execution reaches the happy path and the tests that exist. Reading reaches
the rest, and the highest-yield reading is outside the diff entirely:

- **A new or changed identifier that crosses a boundary** — an env var,
  config key, header, column, wire field, exported symbol. Grep for the
  other side. Values shared between services are the top target: a value
  one side newly accepts and the other still rejects produces no local
  failure and no test failure.
- **A new export from a module that tests mock** — adding to a module's
  surface breaks every partial mock of it, far from the diff.
- **Sibling code paths the change did not touch.** When a change adds a
  branch for one mode, check what the other modes now do at that line.
- **Prior art.** If a spike, an earlier branch, or a sibling implementation
  exists, diff against it. Where this change reverses a choice made there,
  the reversal is a decision for step 5, and its being silent is a finding
  here.
- **Repo obligations, swept by path.** List the top-level directories the
  diff touches and read the `CLAUDE.md` rules scoped to each. Repos state
  obligations as "always update X when changing Y", and they are triggered
  by paths — so read the paths. Recalling which rules exist finds the ones
  the author already obeyed. An unmet obligation is a finding.

## 4. Audit the stated claims

Highest yield of all, and entirely inside your half: prose is checkable
against code. The description is not context for the review — it is an
object of it.

Sort every assertion in the description, the commit messages, the new
comments and the docstrings:

- **A claim about the code** — check it. A description that contradicts
  the diff is a defect in the artifact a human will merge on, and it is
  worse than a code bug because it survives the merge unexamined.
- **A claim about the world** — check whether anything in the repo grounds
  it. Report the ungrounded ones as decisions, not as bugs.
- **A claim about verification** — reproduce it (step 2).

Then check the change against the **ticket**, which is a different
comparison from checking it against its own description. Three failure
modes, none visible from the diff:

- **Scope silently reduced.** The ticket names services, cases, or
  surfaces the PR's coverage account drops. A PR that enumerates what it
  affects is asserting completeness against the ticket's enumeration —
  diff the two lists rather than reading either alone.
- **Acceptance criteria unaddressed.** Check each one. A criterion the PR
  openly cannot meet is fine and worth restating; one it passes over in
  silence is the finding.
- **A ticket premise the change contradicts.** Implementers routinely
  discover the ticket was wrong about the world. That correction is often
  the most valuable thing in the PR and the least visible — it reads as
  ordinary code, and nobody holding only the diff can see that a stated
  assumption was overturned. Surface it as a decision, and say which
  claim it displaced.

## 5. Locate the decision sites

You cannot recover intent. You can find the places where a decision must
have been made, because they are syntactically locatable, and CLAUDE.md
already enumerates them:

a guard or early return; a default value; a fallback chain; a stored
format, schema, migration, or wire contract; a metric or series shape; an
interface or module boundary; a retry count, timeout, or backoff; a log
level; an error message that describes a condition; a comment asserting a
scenario occurs; a test that enforces a case.

For each site, write two things and do not editorialize past them:

- **turns on:** the fact about the world the choice depends on.
- **grounded:** where that fact is established — `file:line`, the
  commissioning ticket or one it links, an upstream library's documented
  behavior — or `nothing found`.

`nothing found` is the signal. It is not an accusation; most of these are
fine. It marks the ones only the user can settle.

**Write `nothing found` only after searching the tickets as well as the
repo.** Absence reported from a repo-only search is a claim about the
world wearing the costume of a check — it reads exactly like a verified
absence and is not one. If you did not reach a source, the token is
`unverified:`, not `nothing found`.

**Append each site to a scratchpad file the moment you find it**, one line
each, and assemble deliverable B by reading that file rather than by
recalling what you found. This is CLAUDE.md's decision-log rule pointed at
someone else's decisions, and it binds harder here: at report time you hold
a finished audit in which a site you noticed in passing and a site you
chased for ten minutes read identically, so recall returns the hard and the
recent and silently drops the automatic ones — which are most of them. With
subagents it is not optional, because their results arrive as separate
returns that decay fastest of all. Back-filling the file at the end
reproduces exactly the inference it exists to avoid.

Then drop everything that reached no artifact. A decision the author
considered and did not encode is not on the list.

## Output

A lead, then two deliverables, in this order, always.

**Lead — what the change accomplishes, and any new mechanism it
introduces.** Short paragraphs before the verdict, in your own words.
The first says concisely what the PR does, as what a caller or user
gets that they did not get before, and what stays the same. The second
is optional: write it only when the PR introduces a mechanism the
codebase did not have before, such as a new setting, endpoint, stored
format, data flow, or rule, which a reader needs in order to follow
the items below. It says what the mechanism takes in, what it decides,
and what it produces, naming identifiers only where they help. A PR
that changes behavior inside mechanisms that already exist gets no
second paragraph, because a restatement of how the diff implements the
change gives the reader nothing the items need. A third paragraph,
what the PR leaves as it is, belongs only where the ticket history
would otherwise mislead: a `Fixes` whose ticket-title defect was fixed
by an earlier commit, or a scope the ticket names and the PR does not
deliver.

Write the lead from the code and the tickets and check it against the
artifact; never summarize the PR description. The description is an
object of step 4, and a lead paraphrased from it carries its errors
into every card: for PR #2213 the slice's design document called the
two extracted functions pure, the shipped docstrings say they log and
mutate their argument, and a lead written from the document would have
handed the reader the wrong model before the first finding. The lead
is the reader's model of the system for everything below it. Run the
acceptance pass over it with the paragraph as the unit;
`tracker/example-findings.json` carries a worked example.

**A — Correctness.** Verdict first, in the first sentence. The verdict
closes with the risk profile: the level of risk of the change as a whole,
low, medium, or high, and the facts that set it, in one or two sentences.
CLAUDE.md's "risk profile" names those facts: what the change can reach,
whether it only adds, and whether a failure would persist. It is a level
for the whole change, never a pointer to one area and never a list of
risks. The profile is part of the verdict rather than a footer, because
it is the sentence of the audit the user carries into the PR body, and a
reader who stops after the first paragraph must not be missing it. Then
two lists under their own labels, in this order:

- **Did not hold** — every defect: code that misbehaves, a contract or a
  written claim the artifact contradicts, a test that does not bind what
  it claims to. The word "findings" names this list and only this list.
- **Held** — claims the PR makes that you confirmed by running or reading.
  These serve as the evidence behind the verdict, not as issues. They stay
  in the report because a confirmed claim is what separates "I ran the
  tests" from "tests pass", and they go second because they are not what
  the reader acts on.

The split exists because a single list under one heading, where a defect
and a confirmation carry the same token and the same shape, reads on a
skim as "things checked", and a reader who skims stops there. The
provenance token says how you know, and nothing in it says which way it
came out. The two labels carry that.

Each item in either list carries exactly one provenance token, written as
you write the item rather than checked afterward:

- `ran:` + the command — you executed something that exhibits this.
- `read:` + `file:line` — recovered from the artifact by reading.
- `unverified:` + what would settle it — depends on something you neither
  executed nor found in the artifact.

Name a probe or a mutation by what it does, never by a label alone. A
probe you wrote lives in a file the reader has not opened, so `P4` or
`M2` is a pointer into your context: it parses, so it prompts no lookup,
and the reader never learns there was a key to consult. At first mention
give the function name and one clause of mechanism, for example
"`test_p4_fga_failure_then_retry`: the FGA write raises after the database
commit, the user row survives, and a retry writes the grants", and let a
bare label abbreviate it afterward only within the same message.

Close section A with the limit line: what execution could not reach here —
cross-process behavior, a deploy, a real multi-worker run, an external
service. State it plainly. A uniform confident tone across items you ran
and items you reasoned about is the failure mode, and the line is the
cheap fix.

**B — Decisions the PR made that only you can judge.** Every item is a
choice the author already encoded in the artifact — a guard, a stored
format, a default, a comment asserting that a scenario occurs — handed to
the user because significance is theirs to assign. Each item names the
choice as made, and its default says what stays if they say nothing.
Where a decision follows from a finding in A, because the artifact
contradicts itself and only the user can say which side is right, the
contradiction stays in A and the choice goes here, and each points at the
other.

Read the scratchpad from step 5 and lay it out as a bounded lead over a
complete list.

Order by **what reading the PR will not reveal**, leading with that. The
user is going to read the diff; a decision written on the face of the
change reaches them without you. What does not: a coupling outside the
diff, a silent reversal of prior art, an assumption a test now enforces, a
guard for a case that never fires, anything on the unhappy or never path.
Within that, put **durable** before **local** — a stored format, schema,
cache key, wire contract, metric series shape, or interface boundary before
a guard, message, level, name, or count — because rework cost is what makes
an item urgent rather than deferrable.

That ordering never admits or excludes an item. **Bound the lead, never the
list:** open with the few you would push back on yourself, then give
everything below them. Drop an item only because it has no reader, never to
keep the list short. A list the user skims costs them nothing; a decision
you suppressed to protect their attention becomes permanent without either
of you choosing it. If the list feels too long to send, that feeling is the
bias this deliverable exists to correct, and the fix is ordering, not
cutting.

Never order by significance. That is the user's to assign.

Give each item its `turns on` / `grounded` pair and state the default: what
stays if the user says nothing. An unanswered question that silently
persists is how a guess becomes permanent. The default names what the
artifact does now, and nothing more: where the question was whether a
comment or the code beneath it is stale, a default of "stays, and the
comment is what to fix" has answered the question in the costume of a
default.

Each item is read alone, as one tracker card, by a reader who has not
opened the diff, the tickets, or this conversation, so every item
expands its own referents. The line you appended to the scratchpad in
step 5 is a pointer into your context — "`Identity.user` relationship,
no `back_populates`" — and it is the wrong unit to ship, because it
names a construct you recognize and the reader has never met. The item
written from it says what the PR did, as an act ("adds
a one-way `Identity.user` relationship at `models.py:141` and no
`User.identities` collection, so a user's identities are reachable
only by query"); what turns on it, with the consequence of each way
the fact could go ("if a consumer walks user → identities, as the
reconciler snapshot in design doc §5.8 does, it queries by hand or
adds the reverse side, and adding that side later without
`back_populates` leaves the two sides unsynchronized in a session");
where that is grounded, or which search came back empty; and what the
artifact does now. The tell is a summary that reads as a noun phrase:
a noun phrase names a thing, and an item has to name an act and its
consequence. The same rule reaches A: a `summary` states the claim in
words that stand without the `detail`.

Both halves of every item, in A and in B, describe behavior: what
happens, to whom, and under what conditions. Mechanism and code
references are allowed where they help explain the issue or the
decision, and never required. The reader triages each card by what it
does to users and operators, and mechanism written into every card by
rule buries that under explanation the triage never uses. The
`evidence` field already carries the `file:line` or command that backs
an item, so the prose need not repeat it.

## Deliver

The report is a file, `~/pr-audits/<N>/findings.json`, in the shape
`tracker/FORMAT.md` describes and `tracker/example-findings.json` shows.
Read both before writing it. It carries the lead, then A and B, exactly
as the Output section lays them out: the same items in the same order, each A item
with its provenance token and evidence, each B item with its `turns on`
/ `grounded` / `default`. Write it from the scratchpad, as step 5
requires, never from recall.

Then check it, and serve it once the checks pass:

    python3 ~/.claude/skills/pr-audit/tracker/server.py --check ~/pr-audits/<N>/findings.json
    python3 ~/.claude/skills/pr-audit/tracker/server.py ~/pr-audits/<N>

Fix every problem `--check` prints, then run the `acceptance-pass` skill
over the file with the card as the unit: its Check 2 is the test each
item has to pass. Serve only after both.

Run the serve command through the Bash tool with `run_in_background:
true`, never with `nohup` or a trailing `&`. A tracked background
command dies with the session, so no tracker outlives the audit that
started it, and the harness re-invokes you when it exits, which is how
the user's submission reaches you. The server picks the next free port
when the default is taken and prints the URL it chose as its first
line; read it from the task's output file, which the tool result names.
The page shows every item with a row of verdict chips, a notes box, and
a `reviewed` checkbox, saves each change to `~/pr-audits/<N>/state.json`,
and carries a `Submit` button that stops the server. Look at
`state.json` before any request that writes it: once the user has
started reviewing, a test write or delete destroys their answer.

The chat message carries the verdict with its risk profile, the did-not-hold count,
the lead decisions by title, the URL, and one line saying that `Submit`
stops the server and wakes you. It does not restate the lists: the
tracker is their one home, and a second serialization drifts from the
first.

The server exiting is the signal that the user is done. When the task
notification arrives, read the output file: a final `submitted at ...`
line with exit code 0 means the user pressed `Submit`; anything else is
a fault to report and fix (a port clash, a crash), not a submission.
Then read `state.json` back. Verdicts on A items are their triage of
your findings, verdicts on B items are their answers to the decisions,
and notes are their reasons. On a B item, `Keep` means the choice could
have gone either way and stays as the author left it, and `Affirm`
means the choice has a reason that has to outlive the review, which the
user's note states.

**The turn after the notification contains a summary and a proposal,
and nothing else.** No edit to the worktree, no comment on the PR, no
message to the author, no ticket, no command that changes anything,
until the user accepts the proposal. The summary groups the items by
the verdict the user gave, each with its note, and lists what they
left unreviewed. The proposal is the default action, shown as the
exact text that would be posted, and it follows from the verdicts
alone:

- One pull-request review, submitted as a comment because whether to
  block the merge is the user's to say, carrying every A item marked
  `Fix` and every B item marked `Change` or `Ask the author`. An item
  whose first ref names a line inside the PR's diff (the right side of
  a hunk in the `gh pr diff` from step 1) becomes an inline comment at
  that line; every other item goes in the review body. Write each
  comment in the Conventional Comments form (conventionalcomments.org):
  `label (decoration): subject`, a blank line, then the discussion,
  with `issue (blocking)` for a `Fix` that is a defect, `chore` for a
  `Fix` that is cleanup, `suggestion (blocking)` for a `Change`,
  `question` for `Ask the author`, and `issue (non-blocking)` naming
  the ticket for a `Defer` the user wants surfaced. The discussion
  carries the item's behavior, plus the mechanism and a fix where the
  author needs them to act, the user's note as their reason, and
  for a B item the answer they gave. The attribution CLAUDE.md
  requires for anything posted through the user's account goes once,
  in the review body, and not on each comment: its job is to make
  sure the authorship is not hidden, not to label which comments
  Claude wrote. The label carries the weight: never phrase a verdict
  as the user's ruling (`Nick's call`, `Nick's direction`), which
  reads as authority rather than as review.
- In that same review, a comment for every B item marked `Affirm`
  whose reason the PR does not already record. Look for the reason
  first in the commit messages and in any code comment at the decision
  point. Where either states it, the item needs nothing. Otherwise the
  comment, labelled `suggestion (blocking)` and placed inline or in
  the body by the same first-ref test as the other comments, names the
  choice, gives the user's note as the reason, and asks the author to
  record it where a later editor will meet it: in a code comment at
  the decision point when someone reading the code would otherwise
  reverse the choice, and otherwise in a sentence of the message of
  the commit that makes the choice. An `Affirm` with an empty note
  gets no comment. The tracker refuses to submit one, and if one
  arrives anyway, list it in the summary and ask for the reason,
  because a reason you supply is an invented justification posted
  under the user's verdict.
- One Linear ticket for every item marked `Defer (ticket)`, drafted
  with the `write-ticket` skill, in the commissioning ticket's team and
  project, naming the PR and the commissioning ticket in its body, with
  no `blocks` or `blockedBy` relations, since dependency wiring is the
  user's.
- Nothing for `Accept`, `Not a defect`, `Keep`, `Unsure`, or an
  unreviewed item.

Show the proposal and wait. A yes posts it, and CLAUDE.md's posting
rules govern the posting; anything else the user says replaces the
proposal. Do not offer alternatives (a message to the author, edits in
the worktree, doing nothing): the user names those when they want
them, and a menu puts a decision they have already made through the
tracker back in front of them. Another round is the
same serve command again, started the same way: `state.json` persists,
so the page reopens with their answers in place.

When the user asks for the report in chat instead of the tracker,
deliver A then B as the Output section lays them out, and chunk as
below.

## Chunking a report delivered in chat

Past roughly 600 changed lines or 15 files, or when a section would run
past ~1,500 words, split across turns in this fixed order:

1. **Lead, verdict and evidence** — what the change accomplishes and any
   new mechanism it introduces, then the merge-relevant conclusion and what you
   ran. Always one chunk, always first, never deferred. A reviewer who
   reads only this must not be missing the headline.
2. **Correctness findings**, chunked by component if long.
3. **Decisions**, chunked by component if long.

End chunk 1 with the remaining chunk list, then deliver one per turn. Run
them back to back without pausing if the user says to keep going.

Chunking moves items to a later turn; it never drops them. It is not a
budget, and reaching for it because a list feels long is the bias from
deliverable B wearing a different hat.

---
name: write-ticket
description: Write or revise a ticket that scopes work for an implementing model — the outcome/spec split, what to specify and what to leave, and how to keep invented concepts out. Use whenever drafting a Linear ticket or issue, breaking a feature into tickets, or reviewing a ticket someone else scoped.
---

# Writing tickets/scoping work

A ticket has two readers and they need opposite things. The human needs
to know what will be true when the work is done; that reader is served
by prose, and their moment ends at merge. The implementer is a model
with the codebase in view and none of the conversation that produced
the ticket; that reader needs a spec, and is served by constraints
rather than by explanation. Split the two with a heading rather than
blending them.

If a question arises while writing a ticket, stop and ask it rather
than embedding the open question in the ticket text.

## What a ticket is for

**A ticket makes an observable behavior change.** It is not for adding
an API a later ticket will consume, and it is not for implementing a
whole feature. Test each item against what someone would see: a
response shape nobody's eye reaches, a state check for a state nothing
sets, an endpoint with no caller — these fail the test and belong
somewhere else or nowhere.

A ticket that genuinely has no observable change on its own — a shared
mechanism, a document its consumer reads next sprint — should say so in
its own first lines, and should land with its first consumer rather
than ahead of it.

## The title

Imperative, naming the action the ticket performs (`Provision a user on
their first login`, `Treat an empty git password as anonymous at the
edge`), never a description of the state afterward or of the problem.

## The two sections

**Outcome.** Present tense, what is true when this is done. The test is
mechanical: it pastes into the PR body verbatim. If it doesn't paste,
it's describing work instead of a result. Open with the problem in a
sentence, then the outcome.

**Spec.** Three lists, in this order. Number the items so they can be
referred to in conversation.

- **Must** — the few things that produce the outcome. Minimize these.
- **Must not** — the boundaries. What would look reasonable and is
  wrong: breaking another deployment's path, duplicating a record,
  building the thing a later ticket owns.
- **You may assume** — permissions not to handle something. Maximize
  these. Each one is work nobody does.

Then, where they earn their place: **Report back on** (decisions the
implementer will make that you want surfaced when the work lands, per
Decisions under uncertainty) and **Pointers** (only what no single item
owns — a blocking PR, a design document).

Most things that feel like requirements are constraints or assumptions.
Failing on a collision is the *absence* of work; written as a
requirement it reads as something to build, and written as "you may
assume a collision is a dead end" it reads as permission not to.

Rejected alternatives ride inside the assumption they justify rather
than getting a section. "No numeric suffix: it hands someone a name
they did not expect" is one unit, not two.

## What to specify and what to leave

**The cut line is "recoverable from the code", not "simple versus
complex".** The implementer is the same model, with the codebase and
without the conversation. It will re-derive any amount of mechanism. It
will never re-derive that a customer authenticates with Kerberos, or
that you decided a feature is deferred rather than forgot it.

**Specify invariants, not mechanisms.** "Never leave the authorization
store more permissive than the database" is the requirement; whether
the commit precedes the tuple write is the implementer's. State the
invariant *once*, in the most durable place available — a service's
`claude.md`, a module docstring, the code itself — and let the ticket
assume it. The ticket gets shorter because something else got written,
not because the requirement disappeared.

**Point, don't paraphrase.** `file:line` for anything the implementer
would otherwise hunt for, inline with the item that needs it. Never
restate what the code says; one home per fact.

**A port has a reference, and the reference is the spec.** When the
ticket brings a behavior that exists for one deployment or backend to
another, find the existing implementation, point at it as the
behavioral reference, and specify only the differences, each as a
decision with its reason. Restating the behavior in your own words is
where drift enters: the paraphrase reads as a spec, the implementer
builds the paraphrase, and the divergence surfaces only when a user
compares the two. Check that the reference reaches every item: a
reference named for one service does not cover a sibling that lives in
another file.

**Cross-artifact contracts are the exception.** Pin an environment
variable name whose rename means editing SSM, task definitions and a
manifest together — and write the reason into the ticket so it doesn't
read as arbitrary. Don't pin a wire contract between two services you
control, where changing it is one commit.

## Guarding against invention

This is the failure that costs most, because every step reads as
reasonable given the step before it. A real behavior gets paraphrased
into a broader concept; the concept gets a schema column; the column
gets query logic; a later ticket writes an assumption about it. Four
artifacts deep from a paraphrase, and nothing anywhere records that the
concept was never real.

- **Before naming a concept, find it.** In the code, or in something
  the world established. If it exists in neither, you are inventing it
  — and an invented concept in a ticket becomes a real column in a
  schema faster than anyone notices.
- **Verify claims about the code while writing.** A grep is cheap and
  catches "keep the existing fallback chain" when no chain exists, or
  "register the client" when it is already registered.
- **State assumptions as facts about the system, not claims about the
  world.** "Nothing sets `deactivated_at`" rather than "nobody is
  deactivated". The first either stays true or breaks visibly; the
  second is a claim about users that quietly stops holding.
- **Mark what you could not verify, and only that.** `[unverified: …]`
  on an item that predicts something about the codebase you did not go
  look at, or that rests on a question nobody has answered. Default
  unmarked, so the marker keeps its discriminating power — a label
  applied to everything discriminates nothing.
- **A reviewing agent catches a missed requirement only if the
  requirement is written somewhere it can see** — the ticket, the repo,
  a `claude.md`. It is not a backstop for anything that lives only in
  your head.

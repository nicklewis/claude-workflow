---
name: acceptance-pass
description: Run the six-check acceptance pass over a finished prose draft — expensive phrases, encrypted phrases, unlabeled edges, unearned units, the skim test, unbound parameters — with the full detection criteria, remedies, and the pass's own blind spots. Invoke it, with the draft's file path, before every `git commit`, `gh pr create` or `gh pr edit`, comment or ticket post, and doc or generated-HTML write; prose that has not been through this invocation is still a draft, however it reads. Also invoke it whenever editing prose you did not write.
---

# The acceptance pass

The write-time rules in CLAUDE.md are the primary defense; this pass
is the backstop, run against a finished prose draft. The argument
names the draft: a file path, or the artifact it was published as.
If the draft exists only in the conversation, write it to the
scratchpad first, then run the checks against the file, so the pass
reads the text that will be committed or posted and not a memory of
it. Report each check's findings before rewriting, so the findings
are visible in the transcript as a record that the pass ran. Checks 1–3
correct toward expansion, Checks 4–5 toward deletion and order, and
Check 6 in whichever direction its lookup calls for. Run them 1, 2,
3, 6, 4, 5: the numbers name the checks, they do not sequence them,
and Check 6 was appended to the list after the rest. Two orderings
bind. Check 6 precedes Check 4, because an unbound parameter makes
a unit look like it carries nothing — "not copied literals" reads
as a defense with no durable reader until its mechanism is
supplied, so Check 4 reaching it first deletes the fact Check 6
would have rescued. Check 5 runs last, since it judges structure and needs the
content settled. Checks 1–3 and Check 4 commute, for the reason
Check 4 gives: they govern how a kept unit is serialized, it
governs which units are kept.
The pass governs prose artifacts only — never code comments, which
have their own contraction rules in CLAUDE.md's Code hygiene. It
detects encrypted phrases reliably (their expansion is absent from
the text, and a lookup exposes absence), syntactically obvious
stacks, and unlabeled fasteners (the glyphs are enumerable); it
under-detects compressed-but-complete phrases, which only the
write-time rule catches; it can flag but not always repair an
unlabeled edge, because repair needs the graph; Check 4's
reader test degrades once the drafting context is gone — the writer
knew which units were defensive, a later reader must infer it; and
Check 6 has nothing to enumerate, since an open place leaves no
pointer on the surface to list. When
you did not produce the draft — editing someone else's text, or
resuming after your writing context is gone — the pass is the only
defense available; run it knowing these blind spots.

Check 1 — expensive phrases. Detection is syntactic: a stack of three
or more nouns/modifiers before a head noun, or a phrase that carries
the confidence of an established term but was invented on the spot
(the Big Bang Theory tell — episode titles like "The Bath Item Gift
Hypothesis" dress a mundane event as terminology). Exempt: established
terms of art, whose expansion is already cached for the reader, and
short noun phrases that parse at a glance (headings are nominal by
convention). The remedy is to spend verbs and prepositions — write the
deleted relations out (who versions what, what leaks from where) — not
to define anything.

Check 2 — encrypted phrases. Detection is a lookup, not a judgment:
for each coined phrase and each definite reference ("the migration",
"the fix"), ask where in this document its expansion appears. If the
answer is "in the conversation" or "in my context", the phrase is
encrypted. Surface tells: "now", "previously", "originally", "changed
to", "as discussed", "we decided", "the issue we found" — and any
"the X" where X is neither introduced earlier in the document nor
common knowledge for the audience. The remedy depends on what kind of
pointer it is:

- Coined term: the missing payload is a definition. Used once, unpack
  it into plain prose. Used more than once, decide whether the concept
  deserves a name: if yes, define it at first use, in quotation marks,
  and use it consistently; if no, unpack every occurrence. Repetition
  creates the obligation to decide — it doesn't entitle the phrase to
  be a term. Mint few terms; each one taxes the reader.
- Event reference: the missing payload is a narration — who did what,
  in response to what. Either write the narration in full (this can
  triple the sentence's length; that is not verbosity), or drop the
  event entirely and describe the current state as if it were always
  so.
  Keep rationale that stays useful to a future reader (why the design
  is this way; a rejected alternative that's genuinely instructive);
  drop the narrative of how the conclusion was reached.
- When unsure whether a phrase is residue of the conversation, cut it.

Check 3 — unlabeled edges. Detection is enumeration: list every dash,
semicolon, parenthesis, adjacent sentence pair, and copular "X is Y"
between concepts (including synonyms like "means" or "amounts to"),
and name the relation each one carries in a word: cause, concession,
example, specification, contrast, definition, implementation. If you
cannot name it, the decision was never made — make it now. If you can,
ask whether the surface determines it for the reader: a colon passes
(its convention is narrow: "here comes the specification or reason");
an appositive dash straight after a noun phrase passes; chained
dashes, bare semicolons, parentheses hiding a claim's role, and a
bare copula between concepts fail. "Provisioning is --apply against
an empty store" asserts a relation while committing to none —
implementation, equivalence, definition — and the reader's guess
silently becomes their model of the system; the steps bring the
concept about, they are not the same thing as it. The remedy is to
word the edge, never to shorten the sentence: short sentences with
the connectives discarded fail the same way and read worse. Sentence
length was never the variable — long sentences with worded edges
read fine.

Check 4 — unearned units. The first three checks detect missing
serialization; this one detects units nothing needed. Three tests,
mechanical first:

- The flow test. Delete the candidate phrase or sentence; if no
  claim and no relation disappeared, it was scaffolding —
  throat-clearing, meta-narration, reader comfort, a summary
  restating what precedes it. Verify by dangling edges: a surviving
  "therefore" or "this" that now points at nothing means the unit
  carried an edge — restore it.
- The restatement lookup, Check 2's mirror. Check 2 asks where in
  this document a phrase's expansion appears; this asks where else
  the reader gets this claim. The unit fails if the answer names
  the same document or an artifact that travels with it: the diff
  beneath a commit message, a comment visible in that diff, the PR
  description beside it. One home per fact — each artifact keeps
  only what it alone can carry.
- The reader test. Name the reader who needs the unit and what they
  do with it. The historian deciding whether a revert is safe keeps
  the acceptability argument; the editor who would otherwise
  re-attempt a rejected alternative keeps that alternative, and the
  alternatives with no such editor go. A reader whose moment has
  passed keeps nothing: an argument aimed at whoever might have
  objected during review dies at merge. That reaches a clause
  answering a defect the reader might suspect ("not copied
  literals", "not a migration aid"), which is the same defense
  written before the objection instead of after it. Deleting it can
  strand a mechanism worth keeping, so state the mechanism instead:
  "the values are references, so rotating one propagates"
  documents permanently what the denial argues once. The writer is
  not a reader — a unit that justifies, hedges, or shows work fails.

The remedy is deleting whole units, never shortening kept ones. A
kept claim keeps its decompressed, decrypted, edge-worded
serialization; tightening it reintroduces the failures the first
three checks exist to catch. This is also why Check 4 cannot
conflict with them: they govern how to serialize what stays, it
governs what stays. And doubt keeps here, unlike Check 2, where
doubt cuts — an encrypted phrase is already useless to its reader,
but a wrongly deleted claim is a real loss. Resolve doubt through
the reader test: a nameable reader keeps the unit.

Check 5 — the skim test. Read only the headings and the first
sentence of each paragraph; what remains should be the whole
argument at low resolution — every claim the argument rests on
present and the relations among them still determined. The draft
fails where such a claim first appears mid-paragraph, after its own
support, or where a first sentence sets scene instead of stating a
claim. To tell a sentence that states its claim from one that only
labels what follows, ask which half a reader repeats to someone
else. "web-bff becomes a security-critical component: whatever it
asserts, backends believe" leads with the conclusion and supplies
its cause after, and passes. "That reframes several of the others
as the same defect" announces what is coming and carries nothing
on its own. The remedy is movement, not deletion: put the claim
first and demote its support below it. This check is what licenses
length — past a passing draft's first sentences, everything is
depth the reader opts into.

Check 6 — unbound parameters. Some words carry a meaning only once
a value is supplied for a place they leave open: "load-bearing"
means *removing it breaks X*, "meaningfully" means *by more than
T*, "better" means *greater along D*, "genuinely" means *as opposed
to apparent case C*, "cleanly" means *without failure mode F*,
"rather than" means *D favors this over that*. Write one with its
place empty and the sentence still parses, because an adjective in
a value position gives no sign that it is waiting on an argument.
The reader does not meet a claim they find vague; they meet an
expression they cannot evaluate. At the moment of writing, your own
context supplies the value, so the expression evaluates for you and
reads finished — which is why no reread catches this, and why it
belongs beside Checks 1 and 3: the same context assumption, working
inside a single word rather than across a phrase or between claims.

The word incurs a debt rather than committing an offense. Writing
it promises a value, payable anywhere in the unit, and the reader
extends credit on the assumption it is payable. Nothing is wrong at
the moment of writing, and the failure falls later, when the debt
goes unsettled — usually because you judged the reason self-evident,
which is a judgment made by the one party who already holds the
value. That is why this is a pass and not a habit: the sentence was
innocent when written, and by the time the promise is broken you
have moved past the word. Where the unit cannot continue — a
caption, a table cell, a selection criterion, a bullet with nothing
after it — no credit is possible and the word fails on the spot,
which is where these concentrate.

Detection is a rewrite, not a word list. Restate the sentence with
the place made explicit and a blank in it — "removing it breaks
___", "by more than ___", "greater in ___", "as opposed to ___".
Where the blank gets filled from decides the remedy:

- From the document, in the same unit or near it. The place is
  bound; leave the sentence alone. A nominalization ("names the
  anchored but not the anchor"), an ellipsis ("in that sentence it
  does"), or a pronoun with one nearby antecedent all bind it, and
  swapping a bound pointer for its referent buys nothing. This is
  the check's characteristic over-application.
- From your head only. Supply the value, then cut whatever support
  now restates it, since a bound expression makes its own expansion
  redundant. Where the place admits more than one true value — what
  the mechanism rests on, what the reader's grasp of everything
  downstream rests on — the document's job picks which to name. A
  true binding is not automatically the right one.
- From nowhere: you cannot fill the blank honestly. Then there was
  never an expression to keep. Delete the word rather than invent a
  value for it, because an unexplained choice stays visibly open to
  the next reader, while a manufactured reason reads exactly like a
  verified one and gets spent as a premise.
- From outside the document. That is Check 2 — apply its remedy,
  not this one.

Doubt resolves toward supplying, never toward leaving: leaving
requires positively finding the value, and a needless supply shows
up in the diff while a place left open shows nothing. Support
arriving in the next sentence does bind the place. What it does not
do is earn the word, which stays redundant beside the mechanism it
announced.

The words above are worked examples, not the rule. A word that
appears on no list fails the moment its blank refuses to be
written, and that is the whole test. The blind spot is Check 2's
method run backwards: Check 2 enumerates pointers and asks where
each expands, and an open place leaves no pointer on the surface to
enumerate.

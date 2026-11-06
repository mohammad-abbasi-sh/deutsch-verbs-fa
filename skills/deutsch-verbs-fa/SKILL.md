---
name: deutsch-verbs-fa
description: German verb conjugation for Persian speakers — conjugate any verb (Präsens, Präteritum, Perfekt, Futur I, Konjunktiv II, Imperativ) with a deterministic zero-dependency tool, handle separable/inseparable prefixes and haben/sein correctly, check a learner's German sentence for verb-form errors, drill with quizzes, and export Anki cards. Use when writing or correcting German for Persian-speaking learners, when an agent must not guess a verb form, or when building German-learning features. Never guess a conjugation — look it up.
---

# German verb conjugation for Persian speakers — look it up, never guess it

Persian has no grammatical gender and no verb conjugation like German's:
every German verb changes its form by person, tense and mood, strong
verbs change their stem vowel, separable verbs split in the sentence,
and Perfekt picks `haben` or `sein` by the verb — none of it is visible
in Persian. Agents answering from memory get these forms wrong
constantly, and a wrong form memorized once is hard to unlearn. This
skill makes conjugation **deterministic**: a zero-dependency engine plus
a hand-checked A1–B1 verb list (183 verbs — class, stem forms, auxiliary,
separable prefix, Persian gloss), with every explanation in Persian.

## The contract

1. **Never guess a verb form.** When German text is on the table, run
   the bundled tool (pure stdlib, no downloads, no API):

   ```bash
   python3 scripts/deutsch_verbs.py conjugate <verb> [--tense T] [--json]
   ```

   It prints the full paradigm — Präsens, Präteritum, Perfekt, Futur I,
   Konjunktiv II and Imperativ — with the separable prefix in its place
   (`ich komme an`, `ich bin angekommen`, `Kommen Sie an`) and the
   Persian gloss. If the verb is not in the curated list, the tool says
   so and suggests near matches — then check a dictionary. Exit codes:
   `0` = conjugated · `1` = verb not in the list · `2` = usage error.

2. **Explain the pattern, honestly.** Every verb carries its class
   (weak / strong / mixed / irregular), its stem change, its Perfekt
   auxiliary and its prefix behaviour. Use `rules` to get the Persian
   explanation:

   ```bash
   python3 scripts/deutsch_verbs.py rules ankommen
   python3 scripts/deutsch_verbs.py rules vergessen   # insep: no ge-, Partizip vergessen
   python3 scripts/deutsch_verbs.py rules wissen      # mixed: wusste, gewusst, wüsste
   ```

   See `references/conjugation-tables.md` for the full endings tables
   and `references/tense-guide.md` for when each tense is used and the
   haben/sein and separable-prefix rules.

3. **Check learner sentences conservatively.** The checker only flags
   what it can decide — a wrong person (`Ich geht` → `Ich gehe`), a
   wrong Perfekt auxiliary (`Ich habe gegangen` → `Ich bin gegangen`),
   an unseparated separable verb (`Ich ankomme` → `Ich komme an`), a
   wrong `werden` form in Futur I:

   ```bash
   python3 scripts/deutsch_verbs.py check "Ich habe gegangen" [--json]
   # → «gehen» با «sein» گذشته می‌سازد، نه «haben» — درستش: Ich bin gegangen
   ```

   Exit codes: `0` = no findings · `1` = findings · `2` = usage error.
   **No finding is not a proof of correctness** — say that when
   reporting. Word order, subordinate clauses and vocabulary are out of
   scope; the checker only judges verb forms it can decide.

4. **Drill and export.** `quiz [--n 5] [--level A1] [--seed N]
   [--answers a,b,c]` runs an interactive drill (seeded sets are
   reproducible); `anki [--level A1] [--tenses präsens,perfekt]
   [--out cards.tsv]` exports the whole list as Anki-importable TSV
   (front: infinitive + Persian gloss + tense + person, back: the
   correct form).

## Know the limits — and say them

- The curated list is A1–B1 core vocabulary (183 verbs, v1.0.0). It does
  not replace a dictionary or a conjugator for verbs outside it.
- The sentence checker is deliberately conservative: it handles simple
  sentences (pronoun + finite form, pronoun + auxiliary + Partizip II,
  pronoun + werden + infinitive). Complex sentences are left alone
  rather than guessed.
- Konjunktiv II of weak verbs equals their Präteritum (the tool says so);
  the polite `würde + Infinitiv` alternative is noted in the tense
  guide, not generated as a separate paradigm.
- Modal verbs have no usable imperative — the tool reports that instead
  of inventing one.
- This is a deterministic reference, not a teacher: it cannot judge
  style, word choice or whether a sentence sounds natural.

## Layout

- `scripts/deutsch_verbs.py` — the engine (conjugation, rules, checker,
  quiz, Anki export). Loads `data/verbs.json` relative to itself.
- `data/verbs.json` — the hand-checked verb list. Contributions welcome:
  keep the schema (`inf`, `fa`, `level` ∈ A1/A2/B1, `cls` ∈
  weak/strong/mixed/irregular, `aux` ∈ haben/sein, `sep` prefix or
  null, `insep` bool, `change` ∈ a>ä/e>i/e>ie, `praet`, `part2`),
  and verify every form against a dictionary before adding.
- `references/conjugation-tables.md` — the full endings tables
  (weak/strong/mixed, stem-change, -e- insertion, imperative).
- `references/tense-guide.md` — when to use each tense, haben vs.
  sein, separable vs. inseparable prefixes, and the common traps.

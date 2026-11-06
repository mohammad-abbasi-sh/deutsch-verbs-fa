# deutsch-verbs-fa — German verb conjugation for Persian speakers

A deterministic **Agent Skill** for the other half of German grammar
that Persian speakers trip over daily: verb conjugation. After
[`deutsch-fa`](https://github.com/mohammad-abbasi-sh/deutsch-fa)
(der/die/das + 4 cases), this is the sequel — *gehen* vs *ging* vs
*gegangen*, *haben* vs *sein*, separable prefixes that split in the
sentence, and the stem changes agents guess wrong.

Persian has no verb conjugation like German's: no person endings, no
stem-vowel changes, no separable prefixes, no haben/sein choice in the
past. `deutsch-verbs-fa` makes every form **deterministic**: a
zero-dependency Python engine plus a hand-checked A1–B1 verb list
(183 verbs — class, stem forms, auxiliary, prefix, Persian gloss),
with every explanation in Persian.

No model calls. No downloads. No API keys. Python 3.8+ standard library
only.

## The problem

```
Learner writes:   Ich habe gegangen.     /  Ich ankomme.
Agent (guessing): looks fine ✓           ← wrong twice, and now the
                                           learner memorizes both errors

With deutsch-verbs-fa:
$ python3 scripts/deutsch_verbs.py check "Ich habe gegangen"
✗ «gehen» با «sein» گذشته می‌سازد، نه «haben».
  درستش: Ich bin gegangen

$ python3 scripts/deutsch_verbs.py check "Ich ankomme"
✗ فعل جداشدنی «ankommen» در جمله جدا می‌شود: پیشوند «an» به انتهای جمله می‌رود.
  درستش: Ich komme an
```

Before/after, from the engine:

| Before (guessed) | After (deutsch-verbs-fa) |
|---|---|
| *Ich geht* | *Ich **gehe*** — person ending, not a guess |
| *Ich habe gegangen* | *Ich **bin** gegangen* — gehen takes sein |
| *Ich ankomme* | *Ich komme **an*** — separable prefix splits |
| *du fahrst* | *du **fährst*** — a → ä stem change |
| *du nehmst* | *du **nimmst*** — nehm- → nimm-, the h drops |
| *er rät* (as *rätt*) | *er **rät*** — no doubled -t |
| *Könn!* | *(no imperative)* — modals have none, the tool says so |

## What's inside

```
skills/deutsch-verbs-fa/
  SKILL.md                  the agent skill (the contract)
  scripts/deutsch_verbs.py  the engine — conjugate, rules, check, quiz, anki
  data/verbs.json           183 hand-checked A1–B1 verbs (inf/fa/level/cls/aux/sep/...)
  references/
    conjugation-tables.md   full endings tables (weak/strong/mixed, -e- insertion)
    tense-guide.md          when to use each tense, haben vs. sein, prefixes, traps
cursor/deutsch-verbs-fa.mdc the Cursor rule (same contract, condensed)
mcp-server/                 MCP server (stdio) exposing 5 tools
tests/                      48 tests, all passing (stdlib unittest)
dist/deutsch-verbs-fa-skill.zip   ready-to-upload Claude.ai skill bundle
```

Commands:

```bash
python3 scripts/deutsch_verbs.py conjugate gehen
# full paradigm: Präsens, Präteritum, Perfekt, Futur I, Konjunktiv II, Imperativ

python3 scripts/deutsch_verbs.py conjugate ankommen --tense perfekt
python3 scripts/deutsch_verbs.py conjugate fahren --json
python3 scripts/deutsch_verbs.py rules vergessen     # Persian explanation
python3 scripts/deutsch_verbs.py check "Ich habe gegangen"
python3 scripts/deutsch_verbs.py quiz --n 5 --level A1 --seed 42
python3 scripts/deutsch_verbs.py anki --out cards.tsv   # 2,196 cards
python3 scripts/deutsch_verbs.py list --level A2 --cls strong
```

## Install

**Claude Code** — copy `skills/deutsch-verbs-fa/` into your project's
skills directory (or `~/.claude/skills/` for global use). The skill's
`SKILL.md` frontmatter makes it discoverable; the script path in the
commands is relative to the skill directory.

**Claude.ai** — upload `dist/deutsch-verbs-fa-skill.zip` as a skill (the
zip contains `SKILL.md`, the script, the verb data and the references).

**Cursor** — copy `cursor/deutsch-verbs-fa.mdc` to `.cursor/rules/` and
`skills/deutsch-verbs-fa/` into your project. Windsurf / Cline /
Continue: see `cursor/README.md`.

**Any MCP client** — point your client at the stdio server:

```json
{
  "mcpServers": {
    "deutsch-verbs-fa": {
      "command": "python3",
      "args": ["/path/to/mcp-server/deutsch_verbs_mcp_server.py"]
    }
  }
}
```

Tools: `conjugate`, `check_sentence`, `quiz`, `anki_export`,
`list_verbs`.

## Why not just another app?

Conjugation websites (verbformen.com, Cooljugator) and apps (the
"14000 German verbs" app, which even has a Persian translation) are
*reference works for learners* — this is a *tool for agents*:
deterministic, scriptable, CI-friendly, with JSON output, a sentence
checker, quizzes and an MCP interface, so a tutor agent, a content
pipeline or a classroom bot can conjugate, check and drill without
guessing. The 183-verb dataset is original and hand-checked; the engine
encodes the standard reference grammar (stem changes, -e- insertion,
t-merging, separable/inseparable prefixes, haben/sein, Konjunktiv II,
the senden/wenden exception, modal verbs with no imperative).

## Honest limits

- The list is A1–B1 core vocabulary (v1.0.0) — not a dictionary for
  verbs outside it; unknown verbs get a labelled *not in the list*,
  not an answer.
- The sentence checker is deliberately conservative: simple sentences
  only (pronoun + finite form, pronoun + auxiliary + Partizip II,
  pronoun + werden + infinitive). No finding ≠ correct.
- Konjunktiv II of weak verbs equals their Präteritum; the polite
  *würde + Infinitiv* alternative is documented, not generated.
- A deterministic reference, not a teacher: no judgment on style or
  naturalness.

## Roadmap

- Grow the verb list toward 300 (B2), community contributions welcome
  (schema in `SKILL.md` — verify every form against a dictionary).
- Example sentence per verb (hand-written, case-correct).
- Spaced-repetition scheduling for `quiz`.
- Subordinate-clause and reflexive-verb coverage for `check`.

## License

MIT — see LICENSE.

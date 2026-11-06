# Cursor — deutsch-verbs-fa rule

`cursor/deutsch-verbs-fa.mdc` is the Cursor version of this skill. It carries
the same contract in condensed form: never guess a verb form (conjugate
with the tool), place separable prefixes correctly, pick haben/sein by
the verb, check learner sentences conservatively, and state the limits.

## Install — Cursor

Copy `cursor/deutsch-verbs-fa.mdc` into your project's `.cursor/rules/`
directory (create it if needed). Cursor applies it automatically. The
rule points at the engine script — copy the whole
`skills/deutsch-verbs-fa/` directory into your project, or install the
engine where the rule's commands can find it.

## Install — Windsurf

Copy `cursor/deutsch-verbs-fa.mdc` to `.windsurf/rules/deutsch-verbs-fa.mdc`
in your project. Windsurf loads `.mdc` rules from that directory. Copy
`skills/deutsch-verbs-fa/` alongside it so the script paths resolve.

## Install — Cline / Continue

Cline and Continue use plain Markdown rules:

- **Cline:** copy the contents of `cursor/deutsch-verbs-fa.mdc` (without the
  frontmatter block) into `.clinerules/deutsch-verbs-fa.md`, and copy
  `skills/deutsch-verbs-fa/` into your project.
- **Continue:** copy the same Markdown body into
  `.continue/rules/deutsch-verbs-fa.md`, and copy `skills/deutsch-verbs-fa/`
  into your project.

In both cases the rule's commands assume the engine lives at
`skills/deutsch-verbs-fa/scripts/deutsch_verbs.py` relative to the project
root — keep that layout.

## What it covers

- The no-guessing contract (conjugate with the tool, not from memory).
- Stem changes, -e- insertion, t-merging, separable/inseparable
  prefixes, haben vs. sein.
- Conservative sentence checking (wrong person, wrong auxiliary,
  unseparated prefix, wrong werden form) — and the "no finding ≠ correct"
  rule.
- Quiz drills and Anki export (2,196 cards).
- The limits (A1–B1 list is not a dictionary; reference, not a teacher).

The full skill with references and the MCP server lives in
`skills/deutsch-verbs-fa/` and `mcp-server/`.

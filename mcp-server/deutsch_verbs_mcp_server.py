#!/usr/bin/env python3
"""MCP server for deutsch-verbs-fa — expose the German verb conjugation
engine as tools for any MCP client.

Zero-dependency (Python standard library only). Speaks JSON-RPC 2.0
over stdio, newline-delimited, following the MCP lifecycle:

    initialize -> notifications/initialized -> tools/list -> tools/call

Tools:
    conjugate
        verb    German infinitive (required)
        tense   präsens | präteritum | perfekt | futur1 | konjunktiv2 |
                imperativ (default: all)
        format  "text" (default) or "json"
    check_sentence
        sentence  German sentence to check (required)
        format    "text" (default) or "json"
    quiz
        n       number of questions (default 5)
        level   A1 | A2 | B1 (optional)
        seed    integer seed for a reproducible set (optional)
        answers comma-separated answers to score non-interactively
    anki_export
        level   A1 | A2 | B1 (optional)
        tenses  comma-separated tenses, default "präsens,perfekt"
    list_verbs
        level   A1 | A2 | B1 (optional)
        cls     weak | strong | mixed | irregular (optional)

The server runs skills/deutsch-verbs-fa/scripts/deutsch_verbs.py as a
subprocess; exit-code semantics are preserved in the returned text
(conjugate: 1 = verb not in the curated list; check: 1 = findings).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / "skills" / "deutsch-verbs-fa" / "scripts" / "deutsch_verbs.py"

SERVER_INFO = {"name": "deutsch-verbs-fa", "version": "1.0.0"}
PROTOCOL_VERSION = "2024-11-05"


def run_cli(*args):
    proc = subprocess.run([sys.executable, str(ENGINE), *args],
                          capture_output=True, text=True, timeout=120)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def _with_exit(code, out, err):
    lines = []
    if out:
        lines.append(out)
    if err:
        lines.append("stderr: " + err)
    return "\n".join(lines)


def tool_conjugate(args):
    verb = args.get("verb")
    if not verb:
        raise ValueError("conjugate requires 'verb'")
    cmd = ["conjugate", verb]
    if args.get("tense"):
        cmd += ["--tense", args["tense"]]
    if args.get("format") == "json":
        cmd.append("--json")
    code, out, err = run_cli(*cmd)
    return _with_exit(code, out, err)


def tool_check_sentence(args):
    sentence = args.get("sentence")
    if not sentence:
        raise ValueError("check_sentence requires 'sentence'")
    cmd = ["check", sentence]
    if args.get("format") == "json":
        cmd.append("--json")
    code, out, err = run_cli(*cmd)
    return _with_exit(code, out, err)


def tool_quiz(args):
    cmd = ["quiz"]
    if args.get("n"):
        cmd += ["--n", str(args["n"])]
    if args.get("level"):
        cmd += ["--level", args["level"]]
    if args.get("seed") is not None:
        cmd += ["--seed", str(args["seed"])]
    if args.get("answers"):
        cmd += ["--answers", args["answers"]]
    code, out, err = run_cli(*cmd)
    return _with_exit(code, out, err)


def tool_anki_export(args):
    cmd = ["anki"]
    if args.get("level"):
        cmd += ["--level", args["level"]]
    if args.get("tenses"):
        cmd += ["--tenses", args["tenses"]]
    code, out, err = run_cli(*cmd)
    lines = [f"anki exit code: {code}",
             f"{len(out.splitlines())} cards (TSV: front<TAB>back)"]
    if out:
        lines.append(out)
    if err:
        lines.append("stderr: " + err)
    return "\n".join(lines)


def tool_list_verbs(args):
    cmd = ["list"]
    if args.get("level"):
        cmd += ["--level", args["level"]]
    if args.get("cls"):
        cmd += ["--cls", args["cls"]]
    code, out, err = run_cli(*cmd)
    return _with_exit(code, out, err)


TOOLS = [
    {
        "name": "conjugate",
        "description": (
            "Conjugate a German verb: full paradigm across Prasens, "
            "Prateritum, Perfekt, Futur I, Konjunktiv II and Imperativ, "
            "with the Persian gloss — from a hand-checked A1-B1 list of "
            "183 verbs. Separable prefixes are placed correctly (komme an, "
            "angekommen). Use instead of guessing a verb form. Answers in "
            "German with Persian explanations."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "verb": {"type": "string",
                         "description": "German infinitive, e.g. gehen, ankommen"},
                "tense": {"type": "string",
                          "enum": ["präsens", "präteritum", "perfekt",
                                   "futur1", "konjunktiv2", "imperativ"],
                          "description": "one tense, or omit for the full paradigm"},
                "format": {"type": "string", "enum": ["text", "json"],
                           "description": "output format (default text)"},
            },
            "required": ["verb"],
        },
    },
    {
        "name": "check_sentence",
        "description": (
            "Check a Persian-speaking learner's German sentence for "
            "verb-form errors — wrong person, wrong Perfekt auxiliary "
            "(haben/sein), unseparated separable verbs — only where "
            "deterministically decidable. Conservative: no finding does "
            "not mean the sentence is perfect. Explanations in Persian."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "sentence": {"type": "string",
                             "description": "German sentence to check"},
                "format": {"type": "string", "enum": ["text", "json"],
                           "description": "output format (default text)"},
            },
            "required": ["sentence"],
        },
    },
    {
        "name": "quiz",
        "description": (
            "Drill German verb conjugation: random questions (verb + tense "
            "+ person) from the curated A1-B1 list, with scoring. Pass "
            "answers to score non-interactively; pass a seed for a "
            "reproducible set."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "n": {"type": "integer",
                      "description": "number of questions (default 5)"},
                "level": {"type": "string", "enum": ["A1", "A2", "B1"],
                          "description": "restrict to one level"},
                "seed": {"type": "integer",
                         "description": "seed for a reproducible question set"},
                "answers": {"type": "string",
                            "description": "comma-separated answers to score"},
            },
        },
    },
    {
        "name": "anki_export",
        "description": (
            "Export the curated verb list as Anki-importable TSV "
            "(front: infinitive + Persian gloss + tense + person; back: "
            "the correct form). Default tenses: prasens + perfekt."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {"type": "string", "enum": ["A1", "A2", "B1"],
                          "description": "restrict to one level"},
                "tenses": {"type": "string",
                           "description": "comma-separated tenses, e.g. präsens,perfekt"},
            },
        },
    },
    {
        "name": "list_verbs",
        "description": (
            "List the curated verbs (infinitive, level, class, Persian "
            "gloss), optionally filtered by level or class."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "level": {"type": "string", "enum": ["A1", "A2", "B1"]},
                "cls": {"type": "string",
                        "enum": ["weak", "strong", "mixed", "irregular"]},
            },
        },
    },
]

HANDLERS = {
    "conjugate": tool_conjugate,
    "check_sentence": tool_check_sentence,
    "quiz": tool_quiz,
    "anki_export": tool_anki_export,
    "list_verbs": tool_list_verbs,
}


def handle(request):
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": SERVER_INFO,
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if method == "tools/list":
        return {
            "jsonrpc": "2.0", "id": req_id,
            "result": {"tools": TOOLS},
        }
    if method == "tools/call":
        name = params.get("name")
        arguments = params.get("arguments") or {}
        handler = HANDLERS.get(name)
        if handler is None:
            return {
                "jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32602,
                          "message": f"unknown tool: {name}"},
            }
        try:
            text = handler(arguments)
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text", "text": text}]},
            }
        except Exception as exc:  # noqa: BLE001 - surface as tool error
            return {
                "jsonrpc": "2.0", "id": req_id,
                "result": {"content": [{"type": "text",
                                        "text": f"error: {exc}"}],
                           "isError": True},
            }
    return {
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": -32601, "message": f"method not found: {method}"},
    }


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue
        response = handle(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()

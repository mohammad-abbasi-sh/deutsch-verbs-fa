#!/usr/bin/env python3
"""Tests for the deutsch-verbs-fa MCP server (stdio JSON-RPC)."""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SERVER = os.path.join(ROOT, "mcp-server", "deutsch_verbs_mcp_server.py")


def session(requests):
    """Feed a list of JSON-RPC requests, return parsed responses."""
    payload = "\n".join(json.dumps(r) for r in requests) + "\n"
    proc = subprocess.run([sys.executable, SERVER], input=payload,
                          capture_output=True, text=True, timeout=120)
    out = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return proc.returncode, out


class TestMCP(unittest.TestCase):
    def test_initialize_and_list(self):
        code, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        ])
        self.assertEqual(code, 0)
        self.assertEqual(len(resps), 2)
        self.assertEqual(resps[0]["result"]["serverInfo"]["name"], "deutsch-verbs-fa")
        names = [t["name"] for t in resps[1]["result"]["tools"]]
        self.assertEqual(names, ["conjugate", "check_sentence", "quiz",
                                 "anki_export", "list_verbs"])

    def test_conjugate(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "conjugate",
                        "arguments": {"verb": "gehen", "tense": "perfekt"}}},
        ])
        text = resps[0]["result"]["content"][0]["text"]
        self.assertIn("bin gegangen", text)

    def test_conjugate_json(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "conjugate",
                        "arguments": {"verb": "fahren", "format": "json"}}},
        ])
        text = resps[0]["result"]["content"][0]["text"]
        data = json.loads(text)
        self.assertEqual(data["paradigm"]["präsens"]["du"], "fährst")

    def test_check_sentence(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "check_sentence",
                        "arguments": {"sentence": "Ich habe gegangen"}}},
        ])
        text = resps[0]["result"]["content"][0]["text"]
        self.assertIn("Ich bin gegangen", text)

    def test_quiz_seeded(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "quiz",
                        "arguments": {"n": 2, "seed": 11, "answers": "x,y"}}},
        ])
        text = resps[0]["result"]["content"][0]["text"]
        self.assertIn("نتیجه: 0 از 2", text)

    def test_list_verbs(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "list_verbs",
                        "arguments": {"level": "A1"}}},
        ])
        text = resps[0]["result"]["content"][0]["text"]
        self.assertIn("89 فعل", text)
        self.assertIn("gehen", text)

    def test_anki_export(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "anki_export",
                        "arguments": {"level": "A1"}}},
        ])
        text = resps[0]["result"]["content"][0]["text"]
        self.assertIn("1068 cards", text)  # 89 A1 verbs x 12 cards

    def test_unknown_tool(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "nope", "arguments": {}}},
        ])
        self.assertIn("error", resps[0])

    def test_missing_argument(self):
        _, resps = session([
            {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
             "params": {"name": "conjugate", "arguments": {}}},
        ])
        self.assertTrue(resps[0]["result"].get("isError"))


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Tests for deutsch-verbs-fa — run: python3 -m unittest discover -s tests -v"""
import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPT = os.path.join(ROOT, "skills", "deutsch-verbs-fa", "scripts", "deutsch_verbs.py")
DATA = os.path.join(ROOT, "skills", "deutsch-verbs-fa", "data", "verbs.json")
sys.path.insert(0, os.path.join(ROOT, "skills", "deutsch-verbs-fa", "scripts"))
import deutsch_verbs as dv


def run(*args):
    return subprocess.run([sys.executable, SCRIPT, *args],
                          capture_output=True, text=True)


class TestWeakVerbs(unittest.TestCase):
    def test_lernen_full(self):
        v = dv.lookup("lernen")
        self.assertEqual(dv.praesens(v),
                         ["lerne", "lernst", "lernt", "lernen", "lernt", "lernen"])
        self.assertEqual(dv.praeteritum(v),
                         ["lernte", "lerntest", "lernte", "lernten", "lerntet", "lernten"])
        self.assertEqual(dv.perfekt(v)[0], "habe gelernt")
        self.assertEqual(dv.futur1(v)[1], "wirst lernen")
        self.assertEqual(dv.konjunktiv2(v), dv.praeteritum(v))
        self.assertEqual(dv.imperativ(v), ("lern", "lernt", "lernen Sie"))

    def test_dt_stem_insertion(self):
        self.assertEqual(dv.praesens(dv.lookup("arbeiten"))[1], "arbeitest")
        self.assertEqual(dv.praesens(dv.lookup("arbeiten"))[2], "arbeitet")
        self.assertEqual(dv.praesens(dv.lookup("finden"))[1], "findest")
        self.assertEqual(dv.praesens(dv.lookup("antworten"))[4], "antwortet")
        self.assertEqual(dv.partizip2(dv.lookup("arbeiten")), "gearbeitet")
        self.assertEqual(dv.partizip2(dv.lookup("enden")), "geendet")

    def test_no_insertion_mm_nn_h(self):
        # kommen/stimmen/beginnen: no -e- (mm/nn); wohnen: single h, no -e-
        self.assertEqual(dv.praesens(dv.lookup("kommen"))[1], "kommst")
        self.assertEqual(dv.praesens(dv.lookup("stimmen"))[1], "stimmst")
        self.assertEqual(dv.praesens(dv.lookup("beginnen"))[1], "beginnst")
        self.assertEqual(dv.praesens(dv.lookup("wohnen"))[1], "wohnst")
        self.assertEqual(dv.praesens(dv.lookup("lernen"))[1], "lernst")

    def test_ieren_no_ge(self):
        self.assertEqual(dv.partizip2(dv.lookup("studieren")), "studiert")
        self.assertEqual(dv.partizip2(dv.lookup("telefonieren")), "telefoniert")
        self.assertEqual(dv.partizip2(dv.lookup("passieren")), "passiert")

    def test_s_stem(self):
        self.assertEqual(dv.praesens(dv.lookup("reisen"))[1], "reist")
        self.assertEqual(dv.praesens(dv.lookup("heißen"))[1], "heißt")
        self.assertEqual(dv.praesens(dv.lookup("sitzen"))[1], "sitzt")
        self.assertEqual(dv.praesens(dv.lookup("tanzen"))[1], "tanzt")


class TestStrongVerbs(unittest.TestCase):
    def test_stem_change_a_umlaut(self):
        self.assertEqual(dv.praesens(dv.lookup("fahren"))[1], "fährst")
        self.assertEqual(dv.praesens(dv.lookup("fahren"))[2], "fährt")
        self.assertEqual(dv.praesens(dv.lookup("fahren"))[4], "fahrt")
        self.assertEqual(dv.praesens(dv.lookup("schlafen"))[1], "schläfst")
        self.assertEqual(dv.praesens(dv.lookup("laufen"))[1], "läufst")
        self.assertEqual(dv.praesens(dv.lookup("tragen"))[2], "trägt")
        self.assertEqual(dv.praesens(dv.lookup("waschen"))[1], "wäschst")
        self.assertEqual(dv.praesens(dv.lookup("wachsen"))[1], "wächst")

    def test_stem_change_e_to_i(self):
        self.assertEqual(dv.praesens(dv.lookup("essen"))[1], "isst")
        self.assertEqual(dv.praesens(dv.lookup("geben"))[1], "gibst")
        self.assertEqual(dv.praesens(dv.lookup("nehmen"))[1], "nimmst")
        self.assertEqual(dv.praesens(dv.lookup("sprechen"))[1], "sprichst")
        self.assertEqual(dv.praesens(dv.lookup("helfen"))[2], "hilft")
        self.assertEqual(dv.praesens(dv.lookup("treffen"))[1], "triffst")
        self.assertEqual(dv.praesens(dv.lookup("werfen"))[1], "wirfst")
        self.assertEqual(dv.praesens(dv.lookup("brechen"))[2], "bricht")
        self.assertEqual(dv.praesens(dv.lookup("sterben"))[1], "stirbst")
        self.assertEqual(dv.praesens(dv.lookup("gelten"))[1], "giltst")
        self.assertEqual(dv.praesens(dv.lookup("vergessen"))[1], "vergisst")

    def test_stem_change_e_to_ie(self):
        self.assertEqual(dv.praesens(dv.lookup("sehen"))[1], "siehst")
        self.assertEqual(dv.praesens(dv.lookup("lesen"))[1], "liest")
        self.assertEqual(dv.praesens(dv.lookup("stehlen"))[1], "stiehlst")
        self.assertEqual(dv.praesens(dv.lookup("empfehlen"))[2], "empfiehlt")
        self.assertEqual(dv.praesens(dv.lookup("geschehen"))[1], "geschiehst")

    def test_er_t_merge(self):
        # changed stem ending in -t + -t ending merge: rät, hält, gilt, lädt
        self.assertEqual(dv.praesens(dv.lookup("raten"))[2], "rät")
        self.assertEqual(dv.praesens(dv.lookup("halten"))[2], "hält")
        self.assertEqual(dv.praesens(dv.lookup("gelten"))[2], "gilt")
        self.assertEqual(dv.conjugate(dv.lookup("einladen"), "präsens")[2], "lädt ein")
        self.assertEqual(dv.praesens(dv.lookup("raten"))[4], "ratet")
        self.assertEqual(dv.praesens(dv.lookup("halten"))[4], "haltet")

    def test_praeteritum_strong(self):
        self.assertEqual(dv.praeteritum(dv.lookup("gehen"))[0], "ging")
        self.assertEqual(dv.praeteritum(dv.lookup("finden"))[1], "fandest")
        self.assertEqual(dv.praeteritum(dv.lookup("lesen"))[1], "lasest")
        self.assertEqual(dv.praeteritum(dv.lookup("bitten"))[1], "batest")
        self.assertEqual(dv.praeteritum(dv.lookup("stehen"))[1], "standest")
        self.assertEqual(dv.praeteritum(dv.lookup("sitzen"))[1], "saßest")
        self.assertEqual(dv.praeteritum(dv.lookup("vergessen"))[1], "vergaßest")
        self.assertEqual(dv.praeteritum(dv.lookup("gehen"))[4], "gingt")
        self.assertEqual(dv.praeteritum(dv.lookup("finden"))[4], "fandet")

    def test_partizip2_strong(self):
        self.assertEqual(dv.partizip2(dv.lookup("gehen")), "gegangen")
        self.assertEqual(dv.partizip2(dv.lookup("sehen")), "gesehen")
        self.assertEqual(dv.partizip2(dv.lookup("essen")), "gegessen")
        self.assertEqual(dv.partizip2(dv.lookup("nehmen")), "genommen")

    def test_perfekt_aux_sein(self):
        self.assertEqual(dv.perfekt(dv.lookup("gehen"))[0], "bin gegangen")
        self.assertEqual(dv.perfekt(dv.lookup("kommen"))[0], "bin gekommen")
        self.assertEqual(dv.perfekt(dv.lookup("bleiben"))[0], "bin geblieben")
        self.assertEqual(dv.perfekt(dv.lookup("fahren"))[0], "bin gefahren")
        self.assertEqual(dv.perfekt(dv.lookup("lernen"))[0], "habe gelernt")

    def test_konjunktiv2_strong(self):
        self.assertEqual(dv.konjunktiv2(dv.lookup("gehen"))[0], "ginge")
        self.assertEqual(dv.konjunktiv2(dv.lookup("fahren"))[0], "führe")
        self.assertEqual(dv.konjunktiv2(dv.lookup("kommen"))[0], "käme")
        self.assertEqual(dv.konjunktiv2(dv.lookup("sehen"))[0], "sähe")
        self.assertEqual(dv.konjunktiv2(dv.lookup("essen"))[0], "äße")
        self.assertEqual(dv.konjunktiv2(dv.lookup("sein"))[0], "wäre")
        self.assertEqual(dv.konjunktiv2(dv.lookup("haben"))[0], "hätte")
        self.assertEqual(dv.konjunktiv2(dv.lookup("werden"))[0], "würde")


class TestMixedAndIrregular(unittest.TestCase):
    def test_wissen(self):
        v = dv.lookup("wissen")
        self.assertEqual(dv.praesens(v),
                         ["weiß", "weißt", "weiß", "wissen", "wisst", "wissen"])
        self.assertEqual(dv.praeteritum(v)[0], "wusste")
        self.assertEqual(dv.praeteritum(v)[3], "wussten")
        self.assertEqual(dv.partizip2(v), "gewusst")
        self.assertEqual(dv.konjunktiv2(v)[0], "wüsste")
        self.assertEqual(dv.imperativ(v), ("wisse", "wisst", "wissen Sie"))

    def test_mixed_verbs(self):
        self.assertEqual(dv.praeteritum(dv.lookup("denken"))[0], "dachte")
        self.assertEqual(dv.praeteritum(dv.lookup("denken"))[3], "dachten")
        self.assertEqual(dv.konjunktiv2(dv.lookup("denken"))[0], "dächte")
        self.assertEqual(dv.praeteritum(dv.lookup("bringen"))[0], "brachte")
        self.assertEqual(dv.konjunktiv2(dv.lookup("bringen"))[0], "brächte")
        self.assertEqual(dv.praeteritum(dv.lookup("kennen"))[3], "kannten")
        self.assertEqual(dv.praeteritum(dv.lookup("rennen"))[0], "rannte")
        self.assertEqual(dv.partizip2(dv.lookup("rennen")), "gerannt")
        self.assertEqual(dv.perfekt(dv.lookup("rennen"))[0], "bin gerannt")
        self.assertEqual(dv.konjunktiv2(dv.lookup("senden"))[0], "sendete")
        self.assertEqual(dv.konjunktiv2(dv.lookup("wenden"))[0], "wendete")

    def test_sein_haben_werden(self):
        self.assertEqual(dv.praesens(dv.lookup("sein")),
                         ["bin", "bist", "ist", "sind", "seid", "sind"])
        self.assertEqual(dv.praeteritum(dv.lookup("sein"))[0], "war")
        self.assertEqual(dv.partizip2(dv.lookup("sein")), "gewesen")
        self.assertEqual(dv.praesens(dv.lookup("haben"))[1], "hast")
        self.assertEqual(dv.praeteritum(dv.lookup("haben"))[0], "hatte")
        self.assertEqual(dv.praesens(dv.lookup("werden"))[1], "wirst")
        self.assertEqual(dv.praeteritum(dv.lookup("werden"))[0], "wurde")
        self.assertEqual(dv.partizip2(dv.lookup("werden")), "geworden")

    def test_modals(self):
        self.assertEqual(dv.praesens(dv.lookup("können"))[0], "kann")
        self.assertEqual(dv.praesens(dv.lookup("müssen"))[0], "muss")
        self.assertEqual(dv.praesens(dv.lookup("wollen"))[0], "will")
        self.assertEqual(dv.praesens(dv.lookup("sollen"))[0], "soll")
        self.assertEqual(dv.praesens(dv.lookup("dürfen"))[0], "darf")
        self.assertEqual(dv.praesens(dv.lookup("mögen"))[0], "mag")
        self.assertEqual(dv.praesens(dv.lookup("möchten"))[0], "möchte")
        self.assertEqual(dv.konjunktiv2(dv.lookup("können"))[0], "könnte")
        self.assertEqual(dv.konjunktiv2(dv.lookup("müssen"))[0], "müsste")
        self.assertEqual(dv.konjunktiv2(dv.lookup("dürfen"))[0], "dürfte")
        self.assertEqual(dv.praeteritum(dv.lookup("möchten"))[0], "wollte")
        self.assertIsNone(dv.imperativ(dv.lookup("können")))
        self.assertIsNone(dv.imperativ(dv.lookup("müssen")))
        self.assertIsNone(dv.conjugate(dv.lookup("können"), "imperativ"))


class TestSeparableInseparable(unittest.TestCase):
    def test_separable(self):
        v = dv.lookup("ankommen")
        self.assertEqual(dv.conjugate(v, "präsens")[0], "komme an")
        self.assertEqual(dv.conjugate(v, "präsens")[1], "kommst an")
        self.assertEqual(dv.conjugate(v, "präteritum")[0], "kam an")
        self.assertEqual(dv.partizip2_full(v), "angekommen")
        self.assertEqual(dv.perfekt(v)[0], "bin angekommen")
        self.assertEqual(dv.futur1(v)[0], "werde ankommen")
        self.assertEqual(dv.conjugate(v, "konjunktiv2")[0], "käme an")
        self.assertEqual(dv.imperativ(v), ("komm an", "kommt an", "kommen Sie an"))

    def test_separable_more(self):
        self.assertEqual(dv.partizip2_full(dv.lookup("aufstehen")), "aufgestanden")
        self.assertEqual(dv.partizip2_full(dv.lookup("einkaufen")), "eingekauft")
        self.assertEqual(dv.partizip2_full(dv.lookup("anrufen")), "angerufen")
        self.assertEqual(dv.partizip2_full(dv.lookup("fernsehen")), "ferngesehen")
        self.assertEqual(dv.partizip2_full(dv.lookup("abfahren")), "abgefahren")
        self.assertEqual(dv.partizip2_full(dv.lookup("einladen")), "eingeladen")
        self.assertEqual(dv.partizip2_full(dv.lookup("aussehen")), "ausgesehen")
        self.assertEqual(dv.partizip2_full(dv.lookup("einsteigen")), "eingestiegen")
        self.assertEqual(dv.partizip2_full(dv.lookup("umziehen")), "umgezogen")
        self.assertEqual(dv.partizip2_full(dv.lookup("zurückkommen")), "zurückgekommen")
        self.assertEqual(dv.conjugate(dv.lookup("anfangen"), "präsens")[1], "fängst an")
        self.assertEqual(dv.imperativ(dv.lookup("mitmachen"))[0], "mach mit")

    def test_inseparable_no_ge(self):
        self.assertEqual(dv.partizip2_full(dv.lookup("bekommen")), "bekommen")
        self.assertEqual(dv.partizip2_full(dv.lookup("verstehen")), "verstanden")
        self.assertEqual(dv.partizip2_full(dv.lookup("vergessen")), "vergessen")
        self.assertEqual(dv.partizip2_full(dv.lookup("beginnen")), "begonnen")
        self.assertEqual(dv.partizip2_full(dv.lookup("gewinnen")), "gewonnen")
        self.assertEqual(dv.partizip2_full(dv.lookup("verlieren")), "verloren")
        self.assertEqual(dv.partizip2_full(dv.lookup("versprechen")), "versprochen")
        self.assertEqual(dv.partizip2_full(dv.lookup("verzeihen")), "verziehen")
        self.assertEqual(dv.partizip2_full(dv.lookup("zerbrechen")), "zerbrochen")
        self.assertEqual(dv.partizip2_full(dv.lookup("gelingen")), "gelungen")
        self.assertEqual(dv.partizip2_full(dv.lookup("besuchen")), "besucht")
        self.assertEqual(dv.partizip2_full(dv.lookup("wiederholen")), "wiederholt")
        self.assertEqual(dv.praeteritum(dv.lookup("bekommen"))[0], "bekam")
        self.assertEqual(dv.praeteritum(dv.lookup("verstehen"))[0], "verstand")
        self.assertEqual(dv.praeteritum(dv.lookup("versprechen"))[0], "versprach")
        self.assertEqual(dv.praeteritum(dv.lookup("zerbrechen"))[0], "zerbrach")
        self.assertEqual(dv.praeteritum(dv.lookup("gefallen"))[0], "gefiel")


class TestImperativ(unittest.TestCase):
    def test_imperative_forms(self):
        self.assertEqual(dv.imperativ(dv.lookup("essen"))[0], "iss")
        self.assertEqual(dv.imperativ(dv.lookup("lesen"))[0], "lies")
        self.assertEqual(dv.imperativ(dv.lookup("sehen"))[0], "sieh")
        self.assertEqual(dv.imperativ(dv.lookup("fahren"))[0], "fahr")
        self.assertEqual(dv.imperativ(dv.lookup("laufen"))[0], "lauf")
        self.assertEqual(dv.imperativ(dv.lookup("lernen"))[0], "lern")
        self.assertEqual(dv.imperativ(dv.lookup("arbeiten"))[0], "arbeite")
        self.assertEqual(dv.imperativ(dv.lookup("finden"))[0], "finde")
        self.assertEqual(dv.imperativ(dv.lookup("bitten"))[0], "bitte")
        self.assertEqual(dv.imperativ(dv.lookup("sein"))[0], "sei")
        self.assertEqual(dv.imperativ(dv.lookup("beginnen"))[0], "beginne")
        self.assertEqual(dv.imperativ(dv.lookup("sprechen"))[0], "sprich")
        self.assertEqual(dv.imperativ(dv.lookup("geben"))[0], "gib")


class TestCheck(unittest.TestCase):
    def test_correct_passes(self):
        for s in ["Ich gehe", "Du gehst", "Er geht", "Wir lernen",
                  "Ich bin gegangen", "Du bist gekommen", "Ich habe gelernt",
                  "Ich komme an", "Sie gehen", "sie geht", "Ich werde gehen",
                  "Er hat vergessen", "Ich weiß", "Du weißt"]:
            self.assertEqual(dv.check_sentence(s), [], s)

    def test_wrong_person(self):
        f = dv.check_sentence("Ich geht")
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["want"], "Ich gehe")
        f = dv.check_sentence("Du geht")
        self.assertEqual(f[0]["want"], "Du gehst")
        f = dv.check_sentence("Er gehe")
        self.assertEqual(f[0]["want"], "Er geht")

    def test_wrong_auxiliary(self):
        f = dv.check_sentence("Ich habe gegangen")
        self.assertEqual(f[0]["error"], "auxiliary")
        self.assertEqual(f[0]["want"], "Ich bin gegangen")
        f = dv.check_sentence("Ich bin gelernt")
        self.assertEqual(f[0]["want"], "Ich habe gelernt")
        f = dv.check_sentence("Er hat gegangen")
        self.assertEqual(f[0]["want"], "Er ist gegangen")

    def test_unseparated_prefix(self):
        f = dv.check_sentence("Ich ankomme")
        self.assertEqual(f[0]["error"], "separable")
        self.assertEqual(f[0]["want"], "Ich komme an")

    def test_separable_wrong_person(self):
        f = dv.check_sentence("Ich kommst an")
        self.assertEqual(f[0]["want"], "Ich komme an")

    def test_futur_wrong_aux(self):
        f = dv.check_sentence("Ich wird gehen")
        self.assertEqual(f[0]["want"], "Ich werde gehen")

    def test_unknown_is_not_a_finding(self):
        self.assertEqual(dv.check_sentence("Ich xyzzy"), [])
        self.assertEqual(dv.check_sentence("Ich gehe nach Hause"), [])


class TestQuizAnkiList(unittest.TestCase):
    def test_quiz_deterministic(self):
        a = dv.quiz_questions(5, seed=42)
        b = dv.quiz_questions(5, seed=42)
        self.assertEqual(a, b)
        for q in a:
            self.assertEqual(q["want"], dv.conjugate(dv.lookup(q["verb"]), q["tense"])[q["person"]])

    def test_quiz_cli_scoring(self):
        qs = dv.quiz_questions(3, seed=7)
        answers = ",".join(q["want"] for q in qs)
        r = run("quiz", "--n", "3", "--seed", "7", "--answers", answers)
        self.assertEqual(r.returncode, 0)
        self.assertIn("3 از 3", r.stdout)
        r = run("quiz", "--n", "3", "--seed", "7", "--answers", "falsch,falsch,falsch")
        self.assertEqual(r.returncode, 1)
        self.assertIn("0 از 3", r.stdout)

    def test_anki_rows(self):
        rows = dv.anki_rows()
        self.assertEqual(len(rows), len(dv.VERBS) * 12)  # 2 tenses x 6 persons
        front, back = rows[0]
        self.assertIn(" — ", front)
        self.assertIn("\t", front + "\t" + back)

    def test_list_counts(self):
        r = run("list", "--level", "A1")
        self.assertEqual(r.returncode, 0)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        self.assertTrue(lines[-1].startswith("89 فعل"))

    def test_rules_text(self):
        t = dv.rules_text(dv.lookup("ankommen"))
        self.assertIn("جدا می‌شود", t)
        t = dv.rules_text(dv.lookup("fahren"))
        self.assertIn("a → ä", t)
        t = dv.rules_text(dv.lookup("vergessen"))
        self.assertIn("بدون ge-", t)


class TestCLI(unittest.TestCase):
    def test_conjugate_json(self):
        r = run("conjugate", "gehen", "--json")
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertEqual(data["verb"], "gehen")
        self.assertEqual(data["paradigm"]["präsens"]["du"], "gehst")
        self.assertEqual(data["paradigm"]["perfekt"]["ich"], "bin gegangen")

    def test_unknown_verb_exit_1(self):
        r = run("conjugate", "xyzzy")
        self.assertEqual(r.returncode, 1)
        self.assertIn("نیست", r.stderr)

    def test_usage_exit_2(self):
        self.assertEqual(run("conjugate").returncode, 2)
        self.assertEqual(run("frobnicate").returncode, 2)
        self.assertEqual(run("conjugate", "gehen", "--tense", "nope").returncode, 2)

    def test_check_cli(self):
        r = run("check", "Ich geht")
        self.assertEqual(r.returncode, 1)
        self.assertIn("Ich gehe", r.stdout)
        r = run("check", "Ich gehe")
        self.assertEqual(r.returncode, 0)


class TestDataIntegrity(unittest.TestCase):
    def test_counts_and_fields(self):
        with open(DATA, encoding="utf-8") as f:
            data = json.load(f)
        verbs = data["verbs"]
        self.assertEqual(len(verbs), data["meta"]["verbs"])
        self.assertEqual(len({v["inf"] for v in verbs}), len(verbs))
        for v in verbs:
            self.assertTrue(v.get("fa"), v["inf"])
            self.assertIn(v["level"], ("A1", "A2", "B1"))
            self.assertIn(v["cls"], ("weak", "strong", "mixed", "irregular"))
            self.assertIn(v.get("aux", "haben"), ("haben", "sein"))
            if v["cls"] in ("strong", "mixed"):
                self.assertTrue(v.get("praet"), v["inf"])
                self.assertTrue(v.get("part2"), v["inf"])

    def test_every_verb_conjugates_cleanly(self):
        for inf, v in dv.VERBS.items():
            for t in dv.TENSES:
                forms = dv.conjugate(v, t)
                if t == "imperativ" and v["cls"] == "irregular" and not v.get("forms", {}).get("imperativ"):
                    self.assertIsNone(forms, inf)
                    continue
                self.assertEqual(len(forms), 3 if t == "imperativ" else 6, (inf, t))
                for f in forms:
                    self.assertTrue(f and f.strip() == f, (inf, t, f))
                    self.assertNotIn("  ", f, (inf, t, f))


if __name__ == "__main__":
    unittest.main()

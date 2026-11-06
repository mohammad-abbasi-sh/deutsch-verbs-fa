#!/usr/bin/env python3
"""deutsch-verbs-fa — German verb conjugation for Persian speakers.

Zero-dependency (Python stdlib only). Conjugates a hand-checked A1-B1 verb
list (183 verbs, Persian glosses) across Prasens, Prateritum, Perfekt,
Futur I, Konjunktiv II and Imperativ; checks a learner's German sentence
for verb-form errors where deterministically decidable; drills with quizzes;
exports Anki cards.

Usage:
  deutsch_verbs.py conjugate <verb> [--tense T] [--json]
  deutsch_verbs.py check "<sentence>" [--json]
  deutsch_verbs.py quiz [--level A1|A2|B1] [--n N] [--seed N] [--answers a,b,c]
  deutsch_verbs.py anki [--level ...] [--tenses präsens,perfekt] [--out file.tsv]
  deutsch_verbs.py list [--level ...] [--cls weak|strong|mixed|irregular]
  deutsch_verbs.py rules <verb>

Exit codes: 0 = ok / no findings · 1 = verb not in list / findings ·
2 = usage error.
"""
import json
import os
import random
import sys

PERSONS = ["ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie"]
# Capital 'Sie' = formal you (person 5); lowercase 'sie' is ambiguous
# (she = 2, they = 5) and is accepted for either.
PERSON_PRONOUNS = {
    "Ich": [0], "Du": [1], "Er": [2], "Es": [2], "Sie": [5],
    "Wir": [3], "Ihr": [4],
    "ich": [0], "du": [1], "er": [2], "es": [2], "sie": [2, 5],
    "wir": [3], "ihr": [4],
}
TENSES = ["präsens", "präteritum", "perfekt", "futur1", "konjunktiv2", "imperativ"]
TENSE_LABELS = {
    "präsens": "Präsens (حال)", "präteritum": "Präteritum (گذشته ساده)",
    "perfekt": "Perfekt (گذشته کامل)", "futur1": "Futur I (آینده)",
    "konjunktiv2": "Konjunktiv II (شرطی/آرزو)", "imperativ": "Imperativ (امری)",
}


def _data_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "..", "data", "verbs.json")


def load_verbs():
    with open(_data_path(), encoding="utf-8") as f:
        data = json.load(f)
    return {v["inf"]: v for v in data["verbs"]}, data.get("meta", {})


VERBS, META = load_verbs()
SEIN = VERBS["sein"]
HABEN = VERBS["haben"]
WERDEN = VERBS["werden"]


# ---------------------------------------------------------------- stem helpers

def stem_of(inf):
    """Verb stem: strip -en, or -n for -eln/-ern verbs."""
    if inf.endswith(("eln", "ern")):
        return inf[:-1]
    return inf[:-2]


def base_of(v):
    """Base infinitive without a separable prefix (ankommen -> kommen)."""
    sep = v.get("sep")
    if sep:
        return v["inf"][len(sep):]
    return v["inf"]


def stem(v):
    return stem_of(base_of(v))


def apply_change(s, change, stem2=None):
    """Apply a Prasens stem change to the LAST vowel of the stem.
    stem2 overrides when the change is not a plain vowel swap
    (nehmen: nehm -> nimm)."""
    if stem2:
        return stem2
    if not change:
        return s
    src, dst = change.split(">")
    idx = s.rfind(src)
    if idx < 0:
        return s
    return s[:idx] + dst + s[idx + len(src):]


def needs_e(s):
    """True when a -e- must be inserted before -st/-t/-te.

    Stem ends in -d/-t, or in -m/-n after a consonant other than l, r, m,
    n — with single 'h' (wohnen -> wohnst) excepted, while 'ch' counts
    (rechnen -> rechnest).
    """
    if not s:
        return False
    if s[-1] in ("d", "t"):
        return True
    if s[-1] in ("m", "n") and len(s) >= 2:
        prev = s[-2]
        if prev in "aeiouäöü" or prev in ("l", "r", "m", "n"):
            return False
        if prev == "h" and (len(s) < 3 or s[-3] in "aeiouäöü"):
            return False
        return True
    return False


def s_stem(s):
    return s[-1:] in ("s", "ß", "x", "z")


def umlaut(s):
    """Umlaut the last vowel of a Prateritum stem (Konjunktiv II)."""
    if "au" in s:
        idx = s.rfind("au")
        return s[:idx] + "äu" + s[idx + 2:]
    for src, dst in (("a", "ä"), ("o", "ö"), ("u", "ü")):
        idx = s.rfind(src)
        if idx >= 0:
            return s[:idx] + dst + s[idx + 1:]
    return s


def split_prefix(form, v):
    """Split a separable prefix off a finite form: 'komme an' -> ('komme','an')."""
    sep = v.get("sep")
    if not sep:
        return form, None
    return form, sep


# ---------------------------------------------------------------- conjugation

def praesens(v):
    """Return the 6 Prasens forms (without separable prefix)."""
    if v.get("forms", {}).get("praesens"):
        return list(v["forms"]["praesens"])
    s = stem(v)
    ch = apply_change(s, v.get("change"), v.get("stem2"))
    out = []
    out.append(s + "e")                                    # ich
    if s_stem(ch):
        out.append(ch + "t")                               # du
    elif needs_e(s) and not v.get("change"):
        out.append(ch + "est")                             # du
    else:
        out.append(ch + "st")                              # du
    if s_stem(ch):
        out.append(ch + "t")                               # er
    elif needs_e(s) and not v.get("change"):
        out.append(ch + "et")                              # er
    elif ch.endswith("t"):
        out.append(ch)                                     # er: rät, hält, gilt
    else:
        out.append(ch + "t")                               # er
    out.append(s + "en")                                   # wir
    if s_stem(s):
        out.append(s + "t")                                # ihr
    elif needs_e(s):
        out.append(s + "et")                               # ihr
    else:
        out.append(s + "t")                                # ihr
    out.append(s + "en")                                   # sie
    return out


def praeteritum(v):
    """Return the 6 Prateritum forms (without separable prefix)."""
    if v.get("forms", {}).get("praeteritum"):
        return list(v["forms"]["praeteritum"])
    if v["cls"] == "weak":
        s = stem(v)
        base = s + ("e" if needs_e(s) else "") + "te"
        return [base, base + "st", base, base + "n", base + "t", base + "n"]
    if v["cls"] == "mixed":
        # praet field already holds the full ich-form (wusste, dachte):
        # endings are -, -st, -, -n, -t, -n.
        p = v["praet"]
        return [p, p + "st", p, p + "n", p + "t", p + "n"]
    p = v["praet"]
    ins = p[-1:] in ("d", "t", "s", "ß", "x", "z")
    return [p,
            p + ("e" if ins else "") + "st",
            p,
            p + "en",
            p + ("e" if ins else "") + "t",
            p + "en"]


def partizip2(v):
    """Return Partizip II (without separable prefix handling)."""
    if v["cls"] in ("strong", "mixed", "irregular"):
        return v["part2"]
    s = stem(v)
    if v.get("insep") or v["inf"].endswith("ieren"):
        core = s + ("e" if needs_e(s) else "") + "t"
        return core
    core = "ge" + s + ("e" if needs_e(s) else "") + "t"
    return core


def partizip2_full(v):
    """Partizip II with a separable prefix in its place: angekommen."""
    p = partizip2(v)
    sep = v.get("sep")
    if not sep:
        return p
    if p.startswith("ge"):
        return sep + p
    return sep + "ge" + p


def aux_verb(v):
    return SEIN if v.get("aux") == "sein" else HABEN


def perfekt(v):
    aux = praesens(aux_verb(v))
    p2 = partizip2_full(v)
    return [a + " " + p2 for a in aux]


def futur1(v):
    w = praesens(WERDEN)
    return [a + " " + v["inf"] for a in w]


def konjunktiv2(v):
    """Return the 6 Konjunktiv II forms (without separable prefix)."""
    if v.get("forms", {}).get("konj2"):
        return list(v["forms"]["konj2"])
    if v["cls"] == "weak":
        return praeteritum(v)
    if v.get("konj2stem"):
        base = v["konj2stem"]
        return [base, base + "st", base, base + "n", base + "t", base + "n"]
    if v["cls"] == "mixed":
        # praet field is the full ich-form (wusste): umlaut it, endings
        # -, -st, -, -n, -t, -n (wüsste, wüsstest, ...).
        u = umlaut(v["praet"])
        return [u, u + "st", u, u + "n", u + "t", u + "n"]
    u = umlaut(v["praet"])
    return [u + "e", u + "est", u + "e", u + "en", u + "et", u + "en"]


def imperativ(v):
    """Return (du, ihr, Sie) imperative forms, or None when unused."""
    if v.get("forms", {}).get("imperativ"):
        forms = v["forms"]["imperativ"]
        return (forms[0], forms[1], v["inf"] + " Sie")
    if v["cls"] == "irregular":
        return None  # modal verbs have no usable imperative
    s = stem(v)
    # du: stem change applies for e>i / e>ie, never for a>ä.
    ch = v.get("change")
    base = apply_change(s, ch, v.get("stem2")) if ch and ch.startswith("e") else s
    # -e after -d/-t, -m/-n after a consonant, -ig, and -nn stems
    # (beginne!, gewinne!); the short form is an accepted variant.
    du = base + ("e" if needs_e(base) or base.endswith(("ig", "nn")) else "")
    ihr = praesens(v)[4]
    sep = v.get("sep")
    if sep:
        return (du + " " + sep, ihr + " " + sep,
                base_of(v) + " Sie " + sep)
    return (du, ihr, v["inf"] + " Sie")


def finite_with_prefix(forms, v):
    """Attach a separable prefix at the end of finite forms."""
    sep = v.get("sep")
    if not sep:
        return list(forms)
    return [f + " " + sep for f in forms]


def conjugate(v, tense):
    """All 6 forms of a verb in a tense (separable prefix in place)."""
    if tense == "präsens":
        return finite_with_prefix(praesens(v), v)
    if tense == "präteritum":
        return finite_with_prefix(praeteritum(v), v)
    if tense == "perfekt":
        return perfekt(v)
    if tense == "futur1":
        return futur1(v)
    if tense == "konjunktiv2":
        return finite_with_prefix(konjunktiv2(v), v)
    if tense == "imperativ":
        imp = imperativ(v)
        if imp is None:
            return None
        return list(imp)
    raise ValueError("unknown tense: %s" % tense)


def full_paradigm(v):
    out = {}
    for t in TENSES:
        forms = conjugate(v, t)
        out[t] = forms
    return out


# ---------------------------------------------------------------- lookup

def lookup(inf):
    return VERBS.get(inf)


def suggest(inf):
    """Closest verbs by prefix/contains, for 'not in list' messages."""
    cands = [k for k in VERBS if k.startswith(inf[:3]) or inf[:3] in k]
    return sorted(cands)[:5]


# ---------------------------------------------------------------- check

def _build_form_index():
    """Map every known surface form -> list of (verb, tense, person)."""
    idx = {}
    for inf, v in VERBS.items():
        for t in ("präsens", "präteritum", "konjunktiv2"):
            for i, f in enumerate(conjugate(v, t)):
                idx.setdefault(f, []).append((inf, t, i))
        for i, f in enumerate(perfekt(v)):
            idx.setdefault(f, []).append((inf, "perfekt", i))
        for i, f in enumerate(futur1(v)):
            idx.setdefault(f, []).append((inf, "futur1", i))
        for f in [partizip2_full(v)]:
            idx.setdefault(f, []).append((inf, "partizip2", None))
        imp = imperativ(v)
        if imp:
            for f in imp:
                idx.setdefault(f, []).append((inf, "imperativ", None))
    return idx


FORM_INDEX = None


def form_index():
    global FORM_INDEX
    if FORM_INDEX is None:
        FORM_INDEX = _build_form_index()
    return FORM_INDEX


def check_sentence(sentence):
    """Check a simple German sentence for verb-form errors.

    Handles: pronoun + finite form; pronoun + auxiliary + Partizip II
    (Perfekt); pronoun + werden + infinitive (Futur I); and unseparated
    separable verbs ('Ich ankomme'). Only flags what is decidable.
    Returns a list of finding dicts (empty = no findings).
    """
    toks = sentence.strip().split()
    if len(toks) < 2:
        return [{"error": "usage",
                 "message": "جمله باید دست‌کم ضمیر + فعل داشته باشد، مثل: Ich gehe"}]
    pron = toks[0]
    if pron not in PERSON_PRONOUNS:
        return [{"error": "usage",
                 "message": "جمله باید با ضمیر شروع شود (Ich, Du, Er, Wir, Ihr, Sie)"}]
    persons = PERSON_PRONOUNS[pron]
    person = persons[0]
    idx = form_index()

    # Separable verb in place: 'Ich komme an' / 'Ich kommst an'
    if len(toks) == 3:
        joined = toks[1] + " " + toks[2]
        hits = idx.get(joined, [])
        if hits:
            if any(h[2] in persons for h in hits):
                return []
            inf, tense, _ = hits[0]
            v = lookup(inf)
            want = conjugate(v, tense)[person]
            return [{"error": "form",
                     "got": sentence,
                     "want": toks[0] + " " + want,
                     "message": "«%s» صورت «%s» برای «%s» است؛ برای «%s» باید «%s» باشد."
                                % (joined, PERSONS[hits[0][2]], v["inf"],
                                   PERSONS[person], want)}]

    # Perfekt / Futur I: pronoun + aux + participle/infinitive
    if len(toks) == 3:
        aux_form, third = toks[1], toks[2]
        aux_hits = idx.get(aux_form, [])
        aux_verbs = {h[0] for h in aux_hits
                     if h[1] == "präsens" and h[0] in ("sein", "haben", "werden")}
        if aux_verbs:
            aux = next(iter(aux_verbs))
            if aux == "werden":
                v = lookup(third)
                if v is None:
                    return []
                want_aux = praesens(WERDEN)[person]
                if aux_form != want_aux:
                    return [{"error": "form",
                             "got": sentence,
                             "want": toks[0] + " " + want_aux + " " + third,
                             "message": "صرف werden با ضمیر نمی‌خواند."}]
                return []
            # Perfekt: third must be a Partizip II
            p2_hits = [h for h in idx.get(third, []) if h[1] == "partizip2"]
            if not p2_hits:
                return []
            v = lookup(p2_hits[0][0])
            want_aux = aux_verb(v)
            if want_aux["inf"] != aux:
                want = praesens(want_aux)[person] + " " + third
                return [{"error": "auxiliary",
                         "got": sentence,
                         "want": toks[0] + " " + want,
                         "message": "«%s» با «%s» گذشته می‌سازد، نه «%s»."
                                    % (v["inf"], want_aux["inf"], aux),
                         "fa": "فعل کمکی اشتباه است."}]
            want_aux_form = praesens(want_aux)[person]
            if aux_form != want_aux_form:
                return [{"error": "form",
                         "got": sentence,
                         "want": toks[0] + " " + want_aux_form + " " + third,
                         "message": "صرف فعل کمکی با ضمیر نمی‌خواند."}]
            return []

    # Simple: pronoun + finite form
    if len(toks) == 2:
        form = toks[1]
        hits = idx.get(form, [])
        if hits:
            same = [h for h in hits if h[2] in persons]
            if same:
                return []
            inf, tense, _ = hits[0]
            v = lookup(inf)
            want = conjugate(v, tense)[person]
            return [{"error": "form",
                     "got": sentence,
                     "want": toks[0] + " " + want,
                     "message": "«%s» صورت «%s» برای «%s» است؛ برای «%s» باید «%s» باشد."
                                % (form, PERSONS[hits[0][2]], v["inf"],
                                   PERSONS[person], want)}]
        # Unseparated separable verb: 'Ich ankomme' -> 'Ich komme an'
        for inf, v in VERBS.items():
            sep = v.get("sep")
            if not sep or not form.startswith(sep):
                continue
            rest = form[len(sep):]
            base_forms = praesens(v) + praeteritum(v) + konjunktiv2(v)
            if rest in base_forms:
                i = base_forms.index(rest)
                tense = ("präsens" if i < 6 else
                         "präteritum" if i < 12 else "konjunktiv2")
                want = conjugate(v, tense)[person]
                return [{"error": "separable",
                         "got": sentence,
                         "want": toks[0] + " " + want,
                         "message": "فعل جداشدنی «%s» در جمله جدا می‌شود: پیشوند «%s» به انتهای جمله می‌رود."
                                    % (inf, sep)}]
        return []
    return []


# ---------------------------------------------------------------- quiz / anki

def quiz_questions(n, level=None, seed=None, tenses=("präsens", "präteritum", "perfekt")):
    rng = random.Random(seed)
    pool = [v for v in VERBS.values() if level is None or v["level"] == level]
    pool.sort(key=lambda v: v["inf"])
    out = []
    for _ in range(n):
        v = rng.choice(pool)
        tense = rng.choice(list(tenses))
        person = rng.randrange(6)
        want = conjugate(v, tense)[person]
        out.append({"verb": v["inf"], "fa": v["fa"], "tense": tense,
                    "person": person, "want": want})
    return out


def anki_rows(level=None, tenses=("präsens", "perfekt")):
    rows = []
    for inf in sorted(VERBS):
        v = VERBS[inf]
        if level is not None and v["level"] != level:
            continue
        for tense in tenses:
            forms = conjugate(v, tense)
            for i, f in enumerate(forms):
                front = "%s (%s) — %s, %s" % (inf, v["fa"], TENSE_LABELS[tense], PERSONS[i])
                back = "%s — %s" % (f, v["fa"])
                rows.append((front, back))
    return rows


# ---------------------------------------------------------------- rules

def rules_text(v):
    lines = []
    lines.append("%s — %s" % (v["inf"], v["fa"]))
    cls_fa = {"weak": "ضعیف (منظم)", "strong": "قوی (بی‌قاعده)",
              "mixed": "مختلط", "irregular": "کاملاً بی‌قاعده"}[v["cls"]]
    lines.append("دسته: %s · سطح %s · فعل کمکی Perfekt: %s"
                 % (cls_fa, v["level"], v.get("aux", "haben")))
    if v.get("sep"):
        lines.append("فعل جداشدنی: پیشوند «%s» در جمله جدا می‌شود و به انتها می‌رود "
                     "(Ich komme an) و در Partizip II وسط می‌آید (angekommen)."
                     % v["sep"])
    if v.get("insep"):
        lines.append("فعل جدانشدنی: پیشوند جدا نمی‌شود و Partizip II بدون ge- ساخته "
                     "می‌شود (%s)." % partizip2_full(v))
    if v.get("change"):
        ch = {"a>ä": "a → ä", "e>i": "e → i", "e>ie": "e → ie"}[v["change"]]
        lines.append("تغییر ریشه در Präsens برای du و er/sie/es: %s "
                     "(du %s، er %s)."
                     % (ch, praesens(v)[1], praesens(v)[2]))
    if v["cls"] == "weak":
        lines.append("منظم: Präteritum با -te (ich %s) و Partizip II با ge-…-t "
                     "(%s) ساخته می‌شود." % (praeteritum(v)[0], partizip2_full(v)))
    elif v["cls"] in ("strong", "mixed"):
        lines.append("Präteritum: ich %s · Partizip II: %s · Konjunktiv II: ich %s."
                     % (praeteritum(v)[0], partizip2_full(v), konjunktiv2(v)[0]))
        if v["cls"] == "mixed":
            lines.append("مختلط: ریشه Präteritum عوض می‌شود ولی پایان‌ها مثل فعل "
                         "ضعیف با -t است.")
    if v["cls"] == "irregular":
        lines.append("این فعل را باید حفظ کرد — جدول کامل را با conjugate ببینید.")
    if v["inf"].endswith("ieren"):
        lines.append("فعل -ieren: در Partizip II بدون ge- می‌آید (%s)."
                     % partizip2_full(v))
    return "\n".join(lines)


# ---------------------------------------------------------------- CLI

def _print_paradigm(v, tense=None, as_json=False):
    if as_json:
        data = {"verb": v["inf"], "fa": v["fa"], "level": v["level"],
                "class": v["cls"], "aux": v.get("aux", "haben")}
        if tense:
            data["tense"] = tense
            data["forms"] = dict(zip(PERSONS, conjugate(v, tense)))
        else:
            data["paradigm"] = {t: dict(zip(PERSONS, conjugate(v, t)))
                                for t in TENSES if conjugate(v, t) is not None}
            if conjugate(v, "imperativ") is None:
                data["paradigm"]["imperativ"] = None
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return
    print("%s — %s  (سطح %s · %s · Perfekt با %s)"
          % (v["inf"], v["fa"], v["level"], v["cls"], v.get("aux", "haben")))
    tenses = [tense] if tense else TENSES
    for t in tenses:
        forms = conjugate(v, t)
        if forms is None:
            print("  %-12s — (غیرمعمول)" % TENSE_LABELS[t])
            continue
        if t == "imperativ":
            print("  %-12s du: %s · ihr: %s · Sie: %s"
                  % (TENSE_LABELS[t], forms[0], forms[1], forms[2]))
        else:
            print("  %-12s %s" % (TENSE_LABELS[t],
                                   " | ".join("%s %s" % (p, f)
                                              for p, f in zip(PERSONS, forms))))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    cmd = argv[0]
    args = argv[1:]
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]

    if cmd == "conjugate":
        if not args:
            print("usage: conjugate <verb> [--tense T] [--json]", file=sys.stderr)
            return 2
        tense = None
        rest = []
        i = 0
        while i < len(args):
            if args[i] == "--tense" and i + 1 < len(args):
                tense = args[i + 1]
                i += 2
            else:
                rest.append(args[i])
                i += 1
        if not rest:
            print("usage: conjugate <verb> [--tense T] [--json]", file=sys.stderr)
            return 2
        v = lookup(rest[0])
        if v is None:
            print("«%s» در فهرست ۱۸۳ فعل نیست." % rest[0], file=sys.stderr)
            sug = suggest(rest[0])
            if sug:
                print("شاید منظورتان این‌هاست: %s" % ", ".join(sug), file=sys.stderr)
            return 1
        if tense and tense not in TENSES:
            print("tense باید یکی از این‌ها باشد: %s" % ", ".join(TENSES),
                  file=sys.stderr)
            return 2
        _print_paradigm(v, tense, as_json)
        return 0

    if cmd == "check":
        if not args:
            print('usage: check "<sentence>" [--json]', file=sys.stderr)
            return 2
        findings = check_sentence(" ".join(args))
        if as_json:
            print(json.dumps({"sentence": " ".join(args),
                              "findings": findings},
                             ensure_ascii=False, indent=2))
        else:
            if not findings:
                print("✓ مشکلی پیدا نشد (یا جمله قابل تصمیم‌گیری قطعی نبود).")
            for f in findings:
                print("✗ %s" % f.get("message", ""))
                if "want" in f:
                    print("  درستش: %s" % f["want"])
                if "fa" in f:
                    print("  %s" % f["fa"])
        return 1 if findings else 0

    if cmd == "list":
        level = None
        cls = None
        i = 0
        while i < len(args):
            if args[i] == "--level" and i + 1 < len(args):
                level = args[i + 1]
                i += 2
            elif args[i] == "--cls" and i + 1 < len(args):
                cls = args[i + 1]
                i += 2
            else:
                i += 1
        rows = [v for v in sorted(VERBS.values(), key=lambda x: x["inf"])
                if (level is None or v["level"] == level)
                and (cls is None or v["cls"] == cls)]
        for v in rows:
            print("%-16s %-8s %-10s %s" % (v["inf"], v["level"], v["cls"], v["fa"]))
        print("%d فعل" % len(rows))
        return 0

    if cmd == "rules":
        if not args:
            print("usage: rules <verb>", file=sys.stderr)
            return 2
        v = lookup(args[0])
        if v is None:
            print("«%s» در فهرست نیست." % args[0], file=sys.stderr)
            return 1
        print(rules_text(v))
        return 0

    if cmd == "quiz":
        n, level, seed, answers = 5, None, None, None
        i = 0
        while i < len(args):
            if args[i] == "--n" and i + 1 < len(args):
                n = int(args[i + 1])
                i += 2
            elif args[i] == "--level" and i + 1 < len(args):
                level = args[i + 1]
                i += 2
            elif args[i] == "--seed" and i + 1 < len(args):
                seed = int(args[i + 1])
                i += 2
            elif args[i] == "--answers" and i + 1 < len(args):
                answers = args[i + 1].split(",")
                i += 2
            else:
                i += 1
        qs = quiz_questions(n, level, seed)
        score = 0
        for k, q in enumerate(qs):
            print("سؤال %d: %s (%s) — %s، %s؟"
                  % (k + 1, q["verb"], q["fa"], TENSE_LABELS[q["tense"]],
                     PERSONS[q["person"]]))
            if answers is not None:
                ans = answers[k].strip() if k < len(answers) else ""
                print("  پاسخ شما: %s" % ans)
            else:
                ans = input("  پاسخ: ").strip()
            if ans == q["want"]:
                print("  ✓ درست!")
                score += 1
            else:
                print("  ✗ درستش: %s" % q["want"])
        print("نتیجه: %d از %d" % (score, len(qs)))
        return 0 if score == len(qs) else 1

    if cmd == "anki":
        level, out, tenses = None, None, ("präsens", "perfekt")
        i = 0
        while i < len(args):
            if args[i] == "--level" and i + 1 < len(args):
                level = args[i + 1]
                i += 2
            elif args[i] == "--out" and i + 1 < len(args):
                out = args[i + 1]
                i += 2
            elif args[i] == "--tenses" and i + 1 < len(args):
                tenses = tuple(args[i + 1].split(","))
                i += 2
            else:
                i += 1
        rows = anki_rows(level, tenses)
        text = "\n".join("%s\t%s" % r for r in rows) + "\n"
        if out:
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
            print("%d کارت در %s نوشته شد." % (len(rows), out))
        else:
            sys.stdout.write(text)
        return 0

    print("دستور ناشناخته: %s" % cmd, file=sys.stderr)
    print(__doc__.strip(), file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

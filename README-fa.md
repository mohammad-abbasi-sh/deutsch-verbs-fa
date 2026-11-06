# deutsch-verbs-fa — صرف فعل آلمانی برای فارسی‌زبان‌ها

یک **Agent Skill** قطعی برای نیمهٔ دیگر گرامر آلمانی که فارسی‌زبان‌ها
هر روز با آن گیر می‌کنند: صرف فعل. بعد از
[`deutsch-fa`](https://github.com/mohammad-abbasi-sh/deutsch-fa)
(der/die/das و ۴ حالت)، این دنبالهٔ آن است — *gehen* در برابر *ging*
در برابر *gegangen*، *haben* در برابر *sein*، پیشوندهای جداشدنی که در
جمله جدا می‌شوند، و تغییر ریشه که ایجنت‌ها حدس می‌زنند و اشتباه می‌کنند.

فارسی صرف فعل مثل آلمانی ندارد: نه پسوند شخص، نه تغییر واکهٔ ریشه، نه
پیشوند جداشدنی، نه انتخاب haben/sein در گذشته.
`deutsch-verbs-fa` همهٔ صورت‌ها را **قطعی** می‌کند: یک موتور پایتون
بدون وابستگی + فهرست دست‌بررسی‌شدهٔ ۱۸۳ فعل A1 تا B1 (دسته، صورت‌های
ریشه، فعل کمکی، پیشوند، معنی فارسی) — با توضیح همه‌چیز به فارسی.

بدون فراخوانی مدل. بدون دانلود. بدون کلید API. فقط کتابخانهٔ استاندارد
پایتون ۳٫۸ به بالا.

## مشکل

```
زبان‌آموز می‌نویسد:  Ich habe gegangen.     /  Ich ankomme.
ایجنت (با حدس):     درست به نظر می‌رسد ✓    ← هر دو غلط‌اند و حالا
                                              زبان‌آموز هر دو را حفظ می‌کند

با deutsch-verbs-fa:
$ python3 scripts/deutsch_verbs.py check "Ich habe gegangen"
✗ «gehen» با «sein» گذشته می‌سازد، نه «haben».
  درستش: Ich bin gegangen

$ python3 scripts/deutsch_verbs.py check "Ich ankomme"
✗ فعل جداشدنی «ankommen» در جمله جدا می‌شود: پیشوند «an» به انتهای جمله می‌رود.
  درستش: Ich komme an
```

## چه چیزی داخل است

```
skills/deutsch-verbs-fa/
  SKILL.md                  اسکیل ایجنت (قرارداد)
  scripts/deutsch_verbs.py  موتور — conjugate, rules, check, quiz, anki
  data/verbs.json           ۱۸۳ فعل دست‌بررسی‌شدهٔ A1 تا B1
  references/
    conjugation-tables.md   جدول کامل پسوندها (ضعیف/قوی/مختلط، درج -e-)
    tense-guide.md          هر زمان کی به کار می‌رود، haben در برابر sein، پیشوندها، تله‌ها
cursor/deutsch-verbs-fa.mdc قانون کرسر (همان قرارداد، فشرده)
mcp-server/                 سرور MCP (stdio) با ۵ ابزار
tests/                      ۴۸ تست، همه پاس (unittest استاندارد)
dist/deutsch-verbs-fa-skill.zip   بستهٔ آماده برای آپلود در Claude.ai
```

دستورها:

```bash
python3 scripts/deutsch_verbs.py conjugate gehen
# پارادایم کامل: Präsens, Präteritum, Perfekt, Futur I, Konjunktiv II, Imperativ

python3 scripts/deutsch_verbs.py conjugate ankommen --tense perfekt
python3 scripts/deutsch_verbs.py rules vergessen     # توضیح فارسی
python3 scripts/deutsch_verbs.py check "Ich habe gegangen"
python3 scripts/deutsch_verbs.py quiz --n 5 --level A1 --seed 42
python3 scripts/deutsch_verbs.py anki --out cards.tsv   # ۲٬۱۹۶ کارت
python3 scripts/deutsch_verbs.py list --level A2 --cls strong
```

## نصب

**Claude Code** — پوشهٔ `skills/deutsch-verbs-fa/` را در پوشهٔ
اسکیل‌های پروژه (یا `~/.claude/skills/` برای استفادهٔ سراسری) کپی کنید.

**Claude.ai** — فایل `dist/deutsch-verbs-fa-skill.zip` را به‌عنوان
اسکیل آپلود کنید.

**Cursor** — فایل `cursor/deutsch-verbs-fa.mdc` را در `.cursor/rules/`
کپی کنید. Windsurf / Cline / Continue: نگاه کنید به `cursor/README.md`.

**هر کلاینت MCP** — سرور stdio را معرفی کنید:

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

ابزارها: `conjugate`, `check_sentence`, `quiz`, `anki_export`,
`list_verbs`.

## محدودیت‌های صادقانه

- فهرست، واژگان هستهٔ A1 تا B1 است (نسخهٔ ۱٫۰٫۰) — جایگزین دیکشنری
  برای فعل‌های خارج از فهرست نیست؛ فعل ناشناخته «در فهرست نیست»
  می‌گیرد، نه یک جواب حدسی.
- بررسی‌کنندهٔ جمله عمداً محافظه‌کار است: فقط جمله‌های ساده.
  «یافته‌ای نیست» یعنی «غلط قطعی پیدا نشد»، نه «جمله درست است».
- Konjunktiv II فعل‌های ضعیف همان Präteritum است؛ صورت مؤدبانهٔ
  *würde + Infinitiv* مستند شده، نه تولیدشده.
- مرجع قطعی است، نه معلم: دربارهٔ سبک و طبیعی‌بودن جمله قضاوت نمی‌کند.

## نقشهٔ راه

- رشد فهرست تا ۳۰۰ فعل (B2)، مشارکت جامعه خوش‌آمد است.
- یک جملهٔ نمونه برای هر فعل (دستی، با حالت صحیح).
- زمان‌بندی تکرار فاصله‌دار برای `quiz`.
- پوشش جمله‌های وابسته و فعل‌های بازتابی در `check`.

## لایسنس

MIT — نگاه کنید به LICENSE.

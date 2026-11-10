#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "jinja2", "openpyxl", "pypdf", "segno"]
# ///
"""workshop-kit: the deterministic half of the workshop pipeline.

  wk.py init      WS --client NAME --slug SLUG   make the workshop folder
  wk.py diagnose  WS (--sheet URL | --csv FILE)  form answers -> intake/diagnosis.json
  wk.py approve   WS slides|exercises|guides     record a checkpoint approval
  wk.py build     WS                             exercises + rules -> build/kit/
  wk.py ship      WS [--replace]                 scan, zip, upload to Drive, share link
  wk.py link      WS                             make + share the Drive folder early, write drive_link
  wk.py qr        WS                             deck/qr.png from drive_link

Exit codes: 0 ok · 1 error · 3 gws failed (kit copied to the synced Drive folder) · 4 Drive folder exists
"""
import argparse, csv, datetime as dt, json, os, re, shutil, subprocess, sys, zipfile
from collections import Counter
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader

SKILL = Path(__file__).resolve().parent.parent
CORE, TEMPLATES = SKILL / "core", SKILL / "templates"
CHROME = (os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium")
          or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
PARTS = ("slides", "exercises", "guides")
MAX_TITLE, MAX_STEPS, MAX_STEP_CHARS, MAX_PROMPT = 40, 5, 90, 600
TOOL_NAMES = {
    "claude": {"project": "Project", "skill": "Skill"},
    "chatgpt": {"project": "Project", "skill": "custom GPT"},
    "copilot": {"project": "Notebook", "skill": "agent"},
}
# Column keys for the diagnosis form. First header containing any phrase wins.
KEYS = {
    "role": ["função", "role"],
    "tools": ["ferramentas usa", "tools do you use"],         # "usas" and "usa" both match
    "ai_tools": ["ferramentas de ia já", "quais já usaste", "ai tools have you"],
    "approved": ["empresa aprovou", "company approved"],
    "fluency": ["fluência", "experiência atual com ferramentas de ia", "fluency"],
    "tasks": ["tarefas", "tasks"],
    "blocks": ["bloqueia", "preocupações", "blocks you"],
    "files": ["ficheiro", "real file"],
}
MULTI, SINGLE, FREE = ("tools", "ai_tools", "approved"), ("fluency", "files"), ("role", "tasks", "blocks")


class GwsError(Exception):
    pass


def die(msg, code=1):
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(code)


# ── workshop.yaml ────────────────────────────────────────────────────────────

def load_cfg(ws: Path) -> dict:
    f = ws / "workshop.yaml"
    if not f.exists():
        die(f"no workshop.yaml in {ws} — run: wk.py init {ws} --client … --slug …")
    cfg = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    defaults = yaml.safe_load((TEMPLATES / "workshop.yaml").read_text(encoding="utf-8"))
    cfg["labels"] = {**defaults["labels"], **(cfg.get("labels") or {})}
    cfg.setdefault("approved", {})
    cfg["approved"] = cfg["approved"] or {}
    return cfg


def set_field(ws: Path, key: str, value: str, block: str | None = None):
    """Rewrite one scalar line in workshop.yaml, keeping comments. block='approved' scopes to that map."""
    f = ws / "workshop.yaml"
    lines = f.read_text(encoding="utf-8").splitlines()
    start = 0
    if block:
        start = next(i for i, l in enumerate(lines) if l.startswith(f"{block}:")) + 1
    pat = re.compile(rf"^({'  ' if block else ''}{re.escape(key)}:)\s*[^#\n]*?(\s+#.*)?$")
    for i in range(start, len(lines)):
        if block and not lines[i].startswith("  "):
            break
        if m := pat.match(lines[i]):
            lines[i] = f"{m[1]} {json.dumps(value, ensure_ascii=False)}{m[2] or ''}"
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    die(f"field {block + '.' if block else ''}{key} not found in workshop.yaml")


def cmd_init(ws: Path, client: str, slug: str):
    for d in ("intake", "deck", "exercises", "demos", "skills"):
        (ws / d).mkdir(parents=True, exist_ok=True)
    if not (ws / "workshop.yaml").exists():
        shutil.copy(TEMPLATES / "workshop.yaml", ws / "workshop.yaml")
        set_field(ws, "client", client)
        set_field(ws, "slug", slug)
    print(f"✓ {ws}")


def cmd_approve(ws: Path, part: str):
    cfg = load_cfg(ws)
    earlier = PARTS[: PARTS.index(part)]
    if missing := [p for p in earlier if not cfg["approved"].get(p)]:
        die(f"approve {', '.join(missing)} first")
    set_field(ws, part, dt.date.today().isoformat(), block="approved")
    print(f"✓ approved: {part}")


# ── gws ──────────────────────────────────────────────────────────────────────

def gws(*args, params=None, body=None, upload=None) -> dict:
    cmd = ["gws", *args]
    if params is not None:
        cmd += ["--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    if upload is not None:                                   # gws refuses uploads outside its working directory
        cmd += ["--upload", Path(upload).name]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=Path(upload).parent if upload else None)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise GwsError(str(e))
    out = r.stdout
    i = out.find("{")
    data = json.loads(out[i:]) if i >= 0 else {}
    if r.returncode or "error" in data:
        raise GwsError((data.get("error") and json.dumps(data["error"])) or (r.stderr or out).strip()[-400:])
    return data


# ── diagnose ─────────────────────────────────────────────────────────────────

def find_columns(header: list[str]) -> dict[str, int | None]:
    low = [h.lower() for h in header]
    return {k: next((i for i, h in enumerate(low) if any(w in h for w in words)), None) for k, words in KEYS.items()}


def diagnose(rows: list[list[str]]) -> dict:
    header, answers = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]
    cols = find_columns(header)
    cell = lambda r, i: r[i].strip() if i is not None and i < len(r) else ""
    counts = {}
    for k in MULTI:
        c = Counter(p.strip() for r in answers for p in cell(r, cols[k]).split(", ") if p.strip())
        counts[k] = dict(c.most_common())
    for k in SINGLE:
        counts[k] = dict(Counter(cell(r, cols[k]) for r in answers if cell(r, cols[k])).most_common())
    return {
        "responses": len(answers),
        "columns": {k: (header[i] if i is not None else None) for k, i in cols.items()},
        "counts": counts,
        "free_text": {k: [cell(r, cols[k]) for r in answers if cell(r, cols[k])] for k in FREE},
    }


def cmd_diagnose(ws: Path, sheet: str | None, csv_path: str | None):
    if sheet:
        sid = re.search(r"/d/([\w-]+)", sheet) or die(f"not a sheet URL: {sheet}")
        rows = gws("sheets", "spreadsheets", "values", "get",
                   params={"spreadsheetId": sid[1], "range": "A1:Z2000"}).get("values", [])
        (ws / "intake").mkdir(exist_ok=True)
        with open(ws / "intake/responses.csv", "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerows(rows)
    else:
        rows = list(csv.reader(open(csv_path, encoding="utf-8")))
    if len(rows) < 2:
        die("the form has no answers yet")
    d = diagnose(rows)
    (ws / "intake").mkdir(exist_ok=True)
    (ws / "intake/diagnosis.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [k for k, v in d["columns"].items() if v is None]
    print(f"✓ intake/diagnosis.json · {d['responses']} answers · {len(KEYS) - len(missing)} of {len(KEYS)} columns"
          + (f" · not in this form: {', '.join(missing)}" if missing else ""))


# ── exercises ────────────────────────────────────────────────────────────────

def load_rules(ws: Path, cfg: dict) -> list[dict]:
    own = ws / "rules.yaml"
    rules = yaml.safe_load((own if own.exists() else CORE / "rules.yaml").read_text(encoding="utf-8"))
    if not own.exists():
        names = TOOL_NAMES.get(cfg.get("tool", "claude"), TOOL_NAMES["claude"])
        for r in rules:
            r["then"] = r["then"].format(**names)
    return rules


def parse_exercise(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {"_error": "no front matter"}
    meta = yaml.safe_load(m[1]) or {}
    parts = re.split(r"^## +(.+?)\s*$", m[2], flags=re.M)
    sections = {parts[i].strip().lower(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    heads = {parts[i].strip().lower(): parts[i].strip() for i in range(1, len(parts) - 1, 2)}
    return {
        "title": str(meta.get("title", "")).strip(),
        "minutes": meta.get("minutes"),
        "rule_id": meta.get("rule"),
        "data": meta.get("data") or [],
        "steps": re.findall(r"^\s*\d+\.\s+(.+)$", sections.get("steps", ""), re.M),
        "prompts": [v for k, v in sections.items() if k.startswith("prompt") and v],
        # what follows "Prompt" in the heading ("2", "· pergunta 1"); empty for a bare "## Prompt"
        "prompt_labels": [heads[k][6:].strip() for k, v in sections.items() if k.startswith("prompt") and v],
        "done_when": sections.get("done when", ""),
        "note": sections.get("note", ""),
    }


def check(x: dict, folder: Path, rule_ids: set[str]) -> list[str]:
    if "_error" in x:
        return [x["_error"]]
    e = []
    if not x["title"] or len(x["title"]) > MAX_TITLE:
        e.append(f"title must have 1–{MAX_TITLE} chars")
    if not isinstance(x["minutes"], int):
        e.append("minutes must be a number")
    if x["rule_id"] not in rule_ids:
        e.append(f'rule "{x["rule_id"]}" not in rules.yaml ({", ".join(sorted(rule_ids))})')
    if not 1 <= len(x["steps"]) <= MAX_STEPS:
        e.append(f"needs 1–{MAX_STEPS} numbered steps, has {len(x['steps'])}")
    e += [f"step {i} has {len(s)} chars (max {MAX_STEP_CHARS})" for i, s in enumerate(x["steps"], 1) if len(s) > MAX_STEP_CHARS]
    if not x["prompts"]:
        e.append("no ## Prompt section")
    e += [f"prompt has {len(p)} chars (max {MAX_PROMPT})" for p in x["prompts"] if len(p) > MAX_PROMPT]
    if not x["done_when"]:
        e.append("no ## Done when section")
    e += [f"data/{f} not found" for f in x["data"] if not (folder / "data" / f).exists()]
    return e


def load_exercises(ws: Path, rules: list[dict]) -> tuple[list[dict], list[str]]:
    by_id = {r["id"]: r for r in rules}
    out, errors = [], []
    for n, f in enumerate(sorted((ws / "exercises").glob("*/exercise.md")), 1):
        x = parse_exercise(f)
        errors += [f"{f.parent.name}: {m}" for m in check(x, f.parent, set(by_id))]
        if "_error" not in x:
            rule = by_id.get(x["rule_id"], {})
            out.append({**x, "num": n, "folder": f.parent.name, "path": f, "rule_then": rule.get("then", "")})
    return out, errors


def load_demos(ws: Path) -> tuple[list[dict], list[str]]:
    """demos/NN-slug/demo.md: front matter (title, minutes, slide, data) + Prompts / What I show / The room should see."""
    demos, errors = [], []
    for f in sorted((ws / "demos").glob("*/demo.md")):
        m = re.match(r"^---\n(.*?)\n---\n", f.read_text(encoding="utf-8"), re.S)
        meta = (yaml.safe_load(m[1]) or {}) if m else {}
        if not meta.get("title"):
            errors.append(f"demos/{f.parent.name}: demo.md needs front matter with a title")
            continue
        errors += [f"demos/{f.parent.name}: data/{d} not found" for d in meta.get("data") or []
                   if not (f.parent / "data" / d).is_file()]
        demos.append({**meta, "folder": f.parent.name, "path": f})
    return demos, errors


def stale_deck_warnings(ws: Path, cfg: dict, exercises: list[dict]) -> list[str]:
    deck = ws / "deck"
    warn = []
    for x in exercises:
        t = x["path"].stat().st_mtime
        if cfg.get("presentation", "claude-slides") == "claude-slides":
            slide = deck / "project/slides" / f"ex-{x['folder']}.html"
            if not slide.exists():
                warn.append(f"no slide ex-{x['folder']} in deck/project/slides/")
            elif slide.stat().st_mtime < t:
                warn.append(f"slide ex-{x['folder']} is older than its exercise.md — update and republish it")
        else:
            files = [p for p in deck.rglob("*") if p.is_file()]
            if files and max(p.stat().st_mtime for p in files) < t:
                warn.append(f"deck/ is older than {x['folder']}/exercise.md — update its slide")
    return warn


# ── build ────────────────────────────────────────────────────────────────────

def print_pdf(html: Path, pdf: Path):
    if not Path(CHROME).exists():
        die(f"Chrome not found at {CHROME} (set CHROME=…)")
    import tempfile
    for attempt in (1, 2):
        # A throwaway profile keeps headless Chrome away from the user's running Chrome profile, which can make it hang.
        with tempfile.TemporaryDirectory(prefix="wk-chrome-") as profile:
            try:
                subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-first-run",
                                f"--user-data-dir={profile}", "--virtual-time-budget=10000",
                                f"--print-to-pdf={pdf}", html.as_uri()],
                               check=True, capture_output=True, timeout=90)
                return
            except subprocess.TimeoutExpired:
                if attempt == 2:
                    die(f"Chrome timed out printing {html.name} twice")


def embeds_to_iframes(s: str) -> str:
    """An <x-embed> holds a whole page (html/body CSS, a script). Inlined, it takes over the print; an iframe keeps it apart.
    Headless print advances timers but never paints frames, so the shim runs requestAnimationFrame count-ups on timers."""
    from html import escape
    shim = "<script>requestAnimationFrame=function(f){return setTimeout(function(){f(performance.now())},16)}</script>"
    return re.sub(r"<x-embed\b([^>]*)>(.*?)</x-embed>",
                  lambda m: f'<iframe{m[1]} srcdoc="{escape(shim + m[2])}"></iframe>', s, flags=re.S)


def slides_pdf(ws: Path, cfg: dict, out: Path, tmp: Path) -> str | None:
    """Return a warning, or None when 4-slides.pdf was written."""
    deck = ws / "deck"
    if (deck / "slides.pdf").exists():                       # an export always wins: best fidelity
        shutil.copy(deck / "slides.pdf", out)
        return None
    pres = cfg.get("presentation", "claude-slides")
    if pres == "claude-slides" and (deck / "project/deck.json").exists():
        index = json.loads((deck / "project/deck.json").read_text(encoding="utf-8"))
        blobs = json.loads((deck / "assets.json").read_text()) if (deck / "assets.json").exists() else {}
        sections = []
        for sid in index.get("order", []):
            f = deck / "project/slides" / f"{sid}.html"
            if f.exists():
                html = re.sub(r"<aside>.*?</aside>", "", f.read_text(encoding="utf-8"), flags=re.S)
                for blob, local in blobs.items():
                    html = html.replace(blob, (ws / local).resolve().as_uri())
                sections.append(embeds_to_iframes(html))
        faces = "".join(f'<link rel="stylesheet" href="{v["href"]}">' for v in index.get("faces", {}).values() if v.get("href"))
        page = (f'<!doctype html><html><head><meta charset="utf-8">{faces}<style>@page{{size:1920px 1080px;margin:0}}'
                "body{margin:0}*{margin:0;box-sizing:border-box}iframe{border:0}"
                "section{width:1920px;height:1080px;position:relative;overflow:hidden;break-after:page}</style></head>"
                f"<body>{''.join(sections)}</body></html>")
        (tmp / "slides.html").write_text(page, encoding="utf-8")
        print_pdf(tmp / "slides.html", out)
        # ponytail: Chrome print skips the Slides runtime (x-icon, x-shape); export deck/slides.pdf when those matter
        return None
    if pres == "marp" and (deck / "deck.md").exists():
        marp = [shutil.which("marp")] if shutil.which("marp") else ["npx", "--yes", "@marp-team/marp-cli"]
        try:
            subprocess.run([*marp, str(deck / "deck.md"), "--pdf", "--allow-local-files", "-o", str(out)],
                           check=True, capture_output=True, timeout=300)
        except (OSError, subprocess.SubprocessError):
            return "marp could not print deck/deck.md: export the deck to deck/slides.pdf"
        return None
    return "no slides PDF: export the deck to deck/slides.pdf"


def prompt_label(L: dict, lab: str, i: int, n: int) -> str:
    return f"{L['prompt']} {lab}" if lab else f"{L['prompt']}{f' {i}' if n > 1 else ''}"


def prompt_txt(x: dict, L: dict) -> str:
    t = [f"{L['exercise']} {x['num']} · {x['title']} ({x['minutes']} {L['minutes']})", "", L["steps"]]
    t += [f"{i}. {s}" for i, s in enumerate(x["steps"], 1)]
    for i, (p, lab) in enumerate(zip(x["prompts"], x["prompt_labels"]), 1):
        t += ["", prompt_label(L, lab, i, len(x["prompts"])), "", p]
    t += ["", f"{L['done_when']}: {x['done_when']}"]
    if x["note"]:
        t += [f"{L['note']}: {x['note']}"]
    return "\n".join(t) + "\n"


def cmd_build(ws: Path) -> Path:
    cfg = load_cfg(ws)
    L = cfg["labels"]
    rules = load_rules(ws, cfg)
    exercises, errors = load_exercises(ws, rules)
    demos, demo_errors = load_demos(ws)
    errors += demo_errors
    if errors:
        print("\n".join(f"✗ {e}" for e in errors), file=sys.stderr)
        die("build stopped · 0 files written")
    for w in stale_deck_warnings(ws, cfg, exercises):
        print(f"! {w}")

    build = ws / "build"
    shutil.rmtree(build, ignore_errors=True)                  # no old file survives a build
    tmp, kit = build / "tmp", build / "kit" / f"{cfg['slug']}-{L['participants']}"
    tmp.mkdir(parents=True)
    kit.mkdir(parents=True)

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True)
    env.globals["prompt_label"] = prompt_label
    ctx = {"ws": cfg, "L": L, "rules": rules, "exercises": exercises}
    (kit / f"3-{L['prompts']}.html").write_text(env.get_template("guide.html").render(mode="screen", **ctx), encoding="utf-8")
    (tmp / "guide.html").write_text(env.get_template("guide.html").render(mode="print", **ctx), encoding="utf-8")
    (tmp / "cheat.html").write_text(env.get_template("cheat-sheet.html").render(**ctx), encoding="utf-8")
    print_pdf(tmp / "guide.html", kit / f"1-{L['guide']}.pdf")
    print_pdf(tmp / "cheat.html", kit / f"2-{L['cheat_sheet']}.pdf")
    if warn := slides_pdf(ws, cfg, kit / f"4-{L['slides']}.pdf", tmp):
        print(f"! {warn}")

    for x in exercises:                                       # allowlist: prompt.txt, data/, solution/
        dest = kit / L["exercises"] / x["folder"]
        dest.mkdir(parents=True)
        (dest / "prompt.txt").write_text(prompt_txt(x, L), encoding="utf-8")
        for src, name in (("data", L["data"]), ("solution", L["solution"])):
            if (x["path"].parent / src).is_dir():
                shutil.copytree(x["path"].parent / src, dest / name, ignore=shutil.ignore_patterns(".*", "__pycache__", "~$*"))

    for dm in demos:                                          # allowlist: demo.md, data/ (make_data.py stays home)
        dest = kit / L.get("demos", "demos") / dm["folder"]
        dest.mkdir(parents=True)
        shutil.copy2(dm["path"], dest / "demo.md")
        if (dm["path"].parent / "data").is_dir():
            shutil.copytree(dm["path"].parent / "data", dest / L["data"], ignore=shutil.ignore_patterns(".*", "__pycache__", "~$*"))

    for sk in sorted(p.parent for p in (ws / "skills").glob("*/SKILL.md")):
        out = kit / L["skills"]
        out.mkdir(exist_ok=True)
        with zipfile.ZipFile(out / f"{sk.name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(sk.rglob("*")):
                if f.is_file() and not f.name.startswith("."):
                    z.write(f, f"{sk.name}/{f.relative_to(sk)}")   # the skill folder sits at the zip root
        if cfg.get("tool") == "chatgpt":
            body = re.sub(r"^---\n.*?\n---\n", "", (sk / "SKILL.md").read_text(encoding="utf-8"), flags=re.S)
            (out / f"{sk.name}-instructions.txt").write_text(body.strip() + "\n", encoding="utf-8")

    shutil.rmtree(tmp)
    n = sum(1 for p in kit.rglob("*") if p.is_file())
    print(f"✓ {kit.relative_to(ws)} · {len(exercises)} exercises · {len(demos)} demos · {n} files")
    return kit


# ── personal data scan ───────────────────────────────────────────────────────

# NIF, PHONE and IBAN match Portuguese formats. Add your country's patterns here and in scan_personal_data.
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
NIF = re.compile(r"(?<!\d)(?<!\d[.,])[1-9]\d{8}(?!\d)")   # 9 digits; the checksum in nif_ok cuts false hits
PHONE = re.compile(r"(?<!\d)(?:\+351[\s.]?)?9[1236]\d[\s.]?\d{3}[\s.]?\d{3}(?!\d)")
IBAN = re.compile(r"\bPT50\s?(?:\d{4}\s?){5}\d\b")
FAKE_DOMAINS = ("example.com", "example.org", "example.net", ".test", ".example", ".invalid")
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".tsv", ".html", ".json", ".yaml", ".yml", ".xml"}


def nif_ok(s: str) -> bool:
    d = [int(c) for c in s]
    check = 11 - sum(d[i] * (9 - i) for i in range(8)) % 11
    return (0 if check >= 10 else check) == d[8]


def text_of(f: Path) -> str:
    s = f.suffix.lower()
    if s in TEXT_SUFFIXES:
        return f.read_text(encoding="utf-8", errors="ignore")
    if s in {".docx", ".pptx", ".zip"}:
        with zipfile.ZipFile(f) as z:
            parts = [z.read(n).decode("utf-8", "ignore") for n in z.namelist()
                     if n.endswith(".xml") or Path(n).suffix.lower() in TEXT_SUFFIXES]
        return re.sub(r"<[^>]+>", " ", " ".join(parts))
    if s in {".xlsx", ".xlsm"}:
        from openpyxl import load_workbook
        wb = load_workbook(f, read_only=True, data_only=True)
        return " ".join(str(v) for ws in wb.worksheets for row in ws.iter_rows(values_only=True) for v in row if v is not None)
    if s == ".pdf":
        from pypdf import PdfReader
        return " ".join(p.extract_text() or "" for p in PdfReader(f).pages)
    return ""


def scan_personal_data(root: Path, allow: list[str]) -> tuple[list[str], list[str]]:
    hits, skipped = [], []
    for f in sorted(p for p in root.rglob("*") if p.is_file()):
        try:
            text = text_of(f)
        except Exception as e:                                # an unreadable file is reported, never ignored
            skipped.append(f"{f.relative_to(root)} ({e.__class__.__name__})")
            continue
        found = [("email", m) for m in EMAIL.findall(text) if not m.lower().endswith(FAKE_DOMAINS)]
        found += [("NIF", m) for m in NIF.findall(text) if nif_ok(m)]
        found += [("phone", m) for m in PHONE.findall(text)]
        found += [("IBAN", m) for m in IBAN.findall(text)]
        hits += sorted({f"{f.relative_to(root)}: {k} {m[:3]}…" for k, m in found if m not in allow})
    return hits, skipped


# ── ship ─────────────────────────────────────────────────────────────────────

def drive_root() -> Path | None:
    return next(Path.home().glob("Library/CloudStorage/GoogleDrive-*/My Drive"), None)


def _q(s: str) -> str:
    return s.replace("\\", "\\\\").replace("'", "\\'")


def find_folder(name: str, parent: str) -> str | None:
    q = f"name = '{_q(name)}' and mimeType = 'application/vnd.google-apps.folder' and '{parent}' in parents and trashed = false"
    files = gws("drive", "files", "list", params={"q": q, "fields": "files(id,name)"}).get("files", [])
    return files[0]["id"] if files else None


def children(folder: str) -> list[str]:
    q = f"'{_q(folder)}' in parents and trashed = false"
    return [f["id"] for f in gws("drive", "files", "list", params={"q": q, "fields": "files(id)"}).get("files", [])]


def create_folder(name: str, parent: str) -> str:
    return gws("drive", "files", "create", params={"fields": "id"},
               body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent]})["id"]


def upload_tree(local: Path, parent: str):
    folder = create_folder(local.name, parent)
    for p in sorted(local.iterdir()):
        if p.is_dir():
            upload_tree(p, folder)
        else:
            gws("drive", "files", "create", params={"fields": "id"}, body={"name": p.name, "parents": [folder]}, upload=p)


def cmd_ship(ws: Path, replace: bool):
    cfg = load_cfg(ws)
    if missing := [p for p in PARTS if not cfg["approved"].get(p)]:
        die(f"not approved: {', '.join(missing)} — run that checkpoint first · nothing copied")
    kit = cmd_build(ws)
    hits, skipped = scan_personal_data(kit, cfg.get("pii_ok") or [])
    for s in skipped:
        print(f"! not scanned: {s}")
    if hits:
        print("\n".join(f"✗ {h}" for h in hits), file=sys.stderr)
        die("personal data found · fix the files, or add the exact string to pii_ok in workshop.yaml")
    print(f"✓ personal data scan: 0 hits")
    zip_path = Path(shutil.make_archive(str(kit), "zip", kit.parent, kit.name))
    print(f"✓ zip: {zip_path.name} · {zip_path.stat().st_size / 1e6:.1f} MB")

    slug, top = cfg["slug"], None
    try:
        workshops = find_folder("workshops", "root") or create_folder("workshops", "root")
        if top := find_folder(slug, workshops):              # reuse it: the link, and the deck's QR, never change
            old = children(top)
            if old and not replace:
                die(f"Drive folder has files: https://drive.google.com/drive/folders/{top}\n"
                    f"  re-run with --replace to swap them (same folder, same link)", code=4)
            for f in old:
                gws("drive", "files", "update", params={"fileId": f}, body={"trashed": True})
            if old:
                print(f"✓ {len(old)} old item(s) moved to the Drive trash · same folder, same link")
        else:
            top = create_folder(slug, workshops)
        upload_tree(kit, top)
        gws("drive", "files", "create", params={"fields": "id"}, body={"name": zip_path.name, "parents": [top]}, upload=zip_path)
        gws("drive", "permissions", "create", params={"fileId": top}, body={"role": "reader", "type": "anyone"})
    except GwsError as e:
        print(f"GWS_FAILED: {e}")
        if top:
            print(f"PARTIAL_DRIVE_FOLDER: https://drive.google.com/drive/folders/{top}")
        root = drive_root()
        if not root:
            die(f"no synced Drive folder either · the zip is at {zip_path}", code=3)
        dest = root / "workshops" / slug
        shutil.copytree(kit, dest / kit.name, dirs_exist_ok=True)
        shutil.copy2(zip_path, dest)
        print(f"COPIED_TO: {dest}")
        sys.exit(3)
    link = f"https://drive.google.com/drive/folders/{top}"
    set_field(ws, "drive_link", link)
    print(f"✓ gws upload: workshops/{slug}/ · anyone with the link can view\n  {link}")


def cmd_link(ws: Path):
    """Make the kit's Drive folder before ship, so the QR can go on the deck early. ship reuses it."""
    slug = load_cfg(ws)["slug"]
    try:
        workshops = find_folder("workshops", "root") or create_folder("workshops", "root")
        top = find_folder(slug, workshops) or create_folder(slug, workshops)
        gws("drive", "permissions", "create", params={"fileId": top}, body={"role": "reader", "type": "anyone"})
    except GwsError as e:
        die(f"gws failed: {e} · try `gws auth login`")
    link = f"https://drive.google.com/drive/folders/{top}"
    set_field(ws, "drive_link", link)
    print(f"✓ workshops/{slug}/ · anyone with the link can view · ship fills it later\n  {link}")


def cmd_qr(ws: Path):
    import segno
    link = load_cfg(ws).get("drive_link") or die("no drive_link yet · run link or ship first")
    out = ws / "deck/qr.png"
    segno.make(link, error="m").save(out, scale=12, border=2, dark="#1F1B16")
    print(f"✓ {out.relative_to(ws)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("init"); p.add_argument("ws"); p.add_argument("--client", required=True); p.add_argument("--slug", required=True)
    p = sub.add_parser("diagnose"); p.add_argument("ws"); g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--sheet"); g.add_argument("--csv")
    p = sub.add_parser("approve"); p.add_argument("ws"); p.add_argument("part", choices=PARTS)
    p = sub.add_parser("build"); p.add_argument("ws")
    p = sub.add_parser("ship"); p.add_argument("ws"); p.add_argument("--replace", action="store_true")
    p = sub.add_parser("link"); p.add_argument("ws")
    p = sub.add_parser("qr"); p.add_argument("ws")
    a = ap.parse_args()
    ws = Path(a.ws).expanduser().resolve()
    {"init": lambda: cmd_init(ws, a.client, a.slug),
     "diagnose": lambda: cmd_diagnose(ws, a.sheet, a.csv),
     "approve": lambda: cmd_approve(ws, a.part),
     "build": lambda: cmd_build(ws),
     "ship": lambda: cmd_ship(ws, a.replace),
     "link": lambda: cmd_link(ws),
     "qr": lambda: cmd_qr(ws)}[a.cmd]()


if __name__ == "__main__":
    main()

#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "jinja2", "openpyxl", "pypdf", "segno"]
# ///
"""Self-check for wk.py. Run: uv run ~/.claude/skills/workshop-kit/scripts/test_wk.py"""
import importlib.util, shutil, tempfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("wk", Path(__file__).with_name("wk.py"))
wk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wk)

# Both form versions ("usas"/"usa") and the new approved-tools question resolve.
editora = ["Timestamp", "Função / equipa", "Que ferramentas usas quase todos os dias?", "Que ferramentas de IA já usaste?",
           "Que ferramentas de IA a empresa aprovou?", "Como descreves a tua fluência com IA hoje?",
           "Que tarefas te consomem mais tempo e gostavas de nunca mais fazer à mão?",
           "O que te bloqueia? Que problemas tens hoje que a IA podia resolver?",
           "Podes trazer um ficheiro ou exemplo real (anonimizado, se preciso) para usarmos ao vivo?"]
cols = wk.find_columns(editora)
assert cols == {"role": 1, "tools": 2, "ai_tools": 3, "approved": 4, "fluency": 5, "tasks": 6, "blocks": 7, "files": 8}, cols
older = [h.replace("usas", "usa").replace("usaste", "usou") for h in editora if "aprovou" not in h]
cols = wk.find_columns(older)
assert cols["tools"] == 2 and cols["ai_tools"] == 3 and cols["approved"] is None, cols

d = wk.diagnose([editora, ["t", "Marketing", "Word, Excel", "ChatGPT, Gemini", "Claude", "Uso todos os dias", "x", "y", "Não"],
                 ["t", "Finanças", "Excel", "ChatGPT", "", "Uso todos os dias", "a", "b", "Sim"], ["", "", "", "", "", "", "", "", ""]])
assert d["responses"] == 2 and d["counts"]["tools"] == {"Excel": 2, "Word": 1} and d["counts"]["ai_tools"]["ChatGPT"] == 2, d

# An x-embed's page goes into an iframe, so its html/body CSS cannot collapse the slides print to one page.
out = wk.embeds_to_iframes('<p>a</p><x-embed style="left:1px"><style>html,body{overflow:hidden}</style><script>a<b</script></x-embed>')
assert (out.startswith('<p>a</p><iframe style="left:1px" srcdoc="&lt;script&gt;requestAnimationFrame=')
        and out.endswith('&lt;style&gt;html,body{overflow:hidden}&lt;/style&gt;&lt;script&gt;a&lt;b&lt;/script&gt;"></iframe>')), out

# NIF checksum: 123456789 is valid, 123456780 is not.
assert wk.nif_ok("123456789") and not wk.nif_ok("123456780")

with tempfile.TemporaryDirectory() as tmp:
    ws = Path(tmp) / "ws"
    wk.cmd_init(ws, "Editora", "editora-2026-11")

    # set_field keeps comments and only touches approved.slides, not labels.slides.
    wk.set_field(ws, "slides", "2026-10-28", block="approved")
    text = (ws / "workshop.yaml").read_text()
    assert '  slides: "2026-10-28"' in text and "  slides: slides" in text and "# one per workshop" in text.lower(), text
    assert wk.load_cfg(ws)["approved"]["slides"] == "2026-10-28"

    # check() catches a missing data file, a long prompt, an unknown rule and a missing "Done when".
    ex = ws / "exercises/01-bad"
    ex.mkdir(parents=True)
    (ex / "exercise.md").write_text("---\ntitle: Bad one\nminutes: 10\nrule: nope\ndata: [missing.xlsx]\n---\n"
                                    "## Steps\n1. Do it.\n\n## Prompt\n" + "x" * 700 + "\n")
    rules = wk.load_rules(ws, wk.load_cfg(ws))
    xs, errors = wk.load_exercises(ws, rules)
    joined = " | ".join(errors)
    for needle in ("data/missing.xlsx not found", "prompt has 700 chars", 'rule "nope"', "no ## Done when"):
        assert needle in joined, joined
    assert "{skill}" not in str(rules) and "Skill" in str(rules)

    good = ws / "exercises/01-bad"
    (good / "data").mkdir()
    (good / "data/missing.xlsx").write_text("")
    (good / "exercise.md").write_text("---\ntitle: Good one\nminutes: 10\nrule: numbers\ndata: [missing.xlsx]\n---\n"
                                      "## Steps\n1. Attach the file.\n2. Paste the prompt.\n\n## Prompt\nSummarise it.\n\n"
                                      "## Done when\nThe total is 173.\n")
    xs, errors = wk.load_exercises(ws, rules)
    assert not errors and xs[0]["steps"] == ["Attach the file.", "Paste the prompt."] and xs[0]["done_when"] == "The total is 173."

    # load_demos() needs a title and every listed data file; build copies demo.md + data/.
    dm = ws / "demos/01-tour"
    dm.mkdir(parents=True)
    (dm / "demo.md").write_text("---\ntitle: Tour\nminutes: 3\nslide: demo-tour\ndata: [plano.pdf]\n---\n## Prompts\n1. Olá.\n")
    ds, derr = wk.load_demos(ws)
    assert derr == ["demos/01-tour: data/plano.pdf not found"], derr
    (dm / "data").mkdir()
    (dm / "data/plano.pdf").write_text("")
    ds, derr = wk.load_demos(ws)
    assert not derr and ds[0]["folder"] == "01-tour" and ds[0]["slide"] == "demo-tour", ds

    # The scan flags real-looking personal data and skips example.com and allowed strings.
    kit = Path(tmp) / "kit"
    kit.mkdir()
    (kit / "a.csv").write_text("ana@editora.pt,123456789,912 345 678\nbob@example.com,123456780\nteacher@school.pt\n")
    hits, skipped = wk.scan_personal_data(kit, allow=["teacher@school.pt"])
    assert len(hits) == 3 and not skipped and not any("bob" in h or "tea" in h for h in hits), hits

print("✓ test_wk.py: all checks passed")

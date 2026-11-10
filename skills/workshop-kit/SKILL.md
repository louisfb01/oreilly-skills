---
name: workshop-kit
description: Build corporate AI-literacy workshops end to end — from a Google Form responses sheet, client emails, meeting notes or any raw docs to a tailored deck (Claude Slides by default), hands-on exercises with data and solutions, a student kit (guide PDF, one-page cheat sheet, copy-button prompts page, exercise files, starter skills) and a shared Google Drive folder with a zip. Four modes — intake, draft, build, ship — with three approval checkpoints (slides, exercises, guides). Use this whenever the user mentions preparing, drafting, updating or packaging a workshop, training, formação or session for a client or team; drops form responses ("diagnóstico", "respostas") or a client brief; asks for workshop slides, exercises, cheat sheets, handouts or prompts for participants; or says "ship/upload the workshop kit", even if they never say "workshop-kit". Also use it to change what the AI-literacy core teaches.
---

# workshop-kit

> By Lucas Soares, from O'Reilly Skills Live. It is the skill behind real client workshops, with personal paths, brand and client names taken out. Start from it and make it yours.

The instructor (the user) teaches AI-literacy workshops to company teams. Every workshop has the same shape:

1. **Literacy block** — the same concepts every time: what an LLM does, tokens, the context window, *AI literacy = managing context*, context rot, lost in the middle, why models make things up, four hallucination checks, and the "if… then…" rules.
2. **Practice block** — exercises built on this client's real tasks and blockers, each one training one rule.

Students leave with a kit they can use on Monday. The kit is the product; the deck serves the room.

## Before the first workshop

- `uv` runs the script. Google Chrome prints the PDFs; set `CHROME=/path/to/chrome` if the script does not find it.
- The `gws` CLI (Google Workspace CLI), logged in, reads the form sheet and uploads the kit to Drive. Without it, `diagnose --csv` still works, and `ship` copies the kit to a synced Drive folder or leaves the zip on disk.
- The default deck format is Claude Slides, which needs Artifacts. Otherwise set `presentation: marp` or the name of any presentation skill.
- `core/` is one instructor's literacy block. To teach your own, see "Changing what the workshop teaches".
- The form questions `diagnose` reads are in `KEYS` in `wk.py`, as English and Portuguese phrases. Add your own form's wording there.

```
~/.claude/skills/workshop-kit/
  core/NN-*.md        the literacy block, English, one file per concept, in number order
  core/rules.yaml     the "if… then…" rules (deck slide, cheat sheet, prompts page)
  core/context_window.html   live demo for concept 03
  templates/          workshop.yaml, exercise.md, demo.md, guide.html, cheat-sheet.html
  scripts/wk.py       init · diagnose · approve · build · ship · qr  (run with: uv run)
  scripts/test_wk.py  self-check; run after editing wk.py

<client>/workshop-<YYYY-MM>/               ← "WS" below
  workshop.yaml       the facts every mode reads (template has comments)
  intake/             anything the instructor gives: responses.csv, emails, notes, PDFs, example files
  brief.md
  rules.yaml          only if the workshop language is not English (translated copy)
  deck/               project/ (Claude Slides) or deck.md (Marp) · assets.json · qr.png
  exercises/NN-slug/  exercise.md · data/ · solution/ · notes.md (notes stay with the instructor)
  demos/NN-slug/      demo.md · data/ (what the instructor opens live) · demos/make_data.py makes the data
  skills/<name>/      starter skills students install
  build/              made by wk.py build; safe to delete
```

`WK="uv run ~/.claude/skills/workshop-kit/scripts/wk.py"` in the commands below. If the skill is installed somewhere else, change that path. The first time, ask the instructor where workshop folders live; a good default for WS is `~/workshops/<client>/workshop-<YYYY-MM>/`.

## The flow and its checkpoints

```
intake → brief ─draft→ slides ─[CP1 approve]→ exercises ─[CP2 approve]→ guides ─[CP3 approve]→ ship
```

The instructor approves each major part before the next one is built, because rework downstream is expensive: exercises reference slides, guides render exercises. Do not start a part until the one before it is approved.

**A checkpoint is always the same four steps:**
1. Make the part current (publish the deck / run `$WK build WS`).
2. Open it for the instructor: `Artifact open` for the deck; `open` for `build/kit/3-*.html`, the exercise folders, or the PDFs.
3. Ask with AskUserQuestion: "Approve the {part}?" → `Approve` / `Change` (they type changes, or comment on the Slides artifact).
4. `Change` → edit the sources, rebuild, ask again. `Approve` → `$WK approve WS {slides|exercises|guides}`.

Approvals are gates, not locks: if the instructor later asks for a slide change, just make it.

## Mode: intake

Input is any mix of: a Google Form responses sheet URL, client emails (Gmail search), meeting notes or a transcript, client docs, example files. The instructor may drop files straight into `intake/`.

1. `$WK init WS --client "<Name>" --slug <client>-<YYYY-MM>`. Copy or save every input into `WS/intake/` (emails as `.md`/`.eml`).
2. If there is a form sheet: `$WK diagnose WS --sheet <url>` → `intake/responses.csv` + `intake/diagnosis.json` (counts for tools, AI tools, approved tools, fluency, files; free text for role, tasks, blocks). Missing columns are normal for older forms.
3. Read everything in `intake/` (use the pdf, docx and xlsx skills for those formats).
4. **Language.** The instructor's words win ("the workshop is in English"). Otherwise infer it from the intake (a form in Portuguese → `pt-PT` or `pt-BR`, by the client's country). If it is still unclear, ask. Set `language` in workshop.yaml. If it is not English, translate the `labels:` block in workshop.yaml (keep the keys).
5. Fill what you can in workshop.yaml (`client`, `form_url`, `tool` — the approved tool if the form says so, else what the client uses; `contact`). Ask the instructor only for what is still empty and matters now: date, duration.
6. Write `WS/brief.md` in English for the instructor, with the client's words quoted in their language:

```markdown
# <Client> · brief
Sources: <n> form answers · <each intake file>
Language: <code> (<why>)

## Who comes
<roles with counts> · Fluency: <distribution> · AI used: <counts> · Approved: <counts>

## Task groups
1. <group>: <examples from their answers> (<n>)

## Blocks
<block> (<n>) · … then one or two verbatim quotes

## Exercises → the rule each one trains
1. <exercise idea, from a task group> → <rule id>

## Real files
<who offered files, and when>
```

7. Show the brief (open it) and say what you assumed in one line. The instructor's reply starts `draft`.

## Mode: draft

### Slides (→ checkpoint 1)

Build the deck in `presentation` (default `claude-slides`). Structure for a ~3 h session: opening (3) · *Where we are* from `diagnosis.json` (3–4: fluency, tools, blockers, a quotes slide) · literacy block (~10–14, from `core/`) · practice topics and demos (~8–12) · one slide per exercise · 30-day plan and close (3–4). Scale with `duration_min`.

- **Literacy block:** read `core/NN-*.md` in number order. Each `##` is one slide; bullets are content; `> visual:` says what to draw; `> demo:` and `> notes:` go into speaker notes. Write the slides directly in the workshop language — no translation files are kept; the deck is the official copy. Keep the sources from front matter on the slide (small footer) or in notes.
- **Rules slide (concept 09):** render the rules from `WS/rules.yaml` if it exists, else `core/rules.yaml`. For a non-English workshop, first write `WS/rules.yaml`: same ids, translated `if`/`then`/`prompt`, `{project}`/`{skill}` replaced with the tool's names (claude: Project, Skill · chatgpt: Project, custom GPT · copilot: Notebook, agent).
- **Context window demo:** for a non-English workshop, write a translated copy to `WS/deck/context_window.html` (strings only; keep the code). The instructor opens it live.
- **Demo slides:** every slide where the instructor shows something live in the tool gets a folder `WS/demos/NN-slug/` (copy `templates/demo.md`): the exact prompts, what to show, what the room should see, and every file it needs in `data/`. Number the folders in deck order. Fictional data comes from one `WS/demos/make_data.py` (uv inline metadata) that asserts the numbers the slide quotes. The slide names the file path (`demos › NN-slug › data › file`) and the folder in its notes, so the instructor never hunts for a file mid-demo. Pick files this audience reads at work (a PDF of their kind of document, their kind of Excel); a demo that needs a tricky setup ("lost in the middle") is better cut than shown badly. A demo may reuse an exercise file: copy it into the demo's `data/`.
- **Exercise slides:** id `ex-<folder>` (e.g. `ex-01-sales-sheet`), so `wk.py build` can tell when a slide is older than its exercise. Show title, minutes, the rule, the steps and "Done when"; point to the prompts page for the prompt text if it does not fit.

**claude-slides:** create the deck once from the Slides Artifact type (`Artifact quickstart` with intent `slides` gives its `type_url`), then follow the instructions the create result carries. Use `root` = `WS/deck` so the files live in `WS/deck/project/`. Save the URL to `deck_url`. Look: the client's design system if `design_system` is set; otherwise the instructor's default design system (`Artifact list type "Design System"`). If there is none, say so and use a plain look: one dark, one light, one accent. Every image you upload: record `{"/_blob/<id>": "deck/<local file>"}` in `WS/deck/assets.json` so the PDF print can find it.
**marp:** write `WS/deck/deck.md` and build it with a Marp skill if one is installed, else the Marp CLI.
**any other skill name:** invoke that skill; put its output in `WS/deck/` and an exported `deck/slides.pdf`.

→ **Checkpoint 1: slides.**

### Exercises (→ checkpoint 2)

One exercise per task group in the brief, usually 4–6. Copy `templates/exercise.md` to `WS/exercises/NN-slug/exercise.md`; the template's comments are the rules `wk.py build` enforces (title ≤ 40 chars, ≤ 5 steps of ≤ 90 chars, prompt ≤ 600 chars, a `## Done when`, every `data:` file exists, `rule:` is a rules.yaml id).

What makes an exercise work in the room (lessons from past workshops):
- **Their task, their words.** The prompt is written in the voice of someone on their team ("I'm in sales at a publisher…"), names the file, the task, the output format and one limit.
- **A check the pair can see.** "Done when" is a number that must match, a word that must not appear, a column that must exist. Never "it looks good". Build the data so the check has an answer.
- **Data: fictional by default**, made from the brief — realistic for their domain, with the quirks their real files have (an ERP export with merged headers, a PDF report with a totals row). Use `example.com` emails, invented names, no real tax or phone numbers. When the client sends real files, swap them in; `ship` scans everything for personal data.
- **`solution/` goes to students** (expected output, a worked prompt). `notes.md` — what goes wrong in class, timings — stays with the instructor.
- **One rule per exercise**, and the slide shows it, so the literacy block keeps paying off.
- Write the exercise slides into the deck now (ids `ex-<folder>`) and republish.

**Starter skills:** for each exercise whose rule is `same-procedure` (or each repeated procedure in the brief), write `WS/skills/<name>/SKILL.md` + `tests.md` in the workshop language: a short procedure the student installs as-is. `build` zips it with the folder at the zip root (what Claude's skill upload expects) and, for `tool: chatgpt`, also writes the body as custom-GPT instructions.

Then `$WK build WS` (fix every ✗ it prints) → open `build/kit/3-*.html` and `WS/exercises/` → **Checkpoint 2: exercises.**

### Guides (→ checkpoint 3)

Write `first_week` in workshop.yaml: five short lines, Monday to Friday, each one small action with this team's real work and the kit's files ("Mon: create a Project «Sales sheets» with 3 good examples"). `$WK build WS` → open `1-*.pdf` and `2-*.pdf` → **Checkpoint 3: guides** (the shape of the guide and the cheat sheet). Layout changes go in `templates/guide.html` / `templates/cheat-sheet.html` (Jinja2) when the instructor wants them for every workshop, which is the usual case.

## Mode: build

`$WK build WS` deletes `build/` and makes it again — never edit files in `build/`; edit the sources. It stops on any exercise error (nothing written) and warns when a deck slide is older than its exercise. Kit, with names from `labels:`:

```
build/kit/<slug>-participants/
  1-guide.pdf        page 1: first week + rules; then one page per exercise
  2-cheat-sheet.pdf  the rules on one A4 page
  3-prompts.html     every prompt with a copy button; search; works offline
  4-slides.pdf       deck/slides.pdf if present (an export wins), else Chrome prints deck/project/slides
  exercises/NN-slug/ prompt.txt · data/ · solution/
  demos/NN-slug/     demo.md · data/
  skills/<name>.zip
```

Only those paths are copied — never `notes.md`, stray outputs, lock files or `__pycache__`.

## Mode: ship

Ship makes a public link, so ask the instructor first ("Ship the kit to Drive and share it with anyone who has the link?"). Then `$WK ship WS`:

1. Refuses unless all three checkpoints are approved.
2. Builds, then scans every kit file (text, docx, pptx, xlsx, pdf, zips) for emails, Portuguese tax numbers (NIF, with checksum), Portuguese mobile numbers and PT IBANs. The patterns are in `wk.py` under "personal data scan"; add your country's formats there. `example.com`-style emails are ignored; exact strings in `pii_ok` are allowed (e.g. the instructor's own email on a slide). Hits stop the ship: fix the file or, if the string is meant to be there, ask the instructor before adding it to `pii_ok`.
3. Zips the kit, uploads kit + zip with gws to `My Drive/workshops/<slug>/`, shares it as "anyone with the link can view", writes `drive_link`. The files also show up in the instructor's synced Drive folder.

Exit codes Claude must handle:
- **3 — `GWS_FAILED`:** the kit was copied to the synced Drive folder instead (`COPIED_TO:`), and Drive for Desktop uploads it. Tell the instructor why gws failed, where the copy is, and — if `PARTIAL_DRIVE_FOLDER:` is printed — that a half-uploaded folder exists (sync would create a second folder with the same name). Ask whether they want to upload by hand, re-authenticate (`! gws auth login`) and retry, or leave it to sync.
- **4 — folder has files:** ask before re-running with `--replace`. It moves the old contents to the Drive trash (recoverable) and uploads into the same folder, so the link and the deck's QR never change. An empty folder (made early for the QR) needs no `--replace`.

QR before ship: `$WK link WS` makes and shares the empty `workshops/<slug>/` folder and writes `drive_link`, so the closing slide can carry the QR before the guides are approved. ship later fills the same folder; the link never changes. The instructor runs `link` themselves: the public share is a permission grant.

After a successful ship (or after `link`):
- `$WK qr WS` → `deck/qr.png`. Upload it to the deck and add or update the closing slide: QR + the link + "everything from today is here".
- Draft (never send) a Gmail message to `contact`: the link, what is in the kit in three lines, and the zip. Show the instructor the draft.

## Changing what the workshop teaches

The core is meant to evolve. To change it, edit `core/`:
- **Edit a concept:** change its file. One `##` = one slide; keep slides to 3–4 bullets.
- **Add or reorder:** create `core/NN-name.md`; the number sets the order (use `05b-…` to insert without renaming).
- **Remove:** delete the file (ask the instructor first).
- **Sources:** every claim with a number or a study gets a source in front matter. When a fact ages (window sizes, model names), prefer a durable phrasing ("hundreds of pages") over a number that will be wrong next year.
- **Rules:** keep `id`s stable — exercises reference them.

Old workshops are not rebuilt automatically; the next draft reads the new core.

## Editing wk.py

Run `uv run ~/.claude/skills/workshop-kit/scripts/test_wk.py` after any change. The form column keys are in `KEYS` (a list of phrases per column, matched lowercase, first header wins); add a phrase when a new form version words a question differently.

## Feedback log

After each run, add an entry to `FEEDBACK.md`. When the same correction shows up twice, move it into this file and mark the entry as promoted.

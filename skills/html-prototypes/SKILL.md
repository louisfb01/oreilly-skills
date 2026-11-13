---
name: html-prototypes
description: "Build a quick HTML page instead of a long chat answer: a review page for a deck or a document, options to compare side by side, a small tool, a plan, an explainer, a diagram, a tracker, or an editor that exports its result. One self-contained file, no build step, checked at desktop and phone width, then published where the user's agent can host it (a Claude artifact, a ChatGPT site, or a local file). Use for any request for a page, review page, prototype, mockup, tool or visual explainer in HTML."
---

# HTML Prototypes

How to build quick, custom HTML pages for the user, whichever agent builds them and wherever they are published. The page is the same single file on every host; only the publishing step changes. A good page is one the user can react on, and whose result comes back to the agent without retyping.

> Start from this file, then make it yours: every time you correct the agent, it logs the correction in `FEEDBACK.md`, and corrections you repeat become rules here.

**Credits.** Most of these practices come from two public sources. Read them; they are short and full of examples:

- Thariq, "The unreasonable effectiveness of HTML": https://thariqs.github.io/html-effectiveness/
- Simon Willison, "Useful patterns for building HTML tools" (December 10, 2025): https://simonwillison.net/2025/Dec/10/html-tools/

When you update this skill from those pages, read the pages themselves, not a tool's summary of them.

## Load first

1. `FEEDBACK.md` in this folder: the user's past corrections.
2. An earlier page the user approved, if one exists. Start from its look and structure (rule 14).
3. The host's own instructions (Hosts, below). They win over this file.

## When a page beats Markdown

Make an HTML page instead of a Markdown answer when one of these is true:

- **Several options to choose from.** Lay them side by side so the user can point at one. "Reacting is easier than imagining." (Thariq)
- **The information is spatial.** A room, a board, a diff, a call graph, a timeline. Markdown flattens them.
- **Motion or interaction is the question.** "Motion and interaction can't be described, only felt." (Thariq)
- **A recurring document should get read.** Status updates and post-mortems gain from a little structure and color.
- **A new topic needs navigating.** Collapsible sections, tabs and a glossary read differently from the same words in one long column.
- **The user has to decide or edit something** and hand the result back (review pages and editors, below).

Anything that must keep running, update itself or carry real users is no longer a prototype: give it its own repo.

## How to build the page

- **Nothing external by default.** No external scripts, stylesheets or web fonts. The file opens straight from disk.
- **System font stacks as tokens** on `:root`: a serif, a sans and a mono stack. Mono for code, paths, labels and numbers.
- **A small palette as tokens** on `:root` (one accent, one success color, a ladder of neutrals), named by role, never hard-coded in rules.
- **A viewport meta tag, CSS grid, a reading column of about 640 to 980 px, and one or two breakpoints** so the page reflows on a phone. `clamp()` for type that scales.
- **Native elements first:** `<details>` for collapsible steps, `position: sticky` for an "On this page" list, real `<button>`s, `<table>` for tables, inline `<svg>` for figures, `data-` attributes as JavaScript hooks.
- **A copy helper on every page that hands text back:** `navigator.clipboard.writeText`, a hidden-textarea fallback, and the button reading "Copied" for a second or two.
- **Little JavaScript.** A slide deck is a handful of `<section>` tags and about twenty lines of script.
- **The request at the top** when it helps the reader: the prompt that produced the page, then the page.

## Build rules

1. **One self-contained file.** Inline CSS and JavaScript. Images as inline SVG or small data URIs. It is the least trouble to host, share and hand to another agent.
2. **No React, no build step.** Simon Willison: "I prompt “no react” and skip that whole rabbit hole entirely."
3. **Keep it small.** A few hundred lines that any model can reread and change later.
4. **Libraries only when they earn it,** from a CDN with the exact version in the URL. Check which CDNs the host allows.
5. **Phone and desktop.** It works at 390 px wide with 16 px side gutters and no horizontal scroll, and at desktop width.
6. **Tokens for color and type.** Define light and dark tokens when the host has themes, and check contrast in both.
7. **Real data, or labelled sample data.** Use real numbers and sources when they exist. A mock says it is a mock. Numbers on the page agree with each other, and every link goes somewhere real.
8. **Copy and paste as the main input and output.** Add "Copy" buttons; copying by hand on a phone is fiddly.
9. **Every editor ends with an export.** Thariq: "Always end with an export button that turns whatever you did in the UI back into something you can paste into the agent or commit." Typical ones: "Copy as markdown", "Copy my review", "Copy JSON", next to "Reset" and a live count of changes.
10. **State only when it helps.** For a page someone will bookmark or share, state in the URL. For more, `localStorage` wrapped in `try/catch`, and the page still works when it is empty. For a review that runs over several days or several people, use the host's database if it has one, so the agent can read the result directly (review pages, below).
11. **Files in and out without a server.** `<input type="file">` reads a file in the browser; a page can generate a download by itself.
12. **Browser APIs only with open CORS.** An LLM API key never goes in the page: anyone who opens it can read the key.
13. **Heavier compute stays in the browser** when needed: WebAssembly builds such as Pyodide or Tesseract.js.
14. **Start from a working example.** A model with one or two existing pages in context writes working code far more often. Look for an earlier page of the user's before writing from scratch.
15. **Say where it came from.** A footer with the sources and the date. On a review page, each item shows what it is based on.
16. **Accessible basics.** Real buttons and labels, visible focus, contrast that holds in every theme, and a keyboard path for anything draggable.
17. **Start plain; let the user ask for more.** Left alone, a model adds stat tiles, toolbars and rows of filter chips to everything. Don't. Start with a plain background, one accent color, one title, and at most one row of tabs, one search field and one toggle. Add a control only when the user names it. When the user approves a look, write it in this file and start every later page from it.
18. **A working list is one line per item, with the action on the line.** For a page the user works through item by item (send, review, tick), every row shows the buttons they need without opening anything: the main action first, then the links that exist, then the done mark. Text they will only copy, and any editing, sits behind one quiet "more". Anything filled in later (replies, results) goes in its own tab.

## Review pages

The most useful page to build first: the user reviews something the agent made (slides, a script, a document, ad copy, options) on the page, and the agent reads the review back and makes the next round at the same link.

- **Show the real thing.** Render each item as it will be seen (the slide as a slide, the post as a post), one item at a time or as a list, with a strip or index to jump around.
- **One decision per item, one click:** Keep, Revise or Remove (or approve / change). Colors for the three states, and a count of what is still not reviewed.
- **A note per item.** A text box next to the item. The user will often dictate into it, so make it large, save as they type, and never lose a note on reload.
- **Let the user edit the text in place** when wording is the point (`contenteditable`), and store each edit separately from the source, so the agent can fold it in exactly as typed.
- **Context beside the item, collapsed or quiet:** what changed since the last version, what the item is based on (sources), and for a talk the speaker notes and the planned time.
- **The review comes back without retyping.** Either a "Copy my review" button that produces Markdown the agent can act on, or the host's database, which the agent reads directly. Say on the page which one it is and whether the review is saved.
- **Rounds.** Each round bumps a version on the items that changed and marks them ("changed", "new"), so the user rereads only those. Removed items stay listed. Republish to the same link; keep the previous round's source as a backup.
- **Apply the review only when the user says the round is done.** Notes on the page are a draft until then.
- **A brief tab** for what the agent decided on its own, open questions, and anything the user should check.
- **Keep it plain** (rule 17). The item, the three buttons, the note. Everything else is secondary.

## Other patterns by job

- **Options to choose from.** Three or four directions side by side, rendered from the same data, so the only variable is the design. Each has a label, a one-line stance, pros and cons, and a "best for" note, then a recommendation. Chips to keep or skip details assemble a reply at the bottom.
- **Mock before you wire.** One file mocking the feature with fake data, buttons to switch layouts, the design decisions listed so the user can push back, and the open questions answered by chips that fill a reply.
- **Animation sandbox.** The motion in isolation, with buttons to swap the easing and timings, and a copy-paste block of the result.
- **Plan.** Scope chips, milestones, a diagram with its legend in one sentence, rough mockups marked as rough, and a risk table. For review, order by what the user is most likely to change: decisions first, each with its alternative, then the build order, then the mechanical work collapsed.
- **Explainer.** A TL;DR first, expandable steps, one live demo with a caption saying what to notice, a comparison table and a short glossary.
- **Report.** Key numbers first, highlights as outcomes, one small chart with a caption, sources and date in the footer.
- **Diagram or board.** Inline SVG or positioned boxes, flat fills, a legend, and boxes that open on click to show the next level. Good for presenting an idea in a call instead of slides.
- **Spatial plan.** A room, a trip, a layout: several arrangements to flip through, the measurements that matter, and a list of what each one needs.
- **Tracker.** One line per item with its action (rule 18).
- **Editors.** The exact thing being edited (a board with drag between columns, toggles with dependency warnings, a template with a live preview), ending in its copy-out button.

## Hosts

The page is the same file everywhere. Pick the host the user's agent already has.

- **Claude artifact** (Claude Code or claude.ai). A private link the user can share. The host's own instructions win: follow its page contract (title, theme tokens, allowed CDNs, size limit), and use its storage features for a review that Claude should read back. Republish from the same file to keep the same link.
- **ChatGPT site** (from Codex). A stable URL that Codex or a scheduled task can keep updating. Reuse the existing project when updating; never create a duplicate. A new site stays owner-only unless the user says it should be public.
- **Any other agent, or local only.** Write `index.html` and open it in the browser. The user reacts on it and uses the Copy button to hand the result back.

Chat hosts run pages in a sandbox that often cannot load data or images from other sites, so keep the page self-contained.

## Check before handing over

1. Open it for real, in a browser or with headless Chrome or Playwright. Look at desktop width and at 390 px.
   - Put `[hidden]{display:none!important}` in the page's own CSS. Any rule such as `.x{display:grid}` beats the browser's `hidden`, and every closed tab or panel shows at once.
2. Nothing overlaps or overflows, the console is clean, every link resolves, and the numbers agree with each other and with their source.
3. Every button works, especially export, copy and reset. On a review page, save a decision and a note, reload, and confirm they are still there.
4. On a host, check the published page, not only the local file.
5. Hand over the link (or the path) with one line on what it shows, and a screenshot when the user is reviewing a visual.

## Guardrails

- No secrets or API keys in the page.
- Nothing private on a page that will be shared. Ask before making a page public.
- Do not invent facts, file paths or numbers to fill a page; mark sample data as sample.
- Never make a page that imitates a real company, person or record.

## Feedback log

After each run, add an entry to `FEEDBACK.md`. When the same correction shows up twice, or the user states it as a rule, move it into this file and mark the entry as promoted.

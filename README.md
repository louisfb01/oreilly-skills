# O'Reilly Skills Live: skills from my sessions

Agent skills and setup material from my weekly sessions in the **O'Reilly Skills Live** series, co-hosted with Lucas Soares. One folder per week. Every skill works with Claude Code, Codex, or any agent that reads `SKILL.md` files, and each one is a starting point: adapt it to your own work.

By [Louis-François Bouchard](https://www.louisbouchard.ai/), CTO and co-founder of Towards AI.

## Weeks

| Week | Session | What you get |
| --- | --- | --- |
| 1 · Nov 10, 2026 | [How I build talks with Claude](weeks/01-how-i-build-talks/) | The [`talk-decks`](skills/talk-decks/) skill, a prompt to build your own from your past threads, and the [slides (PDF)](weeks/01-how-i-build-talks/how-i-build-talks-with-claude-slides.pdf) From Lucas: the [`workshop-kit`](skills/workshop-kit/) skill |
| 2 · Nov 17, 2026 | [A second brain my agents can read](weeks/02-second-brain/) | Points to [obsidian-agent-vault-template](https://github.com/louisfb01/obsidian-agent-vault-template), a ready-to-use vault with rules, skills and a feedback loop |
| 3 | Coming soon | |
| 4 | Coming soon | |
| 5 | Coming soon | |
| 6 | Coming soon | |

## Install the skills

**Claude Code**, for all your projects:

```bash
git clone https://github.com/louisfb01/oreilly-skills.git
mkdir -p ~/.claude/skills
cp -r oreilly-skills/skills/* ~/.claude/skills/
```

For one project only, copy them into `.claude/skills/` inside that project instead.

**Codex:** copy the same folders into `~/.codex/skills/`.

**Any other agent:** tell it to read the skill's `SKILL.md` before the task.

To take just one skill, copy only its folder, for example `skills/talk-decks/`.

## How these skills are meant to be used

Each skill folder has:

- `SKILL.md`: how the job is done. This is what the agent reads.
- `FEEDBACK.md`: where your agent logs what you corrected after each run. When you repeat a correction, it moves into `SKILL.md`. After a few runs, the skill is yours.
- `references/` (optional): longer guides the skill loads only when it needs them.

The rules in these skills came from my own corrections. Yours will differ, so expect to edit them.

## Repo layout

```
skills/<skill>/            installable skills (copy these into your agent's skills folder)
weeks/<NN-topic>/          one page per session: what it covered, how to use its skill, extras
templates/                 skeletons for adding a new week and a new skill
```

Adding a week: copy `templates/week/` to `weeks/<NN-topic>/`, and if the week has a skill, copy `templates/skill/` to `skills/<skill-name>/`. Then add a row to the table above.

## License

MIT. See [LICENSE](LICENSE).

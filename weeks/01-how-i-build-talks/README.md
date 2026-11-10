# Week 1: How I build talks with Claude

O'Reilly Skills Live, Nov 10, 2026. How I go from a brain dump to a talk I can actually give, and where I stop letting Claude drive.

**Slides:** [How I build talks with Claude (PDF, 17 slides)](how-i-build-talks-with-claude-slides.pdf)

**Skill:** [`talk-decks`](../../skills/talk-decks/). It's a general version of the skill I use for every talk. It gets a decent first draft in a good presentation style, then follows your directions.

![The loop: initial preparation (a talk skill), then for every talk: brain dump, plan, first draft, feedback voice notes, practice run, Google Slides](loop.png)

## The loop

**Initial preparation (once):** a skill made of your own corrections. Start from `talk-decks`, or build yours with [make-your-own.md](make-your-own.md).

Then, for every talk:

1. **Brain dump**, out loud, starting from what this room should leave able to do.
2. **Plan**: a one-liner per slide, iterated until the order works.
3. **First draft**, end to end, story first.
4. **Feedback voice notes**: one long dictated note per pass, by slide number, with the why.
5. **Practice run**, timed and out loud. The story breaks here; your next voice note fixes it. Repeat 4 and 5.
6. **Google Slides** (or PowerPoint) with build animations, fine-tuned by hand while you practice.

Claude does most of step 3 and the conversion in step 6. You do most of 1, 4, 5 and the final pass. The story is yours.

## Use it

Install the skill (see the [main README](../../README.md#install-the-skills)), then ask your agent:

> I'm giving a 15-minute talk on X to Y. Here's my brain dump: … Use the talk-decks skill and give me a plan first.

Then review the plan, ask for the first draft, and send your feedback as one voice note per pass, by slide number.

## Make it yours

The rules in the skill came from my corrections. [make-your-own.md](make-your-own.md) is a prompt that reads your past Claude Code or Codex threads, finds what you kept correcting, and writes your own version of the skill.

## Lucas's side: workshop-kit

In the same session, Lucas Soares showed [`workshop-kit`](../../skills/workshop-kit/), the skill behind Lucas's client workshops. It turns a client intake form into a deck, exercises, handouts and a shared folder, and it rebuilds the kit when a source changes. It needs `uv` and Chrome, plus the `gws` CLI for Google Sheets and Drive.

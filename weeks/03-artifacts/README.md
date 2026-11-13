# Week 3: Artifacts mastermind

O'Reilly Skills Live, Nov 24, 2026. Why I ask my agent for a custom page for almost everything I work on, and the rules that make those pages good: review pages for my decks, a board I present from, a 3D plan of a room, trackers.

**Skill:** [`html-prototypes`](../../skills/html-prototypes/). It's a general version of the skill behind every page I build. It works with Claude artifacts, ChatGPT sites from Codex, or any agent that can write an HTML file.

## The idea

An artifact is one HTML file your agent writes for you. Because the agent can read it back, you can do more on it than in the chat:

1. **The agent builds the page**: the real thing to react to, not a description of it.
2. **You react on the page**: keep, revise, remove, a note per item, often dictated.
3. **The agent reads it back** and makes the next round at the same link.

The skill covers when a page beats a chat answer, 18 build rules (one file, no React, phone and desktop, real data, a copy button, start plain), how to build a review page, other patterns, and what to check before the page reaches you.

## Use it

Install the skill (see the [main README](../../README.md#install-the-skills)), then ask your agent:

> Use the html-prototypes skill. Build me a review page for this draft: one item at a time, Keep / Revise / Remove, a note per item, and a way to hand you my review.

Or for a decision:

> Use the html-prototypes skill. Show me three options for X side by side, on one page I can open on my phone.

## Make it yours

Rule 17 says to start plain. When a page looks the way you like, tell your agent to write that look into the skill, so every later page starts from it. Each correction you give goes to `FEEDBACK.md`; the ones you repeat become rules.

## Credits

The skill builds on Thariq's ["The unreasonable effectiveness of HTML"](https://thariqs.github.io/html-effectiveness/) and Simon Willison's ["Useful patterns for building HTML tools"](https://simonwillison.net/2025/Dec/10/html-tools/).

---
id: context-rot
sources:
  - "Hong, Troynikov & Huber, Context Rot: How Increasing Input Tokens Impacts LLM Performance, Chroma, July 2025: https://research.trychroma.com/context-rot"
---
## Context rot: more context, less reliability
- Chroma tested 18 models on deliberately simple tasks and changed only one thing: the length of the input.
- Performance dropped as the input grew, on every model, even when the task stayed the same.
- Text that looks like the answer but is wrong (a distractor) made it worse.
> visual: a line chart, accuracy falling as input tokens grow (redraw from the Chroma figure)
> notes: Models tested were mid-2025 models. Newer ones are better, but the direction holds.

## Signs it is time to start over
- It contradicts what you asked earlier.
- It "forgets" the start of the conversation.
- It mixes two tasks, or the answers get vague.
- The fix: ask for a summary, open a new chat, paste the summary.
> visual: four warning cards, then one arrow to "new chat + summary"

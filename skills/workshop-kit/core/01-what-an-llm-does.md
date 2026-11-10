---
id: what-an-llm-does
sources:
  - "Karpathy, Intro to Large Language Models (talk, 2023): https://www.youtube.com/watch?v=zjkBMFhNj_g"
---
## At its core, it predicts the next piece of text
- A language model reads everything in front of it and picks a likely continuation.
- It repeats this, one piece at a time, until the answer is done.
- Chat, search, file analysis: all of it runs on this one move.
> visual: "The capital of Portugal is ___" with probability bars (Lisbon 92%, Porto 4%, a city 2%…)
> notes: Ask the room to finish the sentence. They just did what the model does.

## Fluent is not the same as true
- The model learns which text is likely, not which text is correct.
- A confident, well-written answer can still be wrong.
- What changes the result is what you put in front of it. That is the rest of today.
> visual: two answers side by side, equally polished; one has a wrong number circled
> notes: This slide sets up context management and the hallucination checks.

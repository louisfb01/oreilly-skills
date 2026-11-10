---
id: why-models-make-things-up
sources:
  - "Kalai, Nachum, Vempala & Zhang, Why Language Models Hallucinate, OpenAI, 2025: https://arxiv.org/abs/2509.04664"
---
## Why models make things up
- The model produces plausible text. Without a source in front of it, plausible is all it has.
- Training and benchmarks reward a confident guess over "I do not know", so the model learns to guess.
- It gets worse with rare facts, exact numbers, recent events and an overloaded context.
- It is the default behaviour without sources, not a rare bug.
> visual: one sentence — "Fluency is not provenance." — on a dark statement slide
> notes: Sycophancy amplifies it: models are tuned to please, so they agree with wrong premises. Mention it in one line.

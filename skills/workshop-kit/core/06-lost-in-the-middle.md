---
id: lost-in-the-middle
sources:
  - "Liu et al., Lost in the Middle: How Language Models Use Long Contexts, TACL 2024: https://arxiv.org/abs/2307.03172"
---
## The model does not read everything equally
- Models use information at the start and at the end of the context best.
- Information in the middle of a long input is the most likely to be missed.
- So position is part of the prompt.
> visual: a U-shaped curve, accuracy by position of the key fact (start, middle, end)

## Put what matters at the edges
- Critical instructions go first, or are repeated at the very end.
- With a long document, state the question before and after it.
- Ask for exactly the part you need, not "everything in this file".
> visual: a long document with the question pinned above and below it

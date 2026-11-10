---
id: tokens
sources:
  - "OpenAI tokenizer (try it live): https://platform.openai.com/tokenizer"
  - "Anthropic, token counting: https://docs.claude.com/en/docs/build-with-claude/token-counting"
---
## Tokens: fragments, not words
- The model does not read words. It reads tokens: chunks of 3–4 characters on average.
- "unbelievable" can be 3 tokens. A number like 2026 can be split too.
- Rough rule: a page of plain text is about 600–800 tokens. Tables, scans and other languages often cost more.
> visual: one sentence in the workshop language, split into coloured token chips
> demo: paste a sentence from the client's own documents into a tokenizer
> notes: Split a number on screen to explain why models slip on arithmetic and exact figures.

## Everything counts against the limit
- Your messages, the model's answers, attached files and hidden instructions are all tokens.
- A 40-page PDF can use more space than an hour of chat.
> visual: a stacked bar: instructions · your messages · answers · one PDF (largest block)

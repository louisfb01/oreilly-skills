---
id: context-window
sources:
  - "Anthropic, context windows: https://docs.claude.com/en/docs/build-with-claude/context-windows"
demo: context_window.html
---
## The context window is a desk of fixed size
- It holds everything the model can see right now: instructions, files, every message and answer.
- It fills up with every turn of the conversation.
- When it is full, the oldest parts drop out or get compressed. The model no longer sees them.
> visual: a desk that fills with paper as the chat goes on; the first sheets fall off the edge
> demo: context_window.html — add a document, add off-topic chat, watch the important fact drop out
> notes: Do not quote exact window sizes. They change with every model release. Say "hundreds of pages" instead.

## Bigger windows do not fix it
- A larger window lets you put more on the desk. It does not make the model read it all equally well.
- The next two slides show why.
> visual: a huge desk, cluttered; a hand searching for one sheet

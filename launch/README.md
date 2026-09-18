# Launching the seats

This folder holds everything needed to bring the four seats up. It is a work in progress until the manual run-through has produced tested prompts.

## Seat table

| Seat | Mandate file | Model (initial) |
|---|---|---|
| Architect | [`../mandates/architect.md`](../mandates/architect.md) | Fable 5.1 |
| Builder | [`../mandates/builder.md`](../mandates/builder.md) | Opus 5 |
| Verifier | [`../mandates/verifier.md`](../mandates/verifier.md) | Fable 5.1 |
| Spec Auditor | [`../mandates/spec-auditor.md`](../mandates/spec-auditor.md) | Sonnet 5 |

Set a session's model with `/model` inside Claude Code, or start it with the `--model` flag.

## Manual procedure

1. Start the Architect window and run:
   ```
   /jam
   Start a Jam session as the architect for this project.
   ```
2. In each other window, run `/jam` and join as that role, for example:
   ```
   /jam
   Join this project as the builder.
   ```
3. Confirm every seat shows as **Connected** in Jam Desktop.
4. Post the brief and specification in the room.

> **TODO:** record the exact first prompt that attaches each seat's mandate file, once tested.
> **TODO:** record whether the Architect hands out join prompts or whether windows can find the room on their own.
> **TODO:** decide whether each seat needs its own working tree to avoid edit collisions.

## Scripted launch (planned)

Once the manual procedure is proven, a script here will open one terminal per seat, each with the right model and first prompt.

## Reattaching a dropped seat

```
Reattach this session to the existing <role> Jam peer.
```

# dark-factory

A reusable four-seat software factory for BAND Desktop (Jam): an Architect, a Builder, a Verifier, and a Spec Auditor, all running as Claude Code sessions in one BAND room.

The mandates are generic. Hand this repo to a team building something completely different and it still works. See [FACTORY.md](FACTORY.md) for the crew, routing, and a typical run.

## Repository layout

```
README.md          this file
FACTORY.md         the factory description: crew, routing, flow, design principles
mandates/          one standing-instruction file per seat
launch/            how to bring the seats up, plus a brief template
stage-N/           the solution for each completed stage (added as stages are finished)
```

## Prerequisites

- A [BAND account](https://app.band.ai/)
- [Jam Desktop](https://docs.band.ai/jam), signed in
- [Claude Code](https://code.claude.com/docs/en/setup), installed and signed in
- Access to the models listed in the crew table in [FACTORY.md](FACTORY.md). Any model can be substituted per seat.

Jam Desktop is documented for macOS and Linux. It also ships a Windows installer, and this factory has been run there.

## Quick start

Full details are in [`launch/`](launch/). In outline:

1. Open Jam Desktop and confirm your Claude Code sessions can connect.
2. Open four Claude Code windows in this repository's root, one per seat, each on the model you want for that seat.
3. In the first window, start a Jam session as the Architect (`/jam`).
4. In the other three, join the same Jam as the Builder, Verifier, and Spec Auditor.
5. Give each seat its mandate file from [`mandates/`](mandates/).
6. Paste your task brief and specification into the room. Use [`launch/brief-template.md`](launch/brief-template.md) for the shape.
7. Step in only when the Architect surfaces a decision.

> **TODO:** confirm exactly how a seat receives its mandate file and how joining windows find the room, then replace steps 3 to 5 with the tested prompts.

If a window restarts, reattach it to its existing seat instead of creating a new one:

```
Reattach this session to the existing <role> Jam peer.
```

## Reusing the factory

Keep mandates generic. Put everything specific to your project, such as the specification, requirements, and constraints, in the brief you paste into the room, not in `mandates/`.

## Secrets

Never commit credentials. `.gitignore` excludes the usual suspects, but check before you push.

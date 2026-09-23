# dark-factory

A reusable four-seat software factory for BAND Desktop (Jam): an Architect, a Builder, a Verifier, and a Spec Auditor, all running as Claude Code sessions in one BAND room.

The mandates are generic. Hand this repo to a team building something completely different and it still works. See [FACTORY.md](FACTORY.md) for the crew, routing, and a typical run.

## Repository layout

```
README.md          this file
FACTORY.md         the factory description: crew, routing, flow, design principles
mandates/          one standing-instruction file per seat
launch/            the launch script, the launch plan, and a brief template
stage-N/           the solution for each completed stage (added as stages are finished)
```

## Prerequisites

- A [BAND account](https://app.band.ai/)
- [Jam Desktop](https://docs.band.ai/jam), signed in. `jam whoami` must succeed; if it does not, run `jam init` first.
- [Claude Code](https://code.claude.com/docs/en/setup), installed and signed in to a Claude subscription. The seats ride that login (`--runtime-auth subscription`); no `ANTHROPIC_API_KEY` is used.
- Access to the models listed in the crew table in [FACTORY.md](FACTORY.md). Any model can be substituted per seat.

Jam Desktop is documented for macOS and Linux. It also ships a Windows installer, and this factory has been run there.

## Quick start

The seats run headless: Jam's own daemon owns four Claude Code processes, one per seat. Full details are in [`launch/`](launch/).

1. Confirm the prerequisites above, in particular that `jam whoami` succeeds.
2. From the repository root, run the launch script:
   ```powershell
   launch/launch-headless.ps1
   ```
   It creates the four seats, creates one shared room, adds you and the three other seats to it, and prints the room's `chat_id` plus the two commands below with the real values filled in. It is safe to re-run.
3. Post your brief, using [`launch/brief-template.md`](launch/brief-template.md) for the shape:
   ```
   jam room send <chat_id> "@Architect <your brief>" --mention <architect_agent_id>
   ```
4. Watch the room:
   ```
   jam room messages <chat_id>
   ```
5. Step in only when the Architect surfaces a decision.

All four seats share the repository root as their working directory. Per-seat isolation is not implemented yet; see [`launch/README.md`](launch/README.md).

### Alternative: terminal-attached seats

You can instead run each seat as a visible Claude Code window that you drive yourself. This is the path to use when you want to watch or take over a seat directly.

1. Open Jam Desktop and confirm your Claude Code sessions can connect.
2. Open four Claude Code windows in this repository's root, one per seat, each on the model you want for that seat.
3. In each window, join the shared Jam as that role:
   ```
   /jam as <role>
   ```
4. Give each seat its mandate file from [`mandates/`](mandates/) — start the window with `claude --append-system-prompt` from the seat's mandate.
5. Paste your task brief and specification into the room. Use [`launch/brief-template.md`](launch/brief-template.md) for the shape.

If one of these windows restarts, reattach it to its existing seat instead of creating a new one:

```
Reattach this session to the existing <role> Jam peer.
```

Restart and reattach have not been tested for the headless path.

## Reusing the factory

Keep mandates generic. Put everything specific to your project, such as the specification, requirements, and constraints, in the brief you paste into the room, not in `mandates/`.

## Secrets

Never commit credentials. `.gitignore` excludes the usual suspects, but check before you push.

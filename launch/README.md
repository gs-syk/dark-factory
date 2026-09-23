# Launching the seats

This folder holds everything needed to bring the four seats up. The headless path is scripted and proven; run [`launch-headless.ps1`](launch-headless.ps1) from the repository root. The terminal-attached path below is the manual alternative. [`PLAN.md`](PLAN.md) records how the recipe was derived and what is still open.

## Seat table

| Seat | Mandate file | Model (initial) | `--runtime-model` id |
|---|---|---|---|
| Architect | [`../mandates/architect.md`](../mandates/architect.md) | Opus 5 | `claude-opus-5` |
| Builder | [`../mandates/builder.md`](../mandates/builder.md) | Opus 5 | `claude-opus-5` |
| Verifier | [`../mandates/verifier.md`](../mandates/verifier.md) | Fable 5.1 | `claude-fable-5-1` |
| Spec Auditor | [`../mandates/spec-auditor.md`](../mandates/spec-auditor.md) | Sonnet 5 | `claude-sonnet-5` |

For a headless seat the model is fixed at creation by `--runtime-model`; change it in the `$Seats` table in `launch-headless.ps1`. For a terminal-attached seat, set the model with `/model` inside Claude Code, or start it with the `--model` flag.

## Scripted launch

`launch-headless.ps1` brings the whole factory up. Run it from the repository root:

```powershell
launch/launch-headless.ps1
```

It does three things:

1. **Creates each seat** as a Jam-owned headless Claude Code process:
   ```
   jam agent create --session <seat-session> --transport claude-code-cli --name <seat-name> \
     --runtime-auth subscription --runtime-model <model-id> --cwd <repo> \
     --instructions-file <repo>/mandates/<seat>.md --json
   ```
   `--runtime-auth subscription` rides your existing Claude Code login, so no `ANTHROPIC_API_KEY` is needed. `--instructions-file` live-links the seat's mandate.
2. **Creates one shared room**, run as the Architect seat:
   ```
   jam chat new --as <owner>/factory-architect
   ```
3. **Adds the participants** — you plus the other three seats:
   ```
   jam chat add <chat_id> <owner> <owner>/factory-builder <owner>/factory-verifier \
     <owner>/factory-spec-auditor --as <owner>/factory-architect
   ```

It then prints the two follow-up commands with the real values filled in:

```
jam room send <chat_id> "@Architect <your brief>" --mention <architect_agent_id>
jam room messages <chat_id>
```

Two gotchas the script works around, recorded in [`PLAN.md`](PLAN.md): `--as` must name a peer with a live worker (a stopped peer, or the bare human account with no `--as`, both fail "peer not found"), and `jam room send` returns HTTP 404 on a `chat new` room until the human is a participant.

### Re-running it

The script is idempotent. It records the seat agent ids and the room's `chat_id` in `launch/.factory-state.json`, which is gitignored, and skips anything already recorded.

If a seat exists in Jam but is missing from that state file, the script stops with a reconciliation warning rather than guessing. As the warning says: find the seat's `agent_id` (`jam status --as <owner>/<seat>` will not show it; check Jam Desktop's Runtime tab) and add it to the state file's `seats` map, or remove the seat with `jam rm --as <owner>/<seat>` and re-run the script to recreate it cleanly.

### Known limitation: shared working tree

All four headless seats are created with the repository root as their `--cwd`. There is no per-seat isolation, so a Builder writing files and another seat reading them are working in the same tree. Per-seat working trees are not resolved for either launch path; see [`PLAN.md`](PLAN.md) "Open questions and risks".

## Terminal-attached launch (alternative)

Each seat runs as a visible Claude Code window you drive yourself.

1. Open four Claude Code windows in the repository root, one per seat, each on that seat's model.
2. Deliver the mandate by starting the window with `claude --append-system-prompt` from the seat's mandate file.
3. In each window, join the shared Jam as that role:
   ```
   /jam as <role>
   ```
4. Confirm every seat shows as **Connected** in Jam Desktop.
5. Post the brief and specification in the room.

### Reattaching a dropped seat

For a terminal-attached window that restarted:

```
Reattach this session to the existing <role> Jam peer.
```

Restart and reattach have not been tested for the headless path, and no headless reattach procedure is documented here.

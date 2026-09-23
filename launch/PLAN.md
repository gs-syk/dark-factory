# Launch automation plan

Status: **headless spike proven for all four seats.** Written 2026-09-18, updated 2026-09-23 after the headless runtime spike. Facts marked *(unverified)* came from summarized web fetches or `--help` output and have not been run.

## Decision so far

The factory is the hackathon entry, not a tool for building a separate entry. BAND's [hacker guide](https://www.band.ai/hacker-guide) calls Jam Desktop a build tool "separate from shipped project" and judges submissions on crew, routing, flow, and a "delete test" ([FACTORY.md](../FACTORY.md) already follows that shape). That originally pointed at **SDK agents** as the target, with Jam terminals as the dev/demo view.

**Revised 2026-09-23:** the SDK path (`ClaudeSDKAdapter`) needs a separate `ANTHROPIC_API_KEY` — pay-per-token via console.anthropic.com — which the owner's account doesn't have (Claude Pro subscription only, no API billing). The **Jam-owned headless runtime** (`jam agent create --transport claude-code-cli --runtime-auth subscription`) rides the existing Claude Code subscription login instead, at zero extra cost, and has now been spiked successfully for all four seats (see below). It is a Jam/`jamd`-managed runtime rather than a fully independent process, so it may sit less cleanly against the hacker guide's "Jam Desktop is separate from the shipped project" framing than a true SDK agent would — that risk is accepted for now in exchange for zero API cost and a proven, working path. Revisit the SDK path only if judging risk turns out to matter more than the cost.

## Where we are

- A manual smoke test worked: four Claude Code windows joined one BAND room through `/jam as <role>`. Handles came out as `gcsworksyk/architect-r498`, `developer-r498`, `spec-auditor-r498`, `verifier-r499`.
- The README and [`launch/README.md`](README.md) still carry open TODOs: how a seat receives its mandate, how joiners find the room, and whether seats need separate working trees.

## The three runtimes

| | 1. Terminal-attached | 2. Jam-owned headless (target) | 3. SDK agent (fallback / judging-risk hedge) |
|---|---|---|---|
| What | Claude Code window with the `band-peer` plugin, joined via `/jam as <role> [with <handle>]` | `jam agent create --transport claude-code-cli` (also `acp`, `codex-app-server`, `copilot-sdk`) | Own process running `Agent.create(adapter=…)` then `agent.run()` from `band-sdk` |
| Run by | A person, in a visible window | The `jamd` daemon | Any process: laptop, VPS, container |
| Model | `claude --model` | `--runtime-model`, `--runtime-effort`, `--claude-permission-mode` | Adapter argument |
| Mandate | `claude --append-system-prompt` | `--instructions-file` (live-linked) | Adapter `custom_section` |
| Documented | Yes ([docs.band.ai/jam](https://docs.band.ai/jam)) | No, only in the installed CLI's `--help` | Yes (SDK repos and docs) |

Terminal-attached needs a join handoff: joiners need the Architect's generated handle (`jam list` shows local peers; `jam onboard --suffix` may allow a shared suffix *(unverified)*).

## Headless spike results (2026-09-23)

All four seats spiked successfully as Jam-owned headless agents, in one shared room, on subscription auth (`ANTHROPIC_API_KEY` never set). Routing worked exactly to spec: only the `@mentioned` Architect took a turn; Builder, Verifier, and Spec Auditor stayed silent despite being room members. The Architect independently read `FACTORY.md` from the repo (not just its `--instructions-file` mandate) and answered correctly from it.

**The working recipe** (each command's quirks were discovered by trial and error — the CLI's own errors are not always about the argument they seem to name):

```
# 1. Create each seat: a parked, running, Jam-owned Claude Code process.
#    --session must be unique per seat. --instructions-file live-links the mandate.
#    --runtime-model accepts the four Claude 5-family ids (claude-sonnet-5, claude-opus-5,
#    claude-fable-5-1) and falls back to claude-sonnet-5 if omitted.
jam agent create --session factory-architect-spike --transport claude-code-cli \
  --name factory-architect --runtime-auth subscription --runtime-model claude-fable-5-1 \
  --cwd <repo> --instructions-file mandates/architect.md --json
# repeat per seat with unique --session/--name/--runtime-model/--instructions-file

# 2. One seat creates its own chat (a fresh Band chat, distinct from `jam room list`'s
#    "rooms" resource). This must be run `--as` a peer with a LIVE worker — a stopped
#    peer, or the bare human account with no `--as`, both fail "peer not found".
jam chat new --as gcsworksyk/factory-architect
# -> prints a chat_id

# 3. That seat adds the human and the other three seats as participants.
jam chat add <chat_id> gcsworksyk gcsworksyk/factory-builder gcsworksyk/factory-verifier \
  gcsworksyk/factory-spec-auditor --as gcsworksyk/factory-architect

# 4. The human posts via the Human API — this only works once the human is already a
#    participant (step 3); posting before that gives HTTP 404, not a permissions error.
jam room send <chat_id> "@Architect ..." --mention <architect_agent_id>

# 5. Poll for the reply.
jam room messages <chat_id>
```

Dead ends worth not repeating: `jam invite --new` (meant for this) returned HTTP 409 or 404 depending on args and was never gotten to work cleanly; `jam room send` to a `chat new`-created id 404s until the human is added as a chat participant first. `jam chat new`/`jam chat add`/`jam chat participants` all require `--as` a peer with a running worker, not the bare human session.

The four spike agents and their shared chat were left running/live after the test (owner's choice, 2026-09-23) rather than torn down — `jam rm --as gcsworksyk/factory-<seat>` removes one when ready.

## Target design (SDK path — de-scoped, see Decision)

```
factory.yaml         seats: role, model, mandate file, permission_mode, worktree
launch/provision.py  register the four agents (idempotent) -> agent_config.yaml (gitignored)
launch/run_seat.py   build the adapter from one manifest entry; Agent.create(...).run()
launch/kickoff.py    create the room, add the four seats and the human, post the brief
launch/launch.ps1    create git worktrees, start four seats in Windows Terminal tabs
```

One manifest entry per seat keeps the mandates generic and models swappable. Each seat is its own process.

What the SDK path gives us *(unverified until spiked)*:

- `ClaudeSDKAdapter(model=…, custom_section=<mandate>, cwd=<worktree>, permission_mode=…)` runs a Claude Code session per room, with file and shell tools plus Band messaging tools. This meets the Builder's tooling needs, which the plain Anthropic adapter would not.
- Registration is scriptable: `POST https://api.band.ai/api/v1/me/agents/register` with `{"agent":{"name","description"}}` returns the agent id and an API key shown **once**. It needs an `X-API-Key` header and a JWT.
- `agent_config.yaml` can hold several named agents, read with `load_agent_config("<name>")`.
- Only mentioned agents see a message, matching our routing rules.
- Different providers per seat are possible, which would strengthen Verifier independence beyond "different Claude tier".

## Local environment

- Python 3.12.9 present. `band-sdk` 3.1.1 is on PyPI (extras: `[claude_sdk]`, `[anthropic]`, `[langgraph]`, and others).
- **Node and `uv` are not installed**, so use Python with `pip`/venv.
- `claude` 2.1.277 at `C:\Users\GStoien\.local\bin\claude.EXE`. `wt.exe` (Windows Terminal) is available.
- `jam agent create --dry-run --json --session <name> --transport claude-code-cli` passed its probe (Claude Code started, no agent created), so the owned-runtime path is a viable fallback.
- BAND docs say Jam is macOS/Linux only; the README notes it also runs on Windows here.

## Open questions and risks

1. ~~**Credentials.**~~ **Resolved (headless path):** no API key or JWT needed — `--runtime-auth subscription` rides the existing Claude Code login. (Still open for the SDK path, now de-scoped.)
2. **Restart recovery.** Not yet tested for the headless path. The mandates' restart rule (announce, read room history and plan, resume) still needs to be exercised against a real `jam restart`/`jam attach`.
3. **Permissions.** The spike used `--claude-permission-mode` default (`auto`); this let the Architect run Bash/Glob/Read freely and reply without a hitch. Not yet tested with Builder actually writing files — worth confirming `auto` doesn't require a human to sit and approve edits, since that would clash with "Architect is the only escalation point".
4. **Agent quota.** Free tier allows 10 agents. Four spike agents plus four earlier terminal-attached peers (`architect-r498` etc., currently stopped) means 8 of 10 are in use. Check before creating more.
5. ~~**Kickoff.**~~ **Resolved:** see the recipe above (`jam chat new` / `jam chat add` / `jam room send`). Still open: whether this needs to run from a live terminal-attached seat every time, or can be scripted once and reused across restarts.
6. **Working trees.** Not yet addressed. All four spike seats share one `cwd` (the repo root) with no isolation — fine for a routing/response spike, not fine for a Builder actually editing files while others read.

## Next steps

1. ~~**Spike.**~~ **Done** — all four seats, headless, on subscription auth, correct `@mention` routing confirmed. See "Headless spike results" above.
2. **Script the recipe.** Turn the proven command sequence into `launch/spike_headless.ps1` (create four seats, one shared chat, add participants) so it's not manual next time.
3. **Working trees.** Decide and implement per-seat `git worktree` isolation, especially for Builder before it starts writing real code.
4. **Restart test** (question 2) and permission-mode check with a real write (question 3), then replace the TODOs in `launch/README.md` and the README quick start with tested commands.
5. **Optional:** keep `launch/spike_seat.py` (SDK path) as a fallback if judging risk on the headless path turns out to matter — not deleted, just de-prioritized.

## Sources

- [Jam docs](https://docs.band.ai/jam), [Hacker Guide](https://www.band.ai/hacker-guide), [docs index](https://docs.band.ai/llms.txt)
- [band-sdk-python](https://github.com/band-ai/band-sdk-python), [band-sdk-typescript](https://github.com/band-ai/band-sdk-typescript)
- [Claude SDK adapter](https://docs.band.ai/integrations/sdks/tutorials/claude-sdk.md), [Register external agent](https://docs.band.ai/api/human-api/human-api-agents/register-my-agent.md), [Environment variables](https://docs.band.ai/integrations/sdks/tutorials/environment-variables.md), [Agent lifecycle](https://docs.band.ai/integrations/sdks/tutorials/agent-lifecycle.md)

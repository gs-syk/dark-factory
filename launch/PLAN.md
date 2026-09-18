# Launch automation plan

Status: **planning, nothing built yet.** Written 2026-09-18 after a smoke test and a docs/CLI survey. Facts marked *(unverified)* came from summarized web fetches or `--help` output and have not been run.

## Decision so far

The factory is the hackathon entry, not a tool for building a separate entry. BAND's [hacker guide](https://www.band.ai/hacker-guide) calls Jam Desktop a build tool "separate from shipped project" and judges submissions on crew, routing, flow, and a "delete test" ([FACTORY.md](../FACTORY.md) already follows that shape). So the seats should ship as **SDK agents**, and Jam terminals remain the development and demo view.

## Where we are

- A manual smoke test worked: four Claude Code windows joined one BAND room through `/jam as <role>`. Handles came out as `gcsworksyk/architect-r498`, `developer-r498`, `spec-auditor-r498`, `verifier-r499`.
- The README and [`launch/README.md`](README.md) still carry open TODOs: how a seat receives its mandate, how joiners find the room, and whether seats need separate working trees.

## The three runtimes

| | 1. Terminal-attached | 2. Jam-owned headless | 3. SDK agent (target) |
|---|---|---|---|
| What | Claude Code window with the `band-peer` plugin, joined via `/jam as <role> [with <handle>]` | `jam agent create --transport claude-code-cli` (also `acp`, `codex-app-server`, `copilot-sdk`) | Own process running `Agent.create(adapter=…)` then `agent.run()` from `band-sdk` |
| Run by | A person, in a visible window | The `jamd` daemon | Any process: laptop, VPS, container |
| Model | `claude --model` | `--runtime-model`, `--runtime-effort`, `--claude-permission-mode` | Adapter argument |
| Mandate | `claude --append-system-prompt` | `--instructions-file` (live-linked) | Adapter `custom_section` |
| Documented | Yes ([docs.band.ai/jam](https://docs.band.ai/jam)) | No, only in the installed CLI's `--help` | Yes (SDK repos and docs) |

Terminal-attached needs a join handoff: joiners need the Architect's generated handle (`jam list` shows local peers; `jam onboard --suffix` may allow a shared suffix *(unverified)*).

## Target design (SDK path)

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

1. **Credentials.** Registration needs an API key plus a JWT. Does `jam init --user-api-key` provide both? If not, register the four agents once in the dashboard ([app.band.ai/agents](https://app.band.ai/agents)) and script everything after that.
2. **Restart recovery.** The SDK docs say nothing about reconnecting after a restart. The mandates' restart rule (announce, read room history and plan, resume) has to carry this. Test it.
3. **Permissions.** `approval_mode="manual"` posts permission requests into the room, which clashes with "Architect is the only escalation point". Prefer `acceptEdits` or `bypassPermissions` inside per-seat git worktrees.
4. **Agent quota.** Free tier allows 10 agents. Check that deleting an agent frees a slot before scripting teardown and re-provision.
5. **Kickoff.** How the human posts the brief and adds the seats to one room (`jam room send`, Human API, or the SDK's `band_create_chatroom` / `band_add_participant`). Not yet checked.
6. **Working trees.** Separate `git worktree` per seat is the default proposal; the Builder's output needs a defined path back to a shared branch for the Verifier's clean-checkout run.
7. **API key vs subscription.** Whether the Claude adapter uses the local Claude login or needs `ANTHROPIC_API_KEY`.

## Next steps

1. **Spike (one seat).** Create a venv, `pip install "band-sdk[claude_sdk]"`, register `factory-architect`, run it with `mandates/architect.md` as `custom_section`, and confirm it answers an `@mention` in a room. This settles questions 1, 3, 5, and 7. It creates a real agent on the account and needs credentials, so it needs the owner's go-ahead.
2. **Manifest.** Write `factory.yaml` and `run_seat.py` once the spike works.
3. **Provisioning and kickoff scripts**, then `launch.ps1`.
4. **Restart test** (question 2), then replace the TODOs in `launch/README.md` and the README quick start with tested commands.
5. **Optional:** spike the owned-runtime path (`jam agent create`) as a fallback.

## Sources

- [Jam docs](https://docs.band.ai/jam), [Hacker Guide](https://www.band.ai/hacker-guide), [docs index](https://docs.band.ai/llms.txt)
- [band-sdk-python](https://github.com/band-ai/band-sdk-python), [band-sdk-typescript](https://github.com/band-ai/band-sdk-typescript)
- [Claude SDK adapter](https://docs.band.ai/integrations/sdks/tutorials/claude-sdk.md), [Register external agent](https://docs.band.ai/api/human-api/human-api-agents/register-my-agent.md), [Environment variables](https://docs.band.ai/integrations/sdks/tutorials/environment-variables.md), [Agent lifecycle](https://docs.band.ai/integrations/sdks/tutorials/agent-lifecycle.md)

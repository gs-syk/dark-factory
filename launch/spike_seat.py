"""One-seat spike: run the Architect as a band-sdk agent instead of a manual Jam terminal.

Prerequisites:
  1. pip install "band-sdk[claude_sdk]" python-dotenv
  2. Register the agent at https://app.band.ai/agents, then add it to agent_config.yaml
     (repo root, gitignored):
         factory-architect:
           agent_id: "..."
           api_key: "..."
  3. Put ANTHROPIC_API_KEY in a .env file at the repo root (also gitignored).

Run:
  python launch/spike_seat.py
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from band import Agent, configure_logging
from band.adapters import ClaudeSDKAdapter
from band.config import load_agent_config

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENT_NAME = "factory-architect"
MANDATE_FILE = REPO_ROOT / "mandates" / "architect.md"


async def main() -> None:
    load_dotenv(REPO_ROOT / ".env")
    configure_logging(root_level="INFO")

    try:
        agent_id, api_key = load_agent_config(AGENT_NAME)
    except Exception as exc:
        sys.exit(
            f"Could not load '{AGENT_NAME}' from agent_config.yaml: {exc}\n"
            "Register the agent at https://app.band.ai/agents and add its "
            "agent_id/api_key to agent_config.yaml first."
        )

    mandate = MANDATE_FILE.read_text(encoding="utf-8")

    adapter = ClaudeSDKAdapter(
        model="claude-sonnet-4-5",
        custom_section=mandate,
        cwd=str(REPO_ROOT),
        permission_mode="acceptEdits",
    )

    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())

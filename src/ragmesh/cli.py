"""Thin async CLI: `ragmesh "question"` builds the agent and prints its answer."""

import asyncio
import sys

from langchain_core.messages import HumanMessage

from ragmesh.agent import build_agent


async def _run(question: str) -> None:
    agent = await build_agent()
    result = await agent.ainvoke({"messages": [HumanMessage(content=question)]})
    print(result["messages"][-1].content)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: ragmesh <question>", file=sys.stderr)
        raise SystemExit(1)
    asyncio.run(_run(" ".join(sys.argv[1:])))


if __name__ == "__main__":
    main()

"""
agent.py — Minimal agentic loop: Ollama model + MCP tools.

The loop:
  1. Start the MCP server as a subprocess (stdio transport)
  2. Ask Ollama what tools are available
  3. Send the user's question to Ollama with those tool definitions
  4. If Ollama calls a tool → execute it via MCP → feed the result back
  5. Repeat until Ollama gives a plain text answer

Usage:
  python agent.py "How do I request more storage on Sherlock?"
  python agent.py  # prompts for a question interactively

On Sherlock, Ollama runs as a batch job on a GPU node rather than on
localhost (see ollama_server.sh + SHERLOCK.md). Point this script at that
server by exporting OLLAMA_BASE_URL before running it, e.g.:

  export OLLAMA_HOST=$(cat ~/.ollama_server)
  export OLLAMA_BASE_URL=http://$OLLAMA_HOST/v1
  python agent.py "..."

With no OLLAMA_BASE_URL set, it falls back to localhost:11434 (e.g. when
using the SSH port-forwarding approach, or running Ollama locally).
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

# ── Configuration ─────────────────────────────────────────────────────────────

OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
MODEL      = os.environ.get("OLLAMA_MODEL", "llama3.1")  # any Ollama model that supports tool calling

# ── Helpers ───────────────────────────────────────────────────────────────────

def mcp_tool_to_openai(tool) -> dict:
    """Convert an MCP tool definition to OpenAI function-calling format."""
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


# ── Main agentic loop ─────────────────────────────────────────────────────────

async def run(question: str) -> None:
    ollama = OpenAI(base_url=OLLAMA_URL, api_key="ollama")

    # Start the MCP server as a local subprocess over stdio.
    # Use sys.executable (not "python") so the subprocess runs with the same
    # interpreter/venv as this script — on Sherlock, "python" outside a venv
    # is often the old system Python 2, not python3.
    server_params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools and translate them for Ollama.
            tools_result = await session.list_tools()
            tools = [mcp_tool_to_openai(t) for t in tools_result.tools]

            print(f"Tools available: {[t['function']['name'] for t in tools]}\n")

            messages = [{"role": "user", "content": question}]

            # Agentic loop — keeps going until the model stops calling tools.
            while True:
                response = ollama.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=tools,
                )
                message = response.choices[0].message

                if not message.tool_calls:
                    # No more tool calls — we have the final answer.
                    print("Answer:", message.content)
                    break

                # The model wants to call one or more tools.
                messages.append(message)

                for call in message.tool_calls:
                    name = call.function.name
                    args = json.loads(call.function.arguments)

                    print(f"→ calling {name}({args})")
                    result = await session.call_tool(name, args)

                    # Feed the tool result back into the conversation.
                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": str(result.content[0].text if result.content else ""),
                    })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Question: ").strip()

    asyncio.run(run(question))

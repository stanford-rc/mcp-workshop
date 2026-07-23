"""
mcp_server.py — Minimal MCP server for the workshop.

Exposes two tools:
  list_docs  — see what doc files are available
  read_doc   — read the contents of one file

Run standalone (stdio transport, for use with agent.py):
  python mcp_server.py
"""

from pathlib import Path

from mcp.server.fastmcp import FastMCP

DOCS_DIR = Path(__file__).parent / "docs"

mcp = FastMCP("Workshop Docs")


@mcp.tool()
def list_docs() -> list[str]:
    """List available documentation files in the docs/ directory."""
    return sorted(f.name for f in DOCS_DIR.glob("*.md"))


@mcp.tool()
def read_doc(filename: str) -> str:
    """
    Read the contents of a documentation file.

    Args:
        filename: File name returned by list_docs (e.g. "storage.md")
    """
    path = DOCS_DIR / filename
    if not path.exists():
        return f"File not found: {filename}. Use list_docs to see available files."
    return path.read_text()


if __name__ == "__main__":
    mcp.run()  # stdio transport by default

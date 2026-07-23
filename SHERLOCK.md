# Running this workshop on Sherlock

This starter kit runs an MCP server (`mcp_server.py`) alongside a small
agentic loop (`agent.py`) that talks to a local LLM via Ollama. On a laptop
you'd just run `ollama serve` and hit `localhost:11434`. On Sherlock, Ollama
needs a GPU, so the server runs as a batch job on a compute node instead —
everything else stays the same.

## 1. Set up the Python environment

From a login node, in this directory:

```bash
ml python/3.12.1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Start the Ollama server as a batch job

```bash
sbatch ollama_server.sh
```

Check the output file for the assigned node/port once it starts:

```bash
cat ollama_server-<jobid>.out
```

The same endpoint is also written to `~/.ollama_server` for convenience.

## 3. Pull the model

Ollama needs the model pulled on the same node the server is running on.
From a **second terminal**, SSH to that node and load the module again:

```bash
ssh <node-from-step-2>
ml ollama
export OLLAMA_HOST=$(cat ~/.ollama_server)
ollama pull llama3.1
```

(`llama3.1` is the default in `agent.py`; swap in any Ollama model that
supports tool calling, e.g. `qwen2.5-coder:7b`.)

## 4. Point the agent at the server

Back on the login node (or wherever you'll run `agent.py`), in the same
terminal you'll use to run the workshop:

```bash
export OLLAMA_HOST=$(cat ~/.ollama_server)
export OLLAMA_BASE_URL=http://$OLLAMA_HOST/v1
```

`agent.py` reads `OLLAMA_BASE_URL` (falling back to `localhost:11434` if
unset) and `OLLAMA_MODEL` (falling back to `llama3.1`).

## 5. Run it

```bash
source .venv/bin/activate   # if not already active
python agent.py "How do I request more storage on Sherlock?"
```

You should see the agent list the available MCP tools, call `list_docs`
and/or `read_doc`, and print a final answer sourced from `docs/storage.md`.

## Alternative: SSH port forwarding

If you'd rather not export `OLLAMA_BASE_URL` (e.g. a tool doesn't support
env var interpolation), forward the compute node's port to your local
`11434` instead, and leave `agent.py`'s default in place:

```bash
ssh -NfL 11434:localhost:${OLLAMA_HOST#*:} ${OLLAMA_HOST%:*}
```

## Notes

- The batch job requests 2 hours (`--time 02:00:00`); resubmit if it expires
  mid-workshop.
- Ollama caps context at 4k tokens on GPUs with <24GB memory. This
  workshop's docs are tiny so it won't matter, but if you extend it with
  larger docs and see truncated answers, see "Increasing context window
  size" on the [Sherlock Ollama docs](https://www.sherlock.stanford.edu/docs/software/using/ollama/).

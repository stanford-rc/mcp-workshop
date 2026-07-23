# Running this workshop on Sherlock

This starter kit runs an MCP server (`mcp_server.py`) alongside a small
agentic loop (`agent.py`) that talks to a local LLM via Ollama. Ollama needs
a GPU. There are two ways to run it:

- **Interactive** — best while you're learning/tweaking things: a live GPU
  session you can poke at.
- **Batch** — best once it works and you want to run it hands-off (e.g. a
  script that submits questions and comes back later for the answer).

Both need the one-time setup below first.

## One-time setup

Virtual environments should be built on a compute node, not a login node, so
grab a quick interactive allocation for this part:

```bash
sh_dev
ml python/3.12.1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate
exit
```

This only needs to happen once — `.venv/` persists in this directory for
both workflows below.

## Interactive

```bash
sh_dev -g 1
tmux new -s ollama
ml ollama
ollama serve
```

Detach from tmux with `Ctrl-b d` — the server keeps running on this node.
(Reattach any time with `tmux attach -t ollama`.)

Back in your regular shell (still on the same GPU node — `sh_dev` put you
there directly, no SSH needed):

```bash
ml ollama
ollama pull llama3.1
source .venv/bin/activate
python agent.py "How do I request more storage on Sherlock?"
```

No `OLLAMA_HOST`/`OLLAMA_BASE_URL` exports needed — `agent.py` defaults to
`localhost:11434`, which is correct since Ollama is running on this same
node.

## Batch

`batch_job.sh` does the whole thing in one non-interactive job: starts
Ollama, pulls the model, runs the agent against a question, exits.

```bash
sbatch batch_job.sh "How do I request more storage on Sherlock?"
```

Check the result once it finishes:

```bash
squeue -u $USER              # watch it run
cat mcp-workshop-<jobid>.out # read the answer
```

Swap models with `OLLAMA_MODEL`:

```bash
sbatch --export=OLLAMA_MODEL=qwen2.5-coder:7b batch_job.sh "..."
```

This is the version worth building on for anything production-like — e.g.
a wrapper script that loops over a list of questions and submits one job
per question, or a cron-scheduled job that reprocesses new docs.

## Notes

- Ollama caps context at 4k tokens on GPUs with <24GB memory. This
  workshop's docs are tiny so it won't matter, but if you extend it with
  larger docs and see truncated answers, see "Increasing context window
  size" on the [Sherlock Ollama docs](https://www.sherlock.stanford.edu/docs/software/using/ollama/).
- Running Ollama as its own long-lived batch job (separate from the agent,
  shared across multiple runs/users) is also possible — see "Ollama server
  as a batch job" in the docs above — but the all-in-one `batch_job.sh` is
  simpler when each run is a single question.

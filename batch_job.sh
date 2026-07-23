#!/bin/bash
#SBATCH --job-name      mcp-workshop
#SBATCH --output        mcp-workshop-%j.out
#SBATCH --error         mcp-workshop-%j.err
#SBATCH --partition     gpu
#SBATCH --gpus          1
#SBATCH --constraints   [GPU_MEM:16GB|GPU_MEM:24GB|GPU_MEM:32GB|GPU_MEM:48GB|GPU_MEM:80GB]
#SBATCH --cpus-per-task 4
#SBATCH --time          00:30:00
#
# Runs the full pipeline non-interactively in one job: starts Ollama, pulls
# the model, runs the agent against a question, then exits.
#
# Requires .venv/ to already exist (see SHERLOCK.md "One-time setup").
#
# Usage:
#   sbatch batch_job.sh "How do I request more storage on Sherlock?"

ml ollama
ml python/3.12.1

# Start Ollama in the background, within this job's own GPU allocation.
ollama serve &
OLLAMA_PID=$!

# Wait for the server to come up before using it.
until ollama list &>/dev/null; do
    sleep 1
done

# No-op (fast) if already pulled/cached.
ollama pull "${OLLAMA_MODEL:-llama3.1}"

source .venv/bin/activate
python agent.py "$@"

kill $OLLAMA_PID

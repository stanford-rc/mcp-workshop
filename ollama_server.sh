#!/bin/bash
#SBATCH --job-name      mcp-workshop-ollama-%j
#SBATCH --output        ollama_server-%j.out
#SBATCH --error         ollama_server-%j.err
#SBATCH --partition     gpu
#SBATCH --gpus          1
#SBATCH --constraints   [GPU_MEM:16GB|GPU_MEM:24GB|GPU_MEM:32GB|GPU_MEM:48GB|GPU_MEM:80GB]
#SBATCH --cpus-per-task 4
#SBATCH --time          02:00:00

# Load the Ollama module
ml ollama

# Choose a random port for the Ollama server (>1024)
OLLAMA_PORT=$(( RANDOM % 60000 + 1024 ))
while (echo > /dev/tcp/localhost/$OLLAMA_PORT) &>/dev/null; do
    OLLAMA_PORT=$(( ( RANDOM % 60000 ) + 1024 ))
done

# Save endpoint to a known location so agent.py / the CLI can find it
echo "$SLURM_NODELIST:$OLLAMA_PORT" > ~/.ollama_server

echo "-----------------------------------------------------------------"
echo "Starting Ollama server on host $SLURM_NODELIST, port $OLLAMA_PORT"
echo "use OLLAMA_HOST=$SLURM_NODELIST:$OLLAMA_PORT to connect"
echo "-----------------------------------------------------------------"

OLLAMA_HOST=0.0.0.0:$OLLAMA_PORT ollama serve

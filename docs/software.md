# Software on Sherlock

Sherlock uses the Lmod module system to manage software.

## Loading software
```bash
module spider matlab          # search for a module
module load matlab/R2023b     # load a specific version
module list                   # see what you have loaded
module purge                  # unload everything
```

## Commonly used modules
- Python: `module load python/3.12`
- CUDA: `module load cuda/12`
- R: `module load R/4.3`
- PyTorch: `module load pytorch`

## Installing your own packages

**Python** — use a virtual environment:
```bash
python -m venv ~/myenv
source ~/myenv/bin/activate
pip install numpy pandas
```

**R** — install to your home directory:
```r
install.packages("tidyverse")
```

## Requesting new software
If you need software that isn't available as a module, open a ticket at
srcc-support@stanford.edu.

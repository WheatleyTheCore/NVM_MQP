#!/bin/bash
#SBATCH --job-name=NVM_MQP
#SBATCH --output=results_%j.out
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=2-00:00:00

# Load Python environment
module load python/3.x
source /venv/bin/activate

# Execute script
python main.py
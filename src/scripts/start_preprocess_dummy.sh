#!/bin/bash
#SBATCH --job-name=train_model       # Job name
#SBATCH --partition=gpu              # Partition to use
#SBATCH --gres=gpu:4                 # Request 4 GPUs
#SBATCH --ntasks=1                   # Request 1 task
#SBATCH --time=2-00:00:00            # Time limit (2 days)
#SBATCH --mem=16000                  # Memory request (16 GB)
#SBATCH --qos=prio                   # Quality of Service

# Activate the virtual environment
source $HOME/venv/bin/activate

# Navigate to the project directory
cd $HOME/dsitls-project/src/ || exit

# Set environment variables for CUDA and XLA
export CUDA_DIR=$CUDA_HOME
export XLA_FLAGS="--xla_gpu_cuda_data_dir=$CUDA_DIR"

# Define the default parameters
CONFIG_CLASS="Conf_COAD_DUMMY_LABEL"
RESAMPLE_ROUND=0
USE_LOCAL_DATA=true

# Parse command-line arguments for custom parameters
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --config_class) CONFIG_CLASS="$2"; shift ;;
        --resample_round) RESAMPLE_ROUND="$2"; shift ;;
        --use_local_data) USE_LOCAL_DATA="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Run the model.py script with the specified parameters
python preprocess_test.py --config_class "$CONFIG_CLASS"

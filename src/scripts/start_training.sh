#!/bin/bash

# Default sbatch parameters
SBATCH_JOB_NAME="train_model"
SBATCH_PARTITION="gpu"
SBATCH_GPUS=4
SBATCH_NTASKS=1
SBATCH_TIME="2-00:00:00"
SBATCH_MEM=16000
SBATCH_QOS="prio"

# Parse sbatch parameters from command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --job-name) SBATCH_JOB_NAME="$2"; shift ;;
        --partition) SBATCH_PARTITION="$2"; shift ;;
        --gres) SBATCH_GPUS="$2"; shift ;;
        --ntasks) SBATCH_NTASKS="$2"; shift ;;
        --time) SBATCH_TIME="$2"; shift ;;
        --mem) SBATCH_MEM="$2"; shift ;;
        --qos) SBATCH_QOS="$2"; shift ;;
        --config_class) CONFIG_CLASS="$2"; shift ;;
        --resample_round) RESAMPLE_ROUND="$2"; shift ;;
        --use_local_data) USE_LOCAL_DATA="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Construct sbatch script with parameters
sbatch_script="#!/bin/bash
#SBATCH --job-name=${SBATCH_JOB_NAME}       # Job name
#SBATCH --partition=${SBATCH_PARTITION}     # Partition to use
#SBATCH --gres=gpu:${SBATCH_GPUS}           # Request GPUs
#SBATCH --ntasks=${SBATCH_NTASKS}           # Request tasks
#SBATCH --time=${SBATCH_TIME}               # Time limit
#SBATCH --mem=${SBATCH_MEM}                 # Memory request
#SBATCH --qos=${SBATCH_QOS}                 # Quality of Service

# Activate the virtual environment
source \$HOME/venv/bin/activate

# Navigate to the project directory
cd \$HOME/dsitls-project/src/ || exit

# Set environment variables for CUDA and XLA
export CUDA_DIR=\$CUDA_HOME
export XLA_FLAGS=\"--xla_gpu_cuda_data_dir=\$CUDA_DIR\"

# Run the model.py script with the specified parameters
python model.py --config_class \"${CONFIG_CLASS}\" --resample_round \"${RESAMPLE_ROUND}\" --use_local_data \"${USE_LOCAL_DATA}\"
"

# Create a temporary sbatch script
temp_script=$(mktemp)
echo "$sbatch_script" > $temp_script

# Submit the sbatch script
sbatch $temp_script

# Remove the temporary script
rm $temp_script

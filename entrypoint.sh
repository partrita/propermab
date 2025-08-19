#!/bin/bash
set -e

# Activate conda environment
source /opt/conda/etc/profile.d/conda.sh
conda activate propermab

# Determine paths
HMMER_BIN_PATH=$(dirname $(which hmmscan))
CONDA_LIB_PATH=${CONDA_PREFIX}/lib

# Create config.json
cat <<EOF > /propermab/config.json
{
    "hmmer_binary_path" : "${HMMER_BIN_PATH}",
    "nanoshaper_binary_path" : "/opt/apbs/APBS-3.0.0.Linux/bin/NanoShaper",
    "apbs_binary_path" : "/opt/apbs/APBS-3.0.0.Linux/bin/apbs",
    "pdb2pqr_path" : "pdb2pqr",
    "multivalue_binary_path" : "/opt/apbs/APBS-3.0.0.Linux/share/apbs/tools/bin/multivalue",
    "immunebuilder_weights_dir" : null,
    "atom_radii_file" : "/opt/propermab_data/amber.siz",
    "apbs_ld_library_paths" : ["${CONDA_LIB_PATH}", "/opt/apbs/APBS-3.0.0.Linux/lib/"]
}
EOF

# Update propermab's default config to use the new config file
# The example in the README shows doing this from python, so we will do it here.
# The working directory for jupyter will be /propermab
cd /propermab
# The config file will be loaded by the user in their notebook as per the README example.

echo "Starting Jupyter Notebook server..."
# Execute the command provided to the docker run command
exec jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password='' --notebook-dir=/propermab

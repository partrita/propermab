# Use miniconda as base image for better conda support
FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    build-essential \
    cmake \
    git \
    libncurses5 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Create conda environment with Python 3.8
RUN conda create -n propermab python=3.8 -y

# Activate environment and install conda dependencies
RUN /bin/bash -c "source activate propermab && \
    conda install -c bioconda -c conda-forge -c pytorch -c main -c r -c msys2 \
    openmm \
    libstdcxx-ng \
    pdbfixer \
    anarci \
    'scipy>=1.6' \
    'biopython>=1.76,<=1.79' \
    py3dmol \
    'matplotlib>=3.5' \
    'seaborn>=0.11' \
    'numba>=0.50' \
    pdb2pqr \
    pip \
    -y"

# Create separate readline environment for readline 7.0
RUN conda create -n readline_env python=3.8 -y && \
    /bin/bash -c "source activate readline_env && conda install readline=7.0 -y"

# Install APBS 3.0.0 (check if local file exists first)
RUN /bin/bash -c ' \
    if [ -f "apbs.zip" ]; then \
        echo "Using existing apbs.zip file"; \
        unzip -o apbs.zip; \
    else \
        echo "Downloading APBS 3.0.0 from GitHub"; \
        wget https://github.com/Electrostatics/apbs/releases/download/v3.0.0/APBS-3.0.0_Linux.zip -O apbs.zip; \
        unzip -o apbs.zip; \
        rm apbs.zip; \
    fi'

# Install Python dependencies via pip in propermab environment
RUN /bin/bash -c "source activate propermab && \
    pip install \
    'immunebuilder>=0.0.5,<=0.0.8' \
    'freesasa==2.1.0' \
    open3d \
    plyfile \
    'markupsafe==2.0.1' \
    'werkzeug==2.0.3' \
    meshio \
    fair-esm \
    antiberty"

# Install propermab package in development mode
RUN /bin/bash -c "source activate propermab && pip install -e ."

# Setup amber.siz file for NanoShaper
COPY amber.siz /app/APBS-3.0.0.Linux/share/apbs/tools/pdb2pqr/dat/amber.siz

# Create optimized default_config.json for Docker environment
RUN echo '{ \
    "hmmer_binary_path" : "/opt/conda/envs/propermab/bin", \
    "nanoshaper_binary_path" : "/app/APBS-3.0.0.Linux/bin/NanoShaper", \
    "apbs_binary_path" : "/app/APBS-3.0.0.Linux/bin/apbs", \
    "pdb2pqr_path" : "/opt/conda/envs/propermab/bin/pdb2pqr", \
    "multivalue_binary_path" : "/app/APBS-3.0.0.Linux/share/apbs/tools/bin/multivalue", \
    "immunebuilder_weights_dir" : "", \
    "atom_radii_file" : "/app/APBS-3.0.0.Linux/share/apbs/tools/pdb2pqr/dat/amber.siz", \
    "apbs_ld_library_paths" : ["/opt/conda/envs/readline_env/lib/", "/app/APBS-3.0.0.Linux/lib/"] \
}' > /app/default_config.json

# Set up environment variables
ENV PATH="/opt/conda/envs/propermab/bin:$PATH"
ENV CONDA_DEFAULT_ENV=propermab

# Create activation script
RUN echo '#!/bin/bash\nsource activate propermab\nexec "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Set entrypoint to activate conda environment
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command shows help
CMD ["python", "-c", "print('PROPERMAB Docker Container\\nUsage: docker run --rm -v $(pwd):/mnt/host -w /app propermab_image python /mnt/host/scripts/pembrolizumab.py')"]

# Add labels for better maintainability
LABEL maintainer="propermab-team"
LABEL description="Docker image for PROPERMAB - molecular features and properties prediction for monoclonal antibodies"
LABEL version="0.2.0"

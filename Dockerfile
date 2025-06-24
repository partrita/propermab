# Base image
FROM continuumio/miniconda3:latest

# Install unzip utility
USER root
RUN apt-get update && apt-get install -y unzip && rm -rf /var/lib/apt/lists/*
# Sticking with root user for now to avoid user permission issues with /app creation
# USER jovyan # Reverted this change

# Set working directory
WORKDIR /app

# Copy environment and setup files
# If running as root, chown might not be strictly necessary here,
# but good practice if a non-root user is added later.
COPY conda_env.yml .
COPY setup.py .
COPY propermab/ propermab/
COPY default_config.json .
COPY README.md .
# Example if a non-root user 'appuser' was created:
# COPY --chown=appuser:appgroup . .

# Create conda environment
RUN conda env create -f conda_env.yml || (cat /opt/conda/envs/propermab/conda-meta/history && exit 1)

# Activate conda environment and set it for subsequent RUN instructions
SHELL ["conda", "run", "-n", "propermab", "/bin/bash", "-c"]

# Install propermab package and its specific pip dependencies separately
# freesasa is now installed via conda
RUN pip install "immunebuilder>=0.0.5,<=0.0.8" open3d
RUN pip install -e .

# Install APBS
# Note: unzip is now installed at the OS level
RUN wget https://github.com/Electrostatics/apbs/releases/download/v3.0.0/APBS-3.0.0_Linux.zip -O apbs.zip && \
    unzip apbs.zip && \
    rm apbs.zip

# Download amber.siz for NanoShaper
RUN wget https://electrostaticszone.eu/files/pdb2xyzr.zip -O pdb2xyzr.zip && \
    unzip pdb2xyzr.zip pdb2xyzr/amber.siz && \
    mv pdb2xyzr/amber.siz /app/APBS-3.0.0.Linux/share/apbs/tools/pdb2pqr/dat/ && \
    rm pdb2xyzr.zip && \
    rm -rf pdb2xyzr

# Set environment variables
# Order is important for LD_LIBRARY_PATH to avoid issues with undefined variables during build
ENV APBS_PATH=/app/APBS-3.0.0.Linux
ENV PATH=${APBS_PATH}/bin:${PATH}
ENV LD_LIBRARY_PATH_APBS_SPECIFIC=${APBS_PATH}/lib

# Install readline 7.0 in a separate environment for APBS dependency
# Ensure base environment is activated before deactivating for readline install
RUN source /opt/conda/etc/profile.d/conda.sh && conda activate base && \
    conda deactivate && \
    conda create -y --name readline_env python=3.8 && \
    conda run -n readline_env conda install -y readline=7.0

ENV LD_LIBRARY_PATH_READLINE=/opt/conda/envs/readline_env/lib

# Combine LD_LIBRARY_PATH components
# Ensure all components are defined before this line
# If LD_LIBRARY_PATH was previously set in the base image or an earlier ENV, it will be prepended.
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH_READLINE}:${LD_LIBRARY_PATH_APBS_SPECIFIC}${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

# Expose port if necessary (currently no service is exposed)
# EXPOSE 8888

# Default command (can be overridden)
CMD ["/bin/bash"]

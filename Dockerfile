# Use a Miniconda base image
FROM continuumio/miniconda3:latest

# Set non-interactive frontend for package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the entire repository to /propermab
COPY . /propermab
WORKDIR /propermab

# Create the conda environment
RUN conda env create -f conda_env.yml

# Activate the conda environment and install the propermab package
SHELL ["conda", "run", "-n", "propermab", "/bin/bash", "-c"]
RUN pip install -e .

# Download and install external dependencies
RUN mkdir -p /opt/apbs && \
    wget https://github.com/Electrostatics/apbs/releases/download/v3.0.0/APBS-3.0.0_Linux.zip -O /opt/apbs/apbs.zip && \
    unzip /opt/apbs/apbs.zip -d /opt/apbs && \
    rm /opt/apbs/apbs.zip

RUN mkdir -p /opt/propermab_data && \
    wget https://electrostaticszone.eu/downloads/scripts-and-utilities/15-pdb2xyzr/pdb2xyzr.zip -O /opt/propermab_data/pdb2xyzr.zip && \
    unzip /opt/propermab_data/pdb2xyzr.zip -d /opt/propermab_data && \
    mv /opt/propermab_data/pdb2xyzr/amber.siz /opt/propermab_data/amber.siz && \
    rm -rf /opt/propermab_data/pdb2xyzr.zip /opt/propermab_data/pdb2xyzr

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Expose the Jupyter Notebook port
EXPOSE 8888

# Set the entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

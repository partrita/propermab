# propermab

`propermab` is a Python package for calculating and predicting molecular features and properties of monoclonal antibodies (mAbs), as described in the following paper:

Li, B., Luo, S., Wang, W., Xu, J., Liu, D., Shameem, M., Mattila, J., Franklin, M.C., Hawkins, P.G., and Atwal, G.S. (2025). PROPERMAB: an integrative framework for in silico prediction of antibody developability using machine learning. mAbs 17, 2474521. 10.1080/19420862.2025.2474521.


## Installation (Linux)

First set up a conda environment by running the following commands on the terminal
```bash
git clone https://github.com/regeneron-mpds/propermab.git
conda env create -f propermab/conda_env.yml
conda activate propermab
```
Now install the `propermab` package with
```bash
pip install -e propermab/
```

## Installation with Docker (Linux)

Alternatively, you can use Docker to simplify the installation process.

1.  **Build the Docker image:**
    ```bash
    docker build -t propermab_image .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -it --rm propermab_image
    ```
    This will start a bash session within the container where `propermab` and all its dependencies are installed. The `default_config.json` file inside the container is already configured for the Docker environment.

    If you need to access files from your host machine (e.g., PDB files, sequence files, or save output files), you can mount a volume:
    ```bash
    docker run -it --rm -v /path/on/host:/data_on_host propermab_image
    ```
    Replace `/path/on/host` with the actual path to the directory on your host machine. Inside the container, this directory will be accessible at `/data_on_host`.

    You can then run `propermab` scripts or use its Python API within this container. For example, to run an example script that uses a PDB file from your mounted volume:
    ```python
    # Inside the Docker container's Python interpreter
    from propermab import defaults
    from propermab.features import feature_utils

    # The default_config.json is already set up in the Docker image
    # No need to call defaults.system_config.update_from_json() unless you have a custom config

    mol_feature = feature_utils.calculate_features_from_pdb('/data_on_host/your_pdb_file.pdb')
    print(mol_feature)
    ```

### APBS
The APBS tool v3.0.0 is used by `propermab` to calculate electrostatic potentials. Download the tool and unzip it to a directory of your choice.
```bash
wget https://github.com/Electrostatics/apbs/releases/download/v3.0.0/APBS-3.0.0_Linux.zip -O apbs.zip
unzip apbs.zip
```
Record the path to this directory as it will be used in the next step. 

### Configuration
Edit the `default_config.json` file to specify the path for each of the entries in the file
```python
{
    "hmmer_binary_path" : "",
    "nanoshaper_binary_path" : "/ABPS_PATH/APBS-3.0.0.Linux/bin/NanoShaper",
    "apbs_binary_path" : "/ABPS_PATH/APBS-3.0.0.Linux/bin/apbs",
    "pdb2pqr_path" : "pdb2pqr",
    "multivalue_binary_path" : "/ABPS_PATH/APBS-3.0.0.Linux/share/apbs/tools/bin/multivalue",
    "atom_radii_file" : "",
    "apbs_ld_library_paths" : ["LIB_PATH", "/ABPS_PATH/APBS-3.0.0.Linux/lib/"]
}
```

You can find the value of `hmmer_binary_path` by issuing the following command on your terminal
```bash
dirname $(which hmmscan)
```

The value of `atom_radii_file` should point to a file named `amber.siz`. This file is needed to run NanoShaper and can be obtained from the pdb2xyzr.zip file available at (https://electrostaticszone.eu/downloads/scripts-and-utilities.html).

To get the value for LIB_PATH, first create a separate conda environment to install the `readline 7.0` package.
```bash
conda deactivate
conda create --name readline python=3.8
conda activate readline
conda install readline=7.0
```
This may sound a bit involved, but it is necessary as the APBS tool specifically requires the readline.so.7 library file. `readline 7.0` can't be installed from within the propermab conda environment because that would result in too many conflicts. With that being said, once the readline package is installed, the value for LIB_PATH can be found by
```bash
echo ${CONDA_PREFIX}/lib/
```
Finally, be sure to replace APBS_PATH with the actual path to the directory where the APBS tool was unzipped in the previous step.

Now deactivate the readline environment and reactivate the propermab environment.

## Example
### Using `propermab` Python API
You can calculate the molecular features directly from a structure PDB file. Note that this assumes that the residues in PDB file are IMGT numbered and that the heavy chain is named H and the light chain is named L.
```python
from propermab import defaults
from propermab.features import feature_utils

defaults.system_config.update_from_json('./default_config.json')

mol_feature = feature_utils.calculate_features_from_pdb('./tests/pembrolizumab_ib.pdb')
```
Or you can provide a pair of heavy and light chain sequences, `propermab` then calls the `ABodyBuilder2` model to predict the structure, which will be used as the input for feature calculation.
```python
from propermab import defaults
from propermab.features import feature_utils

defaults.system_config.update_from_json('./default_config.json')

heavy_seq = 'HEAVY_SEQ'
light_seq = 'LIGHT_SEQ'
mol_features = feature_utils.get_all_mol_features(heavy_seq, light_seq, num_runs=1)
```
Be sure to replace HEAVY_SEQ and LIGHT_SEQ with the actual sequences. Different runs of `ABodyBuilder2` can result in some difference in sidechain conformations due to the relaxation step in `ABodyBuilder2`. This in turn can affect values of some of the molecular features `propermab` calculates. If the average feature value across multiple runs is desired, one can increase `num_runs`. `get_all_mol_features()` returns a Python dictionary in which the keys are feature names and the values are the corresponding lists of feature values from multiple runs.

The following code demonstrates how to calculate the set of sequence-based features, assuming that the sequences are for the Fv domains, the isotype is IgG1, and the type of the light chain is lambda.
```python
from propermab import defaults
from propermab.features import feature_utils

defaults.system_config.update_from_json('./default_config.json')

heavy_seq = 'HEAVY_SEQ'
light_seq = 'LIGHT_SEQ'
seq_features = feature_utils.get_all_seq_features(
    heavy_seq, light_seq, is_fv=True, isotype='igg1', lc_type='lambda'
)
```

## Third-party software
`propermab` requires separate installation of third party software which may carry their own license requirements, and should be reviewed by the user prior to installation and use

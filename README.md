[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/babakkhavari/Clustering)

## What this module does

This repository contains the source code to extract geospatial data required for the least-cost electrification analysis using the OnSSET tool for every settlement in the country.

## Installation

The extraction module (as well as all supporting scripts in this repo) have been developed in Python 3. We recommend installing [Anaconda's free distribution](https://www.anaconda.com/distribution/) as suited for your operating system. In order to be able to run the clustering tool you have to install all necessary packages contained in "moz_onsset_env.yml". To do this, simply open Anaconda prompt and browse to the code directory on your computer and run:

```
conda env create --name moz_onsset_env --file moz_onsset_env.yml
```

## How to run

1. Download input data to data/inputs (see paths in **Input data** section below)
2. Install the required packages (see installation instructions using Anaconda above)
3. Activate the environment in Anaconda prompt (*conda activate moz_onsset_env*)
4. Launch Jupyter Notebook (*jupyter notebook* in Anaconda Prompt)
5. Open *notebooks/clustering.ipynb* and follow the instructions inside
6. Outputs will be written to data/outputs

## Input data

| Dataset | Target location | Description | SDI Location | Alternative location |
|---------|-----------------|-------------|--------------|----|
| Population raster | data/iputs/pop | 100 m population counts in raster format (e.g. .tif) | /datasets/rasterfile/13 | https://wopr.worldpop.org/?MOZ/Population/ (*Gridded population estimates (~100m) for Mozambique* version 2.0)|
| Administrative boundaries | data/inputs/admin_boundaries | Administrative boundaries of Mozambique in polygon format | /datasets/vectorfile/46 | - | 

## Output data

Output data is a vector file of settlement polygons including population estimates, saved as a geoparquet (*clusters.parquet*) in data/outputs:

| Column | Description | Units |
| - | - | - |
| id | Unique id of each settlement | - |
| Country | Name of the country | - |
| Area | Area of each settlement | Sq. km |
| Population | Estimated population in each settlement | People |
| DEGURBA | DEGree of URBAnization | More info [here](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Applying_the_degree_of_urbanisation_manual_-_Extensions_to_level_1_of_the_classification#7.1.4_Classifying_small_spatial_units) |

## License

This module is made available under the **GPL-3.0** license.
See the LICENSE file in this repository for the full text.

## Contact

Questions/maintainer:
- Inocencio Gujamo - MIREME-UIPCE (inocencio.gujamo@gmail.com)
- Imaculada Dos Santos - MIREME-UIPCE (imaculadamz@gmail.com)

Developed by: 
- Babak Khavari - SEforALL (babak.khavari@seforall.org)
- Alexandros Korkovelos - SEforALL (alexandros.korkovelos@seforall.org)
- Andreas Sahlberg - SEforALL (andreas.sahlberg@seforall.org)



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
5. Open the *notebooks* folder
6. Chooese either the *csv_file_preparation_stepBystep_code.ipynb* (recommended for first-time users) or *csv_file_preparation_bulk_code.ipynb* and follow the instructions inside
7. Outputs will be written to data/outputs

## Input data

| Dataset | Target location | Description | SDI Location | Alternative location |
|---------|-----------------|-------------|--------------|----|
| Administrative boundaries | data/inputs/AdminBoundaries | Administrative boundaries of Mozambique in polygon format - including province level | /datasets/vectorfile/46 | - |
| Settlement clusters | data/inputs/Clusters | Population settlement clusters |  | - |
| Distribution transformers | data/inputs/DistributionTransformers | Existing distribution transformers (MV/LV) |  | - |
| Existing HV lines | data/inputs/HV_Existing | Existing HV lines |  | - |
| Planned HV lines | data/inputs/HV_Planned | Planned HV lines |  |  |
| Hydro potential | data/inputs/HydroPotential | Potential sites for small- and mini hydro sites for run-of-river mini-grids |  | https://energydata.info/dataset/small-and-mini-hydropower-potential-in-sub-saharan-africa |
| Existing mini-grids | data/inputs/MiniGrids | Existing mini-grid locations |  | - |
| Existing MV lines | data/inputs/MV_Existing | Existing MV lines |  | - |
| Planned MV lines | data/inputs/Planned | Planned MV lines (already committed) |  | - |
| Night-time lights | data/inputs/NightTimeLights | Night-time lights |  | https://eogdata.mines.edu/products/vnl/ (*median-masked version 2.2*) |
| Roads | data/inputs/Roads | Main road network "trans estradas" |  | - |
| Solar GHI | data/inputs/SolarGHI | Solar resource - Annual Global Horizontal Irradiation |  | https://globalsolaratlas.info/download/mozambique (*Gis data - LTAym_YearlyMonthlyTotals (GeoTIFF)*) |
| Substations | data/inputs/Substations | Existing power substations |  | - |
| Travel time to major cities | data/inputs/TravelTime | Travel time to nearest city with >50,000 population |  | https://data.malariaatlas.org/maps (*Global Travel Time to Cities*) |
| Wind speed | WindVelocity | Annual average wind speed (m/s) |  | https://globalwindatlas.info/api/gis/country/MOZ/wind-speed/50 (*Mozambique > WIND_SPEED > 50*) |

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



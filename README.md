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
8. Check that data in the output csv file match with expected values as described in **Output data** below

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

Output data is a file with extracted GIS data for every settlement, saved as a csv (*OnSSET_InputFile.csv*) in data/outputs:

| Column | Type | Unit | Description |
|---------|-----------------|-------------|--------------|
| Country |	String |	-	| Name of the country |
| Admin_1 |	String |	- |	Admin level 1 (state/region/province) name |
| X_deg |	Float |	degrees |	Longitude (a value between -180 and 180) |
| Y_deg |	Float |	degrees |	Latitude (a value between -180 and 180) |
| GridCellArea |	Float |	sq. km	| Area of population settlement (most settlements <1, can go as high as 1,000-2,000 for the largest settlements) |
| Id |	Integer |	indicator |	ID given to each cluster |
| Pop |	Float |	people |	Population in each cluster for the start year as given by the GIS dataset |
| NightLights |	Integer |	nW cm−2 sr−1 |	Values of light intensity (usually in the range of 0-200) |
| GHI |	Float |	kWh/km^2 |	Solar irradiation (usually in the range of 1,500 – 2,500) |
| Windwel |	Float |	m/s |	Average annual wind speed (usually in the range of 0-10) |
| Travelhours |	Float |	hours |	Time in hours to travel to nearest town of more than 50,000 people (usually in the range of 0-50) |
| SubstationDist |	Float |	km |	Distance to nearest substation (usually in the range of 0-300) |
| RoadDist |	Float |	km |	Distance to nearest road (usually in the range of 0-100) |
| CurrentMVLineDist |	Float |	km |	Distance to nearest existing MV line (usually in the range of 0-300) |
| PlannedMVLineDist |	Float |	km |	Distance to nearest existing or planned MV line (usually in the range of 0-300) |
| CurrentHVLineDist |	Float |	km |	Distance to nearest current HV line (usually in the range of 0-300) |
| PlannedHVLineDist |	Float |	km |	Distance to nearest existing or planned HV line (usually in the range of 0-300) |
| HydropowerFID |	Integer |	indicator |	ID of nearest potential hydropower site |
| Hydropower |	Float |	kW |	Small scale hydropower potential of nearest site (usually in the range of 0-10,000) |
| HydropowerDist |	Float |	km |	Distance to nearest potential hydropower site (usually in the range of 0-300) |
| TransformerDist |	Float |	km |	Distance to nearest service transformer (MV/LV) (usually in the range of 0-300) |
| IsUrban |	Integer |	0 for rural 2 for urban |	Urban/rural split gets assigned in the calibration algorithm (expected to be 0 after extraction unless any information was provided in the clusters already) |
| ResidentialDemandTierCustom |	Float |	kWh/household/year |	Indicative residential electricity demand target (expected to be 0 or in the range of 0-3000) |
| PerHouseholdDemand |	Float |	kWh/household/year |	Indicative residential electricity demand target (expected to be 0 after extraction unless any information was provided in the clusters already) |
| HealthDemand |	Float |	kWh/year |	Indicative electricity demand for health facilities (expected to be 0 after extraction unless any information was provided in the clusters already) |
| EducationDemand |	Float |	kWh/year |	Indicative electricity demand for educational facilities (expected to be 0 after extraction unless any information was provided in the clusters already) |
| AgriDemand |	Float |	kWh/year |	Indicative electricity demand for agricultural processes (expected to be 0 after extraction unless any information was provided in the clusters already) |
| CommercialDemand |	Float |	kWh/year |	Indicative electricity demand target for commercial activity (expected to be 0 after extraction unless any information was provided in the clusters already) |
| ElecPop |	Float |	people |	Placeholder, will be used for information about estimated population that already has access to electricity in the start of the analysis. (expected to be 0 after extraction unless any information was provided in the clusters already) |

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



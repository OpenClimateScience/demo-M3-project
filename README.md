Demonstration: Reproducible Python Project for Water Resources
==============================================================

**Note:** This notebook complements the third module in our [open climate-science curriculum](https://openclimatescience.github.io/curriculum), ["M3: Open Science for Water Resources,"](https://github.com/OpenClimateScience/M3-Open-Science-for-Water-Resources) and serves as a demonstration of reproducible research code.


Overview
--------------

This repository computes a basin-scale water budget for the Yellowstone River basin, according to the formula:

$$
P = E + R + \Delta S
$$

Where $P$ is precipitation, $E$ is evapotranspiration (ET), $R$ is runoff, and $\Delta S$ is change in storage. On monthly to annual time scales, this is a good approximate for a closed, gauged basin.


Contents
--------------

- Step 1: Compute monthly precipitation for the basin, based on GPM IMERG-Final data: `h2o/scripts/step01_IMERG-Final_monthly_precipitation.py`
- Step 2: Compute monthly ET for the basin, based on MODIS MOD16 data: `h2o/scripts/step02_MODIS_MOD16_monthly_ET.py`
- Step 3: Get the runoff data and compute change in storage: `h2o/scripts/step03_HYSETS_monthly_runoff_and_change_in_storage.py`


Setup and Installation
----------------------

The Python software dependencies can be installed using `pip`:

```sh
pip install -r REQUIREMENTS
```


Disclaimer
--------------

This demonstration project is a minimal approach to documenting a reproducible scientific workflow. There are several improvements that could be made, but we wanted to demonstrate the bare minimum requirements because many researchers don't have the time, knowledge, or stamina to implement a more sophisticated reproducible workflow. [Other modules in our open-science curriculum](https://openclimatescience.github.io/curriculum) do demonstrate more sophisticated techniques, so do check Modules 4 and 5!

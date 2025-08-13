'''
Computes monthly runoff from the HYSETS database, then computes the change in
storage based on monthly precipitation and ET (computed earlier).

Change in storage is computed as:

    S = P - (E + R)

Where S is the change in storage, P is precipitation, E is evapotranspiration,
and R is runoff.
'''

import glob
import earthaccess
import numpy as np
import xarray as xr
import rioxarray
import geopandas
import pathlib
import py4eos
from matplotlib import pyplot

CWD = pathlib.Path(__file__).parent.resolve() # Current working directory
HYSETS_FILE = CWD.parent.joinpath('data/HYSETS-2023_watershed_YellowstoneRiver.nc')
PRECIP_FILE = CWD.parent.joinpath('processed/IMERG-Final_precip_monthly_2014-2023.nc')
ET_FILE = CWD.parent.joinpath('processed/MOD16_ET_monthly_2014-2023.nc')
BASIN_FILE = CWD.parent.joinpath('data/shp/YellowstoneRiver_drainage_WSG84.shp')

def main(download = False):
    basin = geopandas.read_file(BASIN_FILE)
    # Project our basin data to the new CRS
    basin_albers = basin.to_crs(epsg = 5070)
    # Get the area of the basin
    basin_area = basin_albers.area.values

    # Open the HYSETS dataset
    ds = xr.open_dataset(HYSETS_FILE)

    # As we're currently just looking at a 10-year period from 2014 through
    #   2023, let's slice the data to that time range
    ds_10years = ds.sel(time = slice('2014-01-01', '2023-12-31'))

    # Compute total daily discharge based on the mean rate
    ds_10years['discharge_total'] = ds_10years.discharge * 60 * 60 * 24

    # Get the [m year-1] that this basin drained through Yellowstone River,
    #  then convert from [m year-1] to [mm year-1]
    runoff_meters_per_yr = ds_10years['discharge_total']\
        .resample(time = 'YS').sum() / basin_area
    runoff_mm_per_yr = runoff_meters_per_yr * 1000

    runoff_series = runoff_mm_per_yr.values

    # Now, get the precip time series
    ds_precip = xr.open_dataset(PRECIP_FILE)
    precip_series = ds_precip.precip_monthly\
        .mean(['lon','lat']).groupby('time.year').sum().values

    ds_et = xr.open_dataset(ET_FILE)
    et_series = ds_et.mean(['x', 'y']).ET.values

    # Plot all components together
    years = np.arange(2014, 2024)
    pyplot.plot(years, precip_series, 'b', label = 'Precipitation')
    pyplot.plot(years, et_series, 'g', label = 'ET')
    pyplot.plot(years, runoff_series, 'r', label = 'Runoff')
    pyplot.ylabel('Water Flux (mm per year)')
    pyplot.legend()
    pyplot.show()

    # Compute and plot change in storage
    delta_storage = precip_series - (et_series + runoff_mm_per_yr.values)
    pyplot.bar(years, height = delta_storage)
    pyplot.ylabel('Change in Storage (mm per year)')
    pyplot.show()


if __name__ == '__main__':
    main()

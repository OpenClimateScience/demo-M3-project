'''
Computes monthly evapotranspiration (ET) for a basin (represented in a
Shapefile), based on MOD16 ET data.
'''

import glob
import earthaccess
import numpy as np
import xarray as xr
import rioxarray
import geopandas
import pathlib
import py4eos

CWD = pathlib.Path(__file__).parent.resolve() # Current working directory
OUTPUT_FILE = CWD.parent.joinpath('processed/MOD16_ET_monthly_2014-2023.nc')
BASIN_FILE = CWD.parent.joinpath('data/shp/YellowstoneRiver_drainage_WSG84.shp')

def main(download = False):
    auth = earthaccess.login()
    basin = geopandas.read_file(BASIN_FILE)
    bbox = basin.bounds.to_numpy().ravel()

    # Project our basin data to the new CRS
    basin_albers = basin.to_crs(epsg = 5070)
    basin_albers.geometry[0]

    if download:
        results = earthaccess.search_data(
            short_name = 'MOD16A3GF',
            temporal = ('2014-01-01', '2023-12-31'),
            bounding_box = tuple(bbox))
        # Filter the results to just the MODIS tile we're interested in,
        #   based on its horizontal (h) and vertical (v) coordinates.
        results_clean = list(filter(lambda granule: 'h10v04' in granule['meta']['native-id'], results))
        earthaccess.download(results, str(CWD.parent.joinpath('data/MOD16A3')))
    # Get a list of the *.hdf files we downloaded
    file_list = glob.glob(str(CWD.parent.joinpath('data/MOD16A3/*.hdf')))
    file_list.sort()

    gtiff_file_list = []

    # Project each image to the new CRS, in order to clip to our basin
    for filename in file_list:
        # Extract the year from the filename
        year = filename.split('.')[1].replace('A', '').replace('001', '')
        # Read in the MODIS MOD16 data
        hdf = py4eos.read_hdf4eos(filename)
        # Create a rasterio Dataset for this raster; also write out a GeoTIFF file
        output_dir = str(CWD.parent.joinpath('processed'))
        output_filename = f'{output_dir}/MOD16A3GF_{year}_ET_500m.tiff'
        ds_et = hdf.to_rasterio(
            'ET_500m', filename = output_filename, scale_and_offset = True)
        ds_et.close()
        # Save the output GeoTIFF filename
        gtiff_file_list.append(output_filename)

    gtiff_file_list.sort()

    # Clip to our basin, compute basin-wide ET
    et_data = []
    for i, filename in enumerate(gtiff_file_list):
        year = np.arange(2014, 2024)[i]
        ds_et = rioxarray.open_rasterio(filename)
        # Project the MOD16 data to match the CRS of our basin
        ds_et_albers = ds_et.rio.reproject(basin_albers.crs)
        # Clip the MOD16 data to the boundary of our basin
        ds_et_basin = ds_et_albers.rio.clip(basin_albers.geometry.values)
        ds_et_basin = ds_et_basin.rename({'band': 'time'})\
            .assign_coords(time = ('time', [year]))
        et_data.append(ds_et_basin)

    xr.Dataset({'ET': xr.concat(et_data, dim = 'time')}).to_netcdf(OUTPUT_FILE)


if __name__ == '__main__':
    main()

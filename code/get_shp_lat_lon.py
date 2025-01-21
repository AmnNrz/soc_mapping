# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: tillmap
#     language: python
#     name: python3
# ---

# +
import geopandas as gpd
import pandas as pd

path_to_data = ('/Users/aminnorouzi/Library/CloudStorage/'
                'OneDrive-WashingtonStateUniversity(email.wsu.edu)/Ph.D/'
                'Projects/Tillage_Mapping/Data/')
# Load the shapefile
shapefile_path = path_to_data + 'GIS_Data/final_shpfiles/'
shp_2022_path = shapefile_path + "final_shp_2122_.shp"
shp_2023_path = shapefile_path + "final_shp_2223_.shp"

output_csv_path = path_to_data + 'gridmet_lat_lon/'

gdf_2022 = gpd.read_file(shp_2022_path)
gdf_2023 = gpd.read_file(shp_2023_path)


# +
gdf_2022['Year'] = 2022
gdf_2023['Year'] = 2023

cols = ['pointID', 'Year']
gdf_22_23 = pd.concat([gdf_2022[cols], gdf_2023[cols]])
gdf_22_23.to_csv(
    "/Users/aminnorouzi/Library/CloudStorage/OneDrive-WashingtonStateUniversity(email.wsu.edu)/Ph.D/Projects/soc_mapping/data/year_pointID.csv"
, index=False)


# +
def add_lat_lon(gdf):

    # Calculate centroids of the polygons
    gdf["centroid"] = gdf.geometry.centroid

    # Extract latitude and longitude from the centroids
    gdf["latitude"] = gdf.centroid.y
    gdf["longitude"] = gdf.centroid.x

    # Drop the centroid column if not needed
    gdf = gdf.drop(columns=["centroid"])
    return gdf


# Add lat and lon to the shapfiles
gdf_2022_shp = add_lat_lon(gdf_2022)
gdf_2023_shp = add_lat_lon(gdf_2023)

# Export to CSV

gdf_2022_shp.to_csv(output_csv_path + "shp_2022_lat_lon.csv", index=False)
gdf_2023_shp.to_csv(output_csv_path + "shp_2023_lat_lon.csv", index=False)
# gdf_2022_shp.to_file(output_csv_path + "shp_2022_lat_lon.shp", index=False)
# gdf_2023_shp.to_file(output_csv_path + "shp_2023_lat_lon.shp", index=False)

# Export to shapefiles (including all supporting files)
gdf_2022_shp.to_file(output_csv_path + "shp_2022_lat_lon", driver="ESRI Shapefile")
gdf_2023_shp.to_file(output_csv_path + "shp_2023_lat_lon", driver="ESRI Shapefile")

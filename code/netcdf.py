# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import netCDF4 as nc
from netCDF4 import Dataset
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import openpyxl
import os

# +
#####################################################################
# Reading a single ndtcdf like pdsi.nc which consists all the years #
#####################################################################


# Read the Excel file
file_path = 'location/locations.xlsx'  
df = pd.read_excel(file_path)


# Iterate over each row and print the values
for index, row in df.iterrows():
    location = row['location']
    latitude = row['Latitude']
    longitude = row['Longitude']

    # Open the NetCDF file
    dataset = nc.Dataset(f'./nc_files/rmax.nc', 'r')

    print(dataset.variables.keys())
    print("\nVariables and their dimensions:")

    print("Description of each variable:")
    for var in dataset.variables:
        # Fetch the variable object
        variable = dataset.variables[var]
        # Extract description attributes, defaulting to 'N/A' if not present
        long_name = variable.long_name if hasattr(variable, 'long_name') else 'N/A'
        units = variable.units if hasattr(variable, 'units') else 'N/A'
        print(f"{var}:")
        print(f"  Long Name: {long_name}")
        print(f"  Units: {units}\n")
    # Don't forget to close the dataset
    dataset.close()

    dataset = nc.Dataset(f'./nc_files/spei14d.nc', 'r')
    # Retrieve the latitude and longitude data
    lat = dataset.variables['lat'][:]
    lon = dataset.variables['lon'][:]

    # Your location's latitude and longitude
    location_lat =  latitude # Replace with the specific latitude
    location_lon = longitude  # Replace with the specific longitude

    # Find the nearest index for the specified location
    lat_idx = np.abs(lat - location_lat).argmin()
    lon_idx = np.abs(lon - location_lon).argmin()

    # Retrieve climate variable for all times for the specified location
    climate_variable = dataset.variables['spei'][:, lat_idx, lon_idx]  # Assuming time is the first dimension

    # Convert to a DataFrame
    df = pd.DataFrame({
        'data': climate_variable
    })


    #Temperature in gridMET is in Kelvin. Convert it to celsius. If you don't have temperature netcdf file, then comment the line below
    #df = df - 273.15


    lat_num = lat[lat_idx]
    lon_num = lon[lon_idx]
    print(lat_num,lon_num)
    df.columns = ['data']

    # Assuming the reference date is January 1, 1900
    reference_date = datetime(1900, 1, 1)

    days = dataset.variables['day'][:]
    # Convert days array to pandas Series
    days_series = pd.Series(days)

    # Convert to Gregorian dates using vectorized operations
    gregorian_dates_pd = reference_date + pd.to_timedelta(days_series, unit='D')

    days = gregorian_dates_pd

    df['dates'] = days
    df_new = df[['dates','data']]
    df_new.columns = ['date', 'rmax']
    df_new.to_excel(f'{location}.xlsx',index = False)



dir1 = './'
dir2 = './'

excel_files = os.listdir(dir1)

for file_name in excel_files:
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        file_path = os.path.join(dir1, file_name)
        df = pd.read_excel(file_path)
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df_filtered = df[(df['date'].dt.year < 1980) | (df['date'].dt.year > 2003)]
        df_filtered = df_filtered[df_filtered['date'].dt.year.between(2004, 2020)]
        output_file_path = os.path.join(dir2, file_name)
        df_filtered.to_excel(output_file_path, index=False)
        print(f"Filtered data saved to: {output_file_path}")


# +
##########################################################################################
# Read netcdf file and Save file for each individual year in the same place as code path #
##########################################################################################

# Read the Excel file
file_path = 'location/locations.xlsx'  
df = pd.read_excel(file_path)

# Iterate over each row and print the values
for index, row in df.iterrows():
    location = row['location']
    latitude = row['Latitude']
    longitude = row['Longitude']

    years = list(range(2004, 2021))
    #years = [2020]
    for year in years:
        # Open the NetCDF file
        dataset = nc.Dataset(f'./nc_files/vpd_{year}.nc', 'r')

        print(dataset.variables.keys())
        print("\nVariables and their dimensions:")

        print("Description of each variable:")
        for var in dataset.variables:
            # Fetch the variable object
            variable = dataset.variables[var]
            # Extract description attributes, defaulting to 'N/A' if not present
            long_name = variable.long_name if hasattr(variable, 'long_name') else 'N/A'
            units = variable.units if hasattr(variable, 'units') else 'N/A'
            print(f"{var}:")
            print(f"  Long Name: {long_name}")
            print(f"  Units: {units}\n")

        # Don't forget to close the dataset
        dataset.close()

        dataset = nc.Dataset(f'./nc_files/vpd_{year}.nc', 'r')
        # Retrieve the latitude and longitude data
        lat = dataset.variables['lat'][:]
        lon = dataset.variables['lon'][:]

        # Your location's latitude and longitude
        location_lat =  latitude # Replace with the specific latitude
        location_lon = longitude  # Replace with the specific longitude

        # Find the nearest index for the specified location
        lat_idx = np.abs(lat - location_lat).argmin()
        lon_idx = np.abs(lon - location_lon).argmin()

        # Retrieve climate variable for all times for the specified location
        climate_variable = dataset.variables['mean_vapor_pressure_deficit'][:, lat_idx, lon_idx]  # Assuming time is the first dimension

        # Convert to a DataFrame
        df = pd.DataFrame({
            'data': climate_variable
        })


        #Temperature in gridMET is in Kelvin. Convert it to celsius. If you don't have temperature netcdf file, then comment the line below
        #df = df - 273.15


        lat_num = lat[lat_idx]
        lon_num = lon[lon_idx]
        print(lat_num,lon_num)
        df.columns = ['data']

        # Assuming the reference date is January 1, 1900
        reference_date = datetime(1900, 1, 1)

        days = dataset.variables['day'][:]
        # Convert days array to pandas Series
        days_series = pd.Series(days)

        # Convert to Gregorian dates using vectorized operations
        gregorian_dates_pd = reference_date + pd.to_timedelta(days_series, unit='D')

        days = gregorian_dates_pd

        df['dates'] = days
        df_new = df[['dates','data']]
        df_new.columns = ['date', 'vpd']
        df_new.to_excel(f'{location}{year}.xlsx',index = False)
        
# -

df_new

# +
######################################################################################
#Merge all years for each location and save them to variable named folder            #
######################################################################################


# Read the Excel file containing the list of locations
file_path = 'location/locations.xlsx'
df = pd.read_excel(file_path)
locations = df['location']

# Directory where the final merged files will be saved
output_dir = './vpd'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Loop through each location
for loc in locations:
    # Clean up location name if necessary
    loc_clean = loc.strip()

    # File paths for the four Excel files
    files = [f'{loc_clean}{year}.xlsx' for year in range(2004, 2021)]

    # Initialize an empty list to store the DataFrames
    dataframes = []

    # Loop through the file paths and read the files into DataFrames
    for file in files:
        if os.path.exists(file):
            df_temp = pd.read_excel(file)
            dataframes.append(df_temp)
            print(f"File {file} read successfully.")
        else:
            print(f"File {file} not found, skipping.")

    # If we have any DataFrames, merge them
    if dataframes:
        merged_df = pd.concat(dataframes, axis=0)
        merged_df.reset_index(drop=True, inplace=True)

        # Write the merged DataFrame to a new Excel file
        output_file = os.path.join(output_dir, f'{loc_clean}.xlsx')
        merged_df.to_excel(output_file, index=False)
        print(f"Files merged successfully into {output_file}")
    else:
        print(f"No valid files found for location {loc_clean}, skipping merge.")


# +
###################################################################################################
# I deleted the dates from old file from 1979 to 2003. Save them in old1 file.                    #
#  Just remember that I manaully delete old files and replace them with  old1 files manaully.     #
# This should be done just once.                                                                  #
###################################################################################################

import os
import pandas as pd
dir1 = './old'
dir2 = './old1'
excel_files = os.listdir(dir1)
for file_name in excel_files:
    file_path = os.path.join(dir1, file_name)
    df = pd.read_excel(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df_filtered = df[~df['date'].dt.year.between(1979, 2004)]
    output_file_path = os.path.join(dir2, file_name)
    df_filtered.to_excel(output_file_path, index=False)

# +
####################################################################
# Concatenate dataframes from old and new variables and save them  #
#                  in 'new' document.                              #
####################################################################



import os
import pandas as pd

# Define the directories containing the Excel files

dir1 = './old'
dir2 = './vpd'
output_dir = './new'  # Directory to save the updated files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List of Excel file names (assuming they have the same names in each document)
excel_files = os.listdir(dir1)

for file_name in excel_files:
    # Paths to the corresponding files in each directory
    file1_path = os.path.join(dir1, file_name)
    file2_path = os.path.join(dir2, file_name)
    
    # Check if file exists in both directories
    if not os.path.exists(file2_path):
        print(f"File {file_name} does not exist in {dir2}. Skipping...")
        continue
    
    # Read the Excel files
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)
    
    # Find columns that are common between df1 and df2
    common_columns = df1.columns.intersection(df2.columns)

    # Drop the common columns from df2
    df2_dropped = df2.drop(columns=common_columns)

    # Step 2: Concatenate df1 and df2 (horizontally in this case)
    result = pd.concat([df1, df2_dropped], axis=1)
    
    # Save the updated DataFrame to a new Excel file in the output directory
    output_file_path = os.path.join(output_dir, file_name)
    result.to_excel(output_file_path, index = False)
    print(f"Updated file saved to {output_file_path}")

print("All files have been updated and saved.")

# +
import os
import pandas as pd


#############################################################
#       This part is for merging the columns                #
#       of all the new data extracted from netcdfs          #
#############################################################

# Define the directories containing the Excel files
dir1 = './pr/'
dir2 = './tmin/'
dir3 = './tmax/'
output_dir = './merge_updates/'  # Directory to save the updated files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List of Excel file names (assuming they have the same names in each document)
excel_files = os.listdir(dir1)

for file_name in excel_files:
    # Paths to the corresponding files in each directory
    file1_path = os.path.join(dir1, file_name)
    file2_path = os.path.join(dir2, file_name)
    file3_path = os.path.join(dir3, file_name)
    
    # Read the Excel files
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)
    df3 = pd.read_excel(file3_path)
    
    # Extract the second column from the files in the second and third documents
    column2_from_df2 = df2.iloc[:, 1]
    column2_from_df3 = df3.iloc[:, 1]
    
    # Add these columns to the corresponding file in the first document
    df1['tmin'] = column2_from_df2
    df1['tmax'] = column2_from_df3
    
    # Save the updated DataFrame to a new Excel file in the output directory
    output_file_path = os.path.join(output_dir, file_name)
    df1.to_excel(output_file_path, index=False)
    
    print(f"Updated file saved to {output_file_path}")

print("All files have been updated and saved.")


# +
#############################################################
#       This part is for merging the columns                #
#       from new data to the bottom rows of the old data    #
#       with the same column name                           #
#############################################################





import os
import pandas as pd

# Define the directories containing the Excel files

dir1 = './washington'
dir2 = './merge_updates'

output_dir = './final'  # Directory to save the updated files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# List of Excel file names (assuming they have the same names in each document)
excel_files = os.listdir(dir1)

for file_name in excel_files:
    # Paths to the corresponding files in each directory
    file1_path = os.path.join(dir1, file_name)
    file2_path = os.path.join(dir2, file_name)
    
    # Check if file exists in both directories
    if not os.path.exists(file2_path):
        print(f"File {file_name} does not exist in {dir2}. Skipping...")
        continue
    
    # Read the Excel files
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)
    
    # Concatenate the DataFrames based on the same column names
    merged_df = pd.concat([df1, df2], axis=0, join='inner')
    
    # Reset the index of the merged DataFrame
    merged_df.reset_index(drop=True, inplace=True)
    
    # Save the updated DataFrame to a new Excel file in the output directory
    output_file_path = os.path.join(output_dir, file_name)
    merged_df.to_excel(output_file_path, index=False)
    
    print(f"Updated file saved to {output_file_path}")

print("All files have been updated and saved.")


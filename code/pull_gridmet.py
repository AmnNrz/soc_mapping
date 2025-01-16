# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: gee
#     language: python
#     name: python3
# ---

# +
import geopandas as gpd
import pandas as pd
import numpy as np


path_to_data = ("/home/a.norouzikandelati/Projects/soc_mapping/data/")

shp_2022 = gpd.read_file(path_to_data + "shapefile/shp_2022_lat_lon.shp")
shp_2023 = gpd.read_file(path_to_data + "shapefile/shp_2023_lat_lon.shp")

# Check if pointIDs are unique
is_any_equal = shp_2023['pointID'].isin(shp_2022['pointID']).any()
print(is_any_equal)

cols = ['pointID', 'latitude', 'longitude']
df = pd.concat([shp_2022[cols], shp_2023[cols]])


# +
# import pandas as pd
# import os
# from geopy.distance import geodesic
# import shutil

# # Folder paths on Kamiak
# source_folder = ('/weka/data/lab/adam/data/metdata/historical/'
#                  'UI_historical/VIC_Binary_CONUS_1979_to_2022_24thD')  # Replace with the folder path containing the files on Kamiak
# destination_folder = path_to_data +('grid_met')  # Replace with your Kamiak folder path

# # Ensure the destination folder exists
# os.makedirs(destination_folder, exist_ok=True)

# # Extract latitude and longitude from file names
# file_names = [f for f in os.listdir(source_folder) if f.startswith('data_')]
# file_coordinates = []

# for file_name in file_names:
#     try:
#         _, lat_lon = file_name.split('_', 1)
#         lat, lon = map(float, lat_lon.split('_'))
#         file_coordinates.append((file_name, (lat, lon)))
#     except ValueError:
#         print(f"Skipping invalid file name: {file_name}")

# # Function to find the closest file for a given point
# def find_closest_file(lat, lon, file_coordinates):
#     point_coords = (lat, lon)
#     closest_file = None
#     closest_distance = float('inf')
    
#     for file_name, coords in file_coordinates:
#         distance = geodesic(point_coords, coords).meters
#         if distance < closest_distance:
#             closest_distance = distance
#             closest_file = file_name
    
#     return closest_file

# # Add the closest file name to the dataframe
# df['gridmet_file'] = df.apply(lambda row: find_closest_file(row['latitude'], row['longitude'], file_coordinates), axis=1)

# # Copy files to the destination folder
# for file_name in df['gridmet_file'].unique():
#     source_path = os.path.join(source_folder, file_name)
#     destination_path = os.path.join(destination_folder, file_name)
#     if os.path.exists(source_path):
#         shutil.copy2(source_path, destination_path)  # Copies file with metadata
#     else:
#         print(f"File {file_name} not found in source folder.")

# # Save the updated dataframe to track downloads
# output_path = os.path.join(destination_folder, 'gridmet_file_df.csv')
# df.to_csv(output_path, index=False)

# print(f"Updated dataframe saved to {output_path}")
# print(f"Files copied to {destination_folder}")

# +
import os
import numpy as np
import pandas as pd
#Determine unsigned and sigend 2 bytes integer values. unsigned values are for variables that has 0 or positive values.
def read_gridMET(file_path):
    dt = np.dtype([
        ('precip', '<u2'),
        ('tmax', '<i2'),
        ('tmin', '<i2'),
        ('windspeed', '<i2'),
        ('SPH', '<i2'),
        ('SRAD', '<i2'),
        ('Rmax', '<i2'),
        ('Rmin', '<i2')
    ])
    
    with open(file_path, 'rb') as f:
        b = f.read()
        
    np_data = np.frombuffer(b, dt)
    num_records = len(np_data)

    # Generate a date range with the exact number of records
    start_date = '1979-01-01'
    date_rng = pd.date_range(start=start_date, periods=num_records, freq='D')

    # Validate lengths
    if len(np_data) != len(date_rng):
        raise ValueError(
            f"Data length ({len(np_data)}) does not match date range length ({len(date_rng)})"
        )

    # Create DataFrame
    df = pd.DataFrame(np_data)
    df.insert(0, 'date', date_rng)

    # Apply scaling
    df['precip'] = df['precip'] / 40
    df['tmax'] = df['tmax'] / 100
    df['tmin'] = df['tmin'] / 100
    df['windspeed'] = df['windspeed'] / 100
    df['SPH'] = df['SPH'] / 10000
    df['SRAD'] = df['SRAD'] / 40
    df['Rmax'] = df['Rmax'] / 100
    df['Rmin'] = df['Rmin'] / 100

    return df


# Directory containing binary files
binary_files_directory = path_to_data + "gridmet/"

# List to hold DataFrames of processed binary files
data_frames = []

# Get all file names in the folder
file_names = os.listdir(path_to_data + "gridmet/")

# Loop through each binary file and match with latitude and longitude
for name in file_names:
    binary_file_path = os.path.join(binary_files_directory, name)
    
    if os.path.exists(binary_file_path):
        df = read_gridMET(binary_file_path)
        data_frames.append(df)

# Iterate through the data frames in the list
for i in range(len(data_frames)):
    df = data_frames[i]
    
    # Calculate the average column
    df['tavg'] = (df['tmin'] + df['tmax']) / 2

    # Reorder the columns to place 'tavg' next to 'tmin'
    columns = ['date', 'precip', 'tmin', 'tavg', 'tmax', 'windspeed', 'SPH', 'SRAD', 'Rmax', 'Rmin']
    data_frames[i] = df[columns]

    print(f"Processed DataFrame {i + 1}")

print("All files processed.")


# +
import os
import numpy as np
import pandas as pd
#Determine unsigned and sigend 2 bytes integer values. unsigned values are for variables that has 0 or positive values.
def read_gridMET(file_path):
    dt = np.dtype([
        ('precip', '<u2'),
        ('tmax', '<i2'),
        ('tmin', '<i2'),
        ('windspeed', '<i2'),
        ('SPH', '<i2'),
        ('SRAD', '<i2'),
        ('Rmax', '<i2'),
        ('Rmin', '<i2')
    ])
    
    with open(file_path, 'rb') as f:
        b = f.read()
        
    date_rng = pd.date_range(start='1979-01-01', end='2019-12-31', freq='D')
    np_data = np.frombuffer(b, dt)
    
    df = pd.DataFrame(np_data)
    df.insert(0, 'date', date_rng)
    
    df['date'] = pd.to_datetime(df['date'])
    df['precip'] = df['precip'] / 40
    df['tmax'] = df['tmax'] / 100
    df['tmin'] = df['tmin'] / 100
    df['windspeed'] = df['windspeed'] / 100
    df['SPH'] = df['SPH'] / 10000
    df['SRAD'] = df['SRAD'] / 40
    df['Rmax'] = df['Rmax'] / 100
    df['Rmin'] = df['Rmin'] / 100

    return df


# Directory containing binary files
binary_files_directory = path_to_data + "gridmet/"

# List to hold DataFrames of processed binary files
data_frames = []

os.listdir(path_to_data + "gridmet/")

# Loop through each binary file and match with latitude and longitude
for name in file_names:
    binary_file_path = os.path.join(binary_files_directory, name)
    
    if os.path.exists(binary_file_path):
        df = read_gridMET(binary_file_path)
        data_frames.append(df)

# Iterate through the data frames in the list
for i in range(len(data_frames)):
    df = data_frames[i]
    
    # Calculate the average column
    df['tavg'] = (df['tmin'] + df['tmax']) / 2

    # Reorder the columns to place 'tavg' next to 'tmin'
    columns = ['date', 'precip', 'tmin', 'tavg', 'tmax', 'windspeed', 'SPH', 'SRAD', 'Rmax', 'Rmin']
    data_frames[i] = df[columns]

    print(f"Processed DataFrame {i + 1}")

print("All files processed.")



# +
import os
import numpy as np
import pandas as pd

def read_gridMET(file_path):
    dt = np.dtype([
        ('precip', '<u2'),
        ('tmax', '<i2'),
        ('tmin', '<i2'),
        ('windspeed', '<i2'),
        ('SPH', '<i2'),
        ('SRAD', '<i2'),
        ('Rmax', '<i2'),
        ('Rmin', '<i2')
    ])
    
    with open(file_path, 'rb') as f:
        b = f.read()
        
    np_data = np.frombuffer(b, dt)
    num_records = len(np_data)
    date_rng = pd.date_range(start='1979-01-01', periods=num_records, freq='D')
    
    df = pd.DataFrame(np_data)
    df.insert(0, 'date', date_rng)
    
    df['date'] = pd.to_datetime(df['date'])
    df['precip'] = df['precip'] / 40
    df['tmax'] = df['tmax'] / 100
    df['tmin'] = df['tmin'] / 100
    df['windspeed'] = df['windspeed'] / 100
    df['SPH'] = df['SPH'] / 10000
    df['SRAD'] = df['SRAD'] / 40
    df['Rmax'] = df['Rmax'] / 100
    df['Rmin'] = df['Rmin'] / 100

    return df


# Directory containing binary files
binary_files_directory = path_to_data + "gridmet/"

# List to hold DataFrames of processed binary files
data_frames = []

file_names = os.listdir(binary_files_directory)

# Loop through each binary file and match with latitude and longitude
for name in file_names:
    binary_file_path = os.path.join(binary_files_directory, name)
    
    if os.path.exists(binary_file_path):
        df = read_gridMET(binary_file_path)
        data_frames.append(df)

# Iterate through the data frames in the list
for i in range(len(data_frames)):
    df = data_frames[i]
    
    # Calculate the average column
    df['tavg'] = (df['tmin'] + df['tmax']) / 2

    # Reorder the columns to place 'tavg' next to 'tmin'
    columns = ['date', 'precip', 'tmin', 'tavg', 'tmax', 'windspeed', 'SPH', 'SRAD', 'Rmax', 'Rmin']
    data_frames[i] = df[columns]

    print(f"Processed DataFrame {i + 1}")

print("All files processed.")


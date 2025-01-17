library(agclimtools)
library(dplyr)



# Define the path to the data folder
path_to_data <- paste0(
  "/home/amin-norouzi/OneDrive/Ph.D/Projects/",
  "soc_mapping/data/"
)

# Read files that tracked pointIDs
grid_file_pointid <- read.csv(paste0(path_to_data, "gridmet_file_df.csv"))

# Initialize an empty list to store data frames
all_data <- list()

# Loop through each row of grid_file_pointid
for (i in 1:nrow(grid_file_pointid)) {
  # Get the pointID and gridmet_file for the current row
  pointID <- grid_file_pointid$pointID[i]
  gridmet_file <- grid_file_pointid$gridmet_file[i]
  
  # Construct the full file path
  file_path <- paste0(path_to_data, "gridmet/", gridmet_file)
  
  # Check if the file exists
  if (file.exists(file_path)) {
    # Read the file using read_gridmet
    data <- read_gridmet(file_path, begin = 2020, end = 2023)
    
    # Add the pointID and gridmet_file columns to the data
    data$pointID <- pointID
    data$gridmet_file <- gridmet_file
    
    # Append the data frame to the list
    all_data[[gridmet_file]] <- data
  } else {
    warning(paste("File not found:", file_path))
  }
}

# Combine all data frames into one
final_data <- do.call(rbind, all_data)

final_data <- data.frame(final_data, row.names = NULL)


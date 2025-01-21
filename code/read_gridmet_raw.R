library(agclimtools)
library(dplyr)
library(sf)



# Define the path to the data folder
# path_to_data <- paste0(
#   "/home/amin-norouzi/OneDrive/Ph.D/Projects/",
#   "soc_mapping/data/"
# )

path_to_data <- paste0(
  '/Users/aminnorouzi/Library/CloudStorage/',
  'OneDrive-WashingtonStateUniversity(email.wsu.edu)/Ph.D/',
  'Projects/soc_mapping/data/'
)


# Read files that tracked pointIDs
grid_file_pointid <- read.csv(paste0(path_to_data, "gridmet_file_df.csv"))

# Initialize an empty list to store data frames
all_data <- list()

i <- 689
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
    data <- read_gridmet(file_path, begin = 1979, end = 2023)
    
    # Add the pointID and gridmet_file columns to the data
    data$pointID <- pointID
    data$gridmet_file <- gridmet_file
    
    # Append the data frame to the list
    all_data[[pointID]] <- data
  } else {
    warning(paste("File not found:", file_path))
  }
}

# Combine all data frames into one
final_data <- do.call(rbind, all_data)

final_data <- data.frame(final_data, row.names = NULL)

# Add year of survey to the dataframe
year_df <- read.csv(paste0(path_to_data, "year_pointID.csv"))


final_data <- merge(final_data, year_df, by = "pointID", all.x = TRUE)

final_data$tavg <- rowMeans(final_data[, c("tmax", "tmin")], na.rm = TRUE)



gdd_cal <- function(df) {
  df <- df %>%
    mutate(gdd = case_when(
      tavg < 0 ~ 0,
      tavg > 30 ~ 30,
      TRUE ~ tavg
    ))
  return(df)
}

final_data <- gdd_cal(final_data)





final_df <- data.frame()

for (y in unique(final_data$Year)){

  final_data_y <- final_data %>% dplyr::filter(Year == y)
  
  final_data_y <- final_data_y %>% select(-Year)
  
  # Load necessary libraries
  library(dplyr)
  library(lubridate)
  
  # Remove rows with NaN values
  final_data_y <- final_data_y %>%
    filter(!is.na(precip) & !is.na(tmax) & !is.na(tmin) & !is.na(windspeed) & !is.na(gdd))
  
  # Convert 'date' to Date type
  final_data_y$date <- as.Date(final_data_y$date)
  
  # Extract the year and month
  final_data_y$year <- year(final_data_y$date)
  final_data_y$month <- month(final_data_y$date)
  
  # Create a season column based on the month
  final_data_y$season <- case_when(
    final_data_y$month %in% c(3, 4, 5) ~ "Spring",
    final_data_y$month %in% c(6, 7, 8) ~ "Summer",
    final_data_y$month %in% c(9, 10, 11) ~ "Fall",
    final_data_y$month %in% c(12, 1, 2) ~ "Winter",
    TRUE ~ "Other"
  )
  
  # Create a function to calculate average seasonal values for any given year window (cumulative)
  calculate_seasonal_avg <- function(data, season, var_name, years) {
    data %>%
      filter(season == season) %>%
      group_by(pointID, year) %>%
      summarise(var_accum = sum(!!sym(var_name), na.rm = TRUE)) %>%
      filter(year >= min(years) & year <= max(years)) %>%
      summarise(var_avg = mean(var_accum, na.rm = TRUE))
  }
  
  # Function to calculate seasonal average for temperature (not accumulative)
  calculate_seasonal_temp_avg <- function(data, season, var_name, years) {
    data %>%
      filter(season == season) %>%
      group_by(pointID, year) %>%
      summarise(var_avg = mean(!!sym(var_name), na.rm = TRUE)) %>%
      filter(year >= min(years) & year <= max(years)) %>%
      summarise(var_avg = mean(var_avg, na.rm = TRUE))
  }
  
  
  # Function to calculate seasonal average for wind speed (not accumulative)
  calculate_seasonal_windspeed_avg <- function(data, season, var_name, years) {
    data %>%
      filter(season == season) %>%
      group_by(pointID, year) %>%
      summarise(var_avg = mean(!!sym(var_name), na.rm = TRUE)) %>%
      filter(year >= min(years) & year <= max(years)) %>%
      summarise(var_avg = mean(var_avg, na.rm = TRUE))
  }
  
  
  # Calculate the seasonal average for each time window (30, 10, 5, and 1-year) and each season
  
  # Precipitation (accumulative) for different years
  years_30 <- 1991:y-1
  years_10 <- 2011:y-1
  years_5 <- 2017:y-1
  years_1 <- y-1
  
  precip_spring_30 <- calculate_seasonal_avg(final_data_y, "Spring", "precip", years_30)
  precip_summer_30 <- calculate_seasonal_avg(final_data_y, "Summer", "precip", years_30)
  precip_fall_30 <- calculate_seasonal_avg(final_data_y, "Fall", "precip", years_30)
  precip_winter_30 <- calculate_seasonal_avg(final_data_y, "Winter", "precip", years_30)
  
  precip_spring_10 <- calculate_seasonal_avg(final_data_y, "Spring", "precip", years_10)
  precip_summer_10 <- calculate_seasonal_avg(final_data_y, "Summer", "precip", years_10)
  precip_fall_10 <- calculate_seasonal_avg(final_data_y, "Fall", "precip", years_10)
  precip_winter_10 <- calculate_seasonal_avg(final_data_y, "Winter", "precip", years_10)
  
  precip_spring_5 <- calculate_seasonal_avg(final_data_y, "Spring", "precip", years_5)
  precip_summer_5 <- calculate_seasonal_avg(final_data_y, "Summer", "precip", years_5)
  precip_fall_5 <- calculate_seasonal_avg(final_data_y, "Fall", "precip", years_5)
  precip_winter_5 <- calculate_seasonal_avg(final_data_y, "Winter", "precip", years_5)
  
  precip_spring_1 <- calculate_seasonal_avg(final_data_y, "Spring", "precip", years_1)
  precip_summer_1 <- calculate_seasonal_avg(final_data_y, "Summer", "precip", years_1)
  precip_fall_1 <- calculate_seasonal_avg(final_data_y, "Fall", "precip", years_1)
  precip_winter_1 <- calculate_seasonal_avg(final_data_y, "Winter", "precip", years_1)
  
  # Temperature (non-accumulative) for different years
  temp_spring_30 <- calculate_seasonal_temp_avg(final_data_y, "Spring", "tmax", years_30)
  temp_summer_30 <- calculate_seasonal_temp_avg(final_data_y, "Summer", "tmax", years_30)
  temp_fall_30 <- calculate_seasonal_temp_avg(final_data_y, "Fall", "tmax", years_30)
  temp_winter_30 <- calculate_seasonal_temp_avg(final_data_y, "Winter", "tmax", years_30)
  
  temp_spring_10 <- calculate_seasonal_temp_avg(final_data_y, "Spring", "tmax", years_10)
  temp_summer_10 <- calculate_seasonal_temp_avg(final_data_y, "Summer", "tmax", years_10)
  temp_fall_10 <- calculate_seasonal_temp_avg(final_data_y, "Fall", "tmax", years_10)
  temp_winter_10 <- calculate_seasonal_temp_avg(final_data_y, "Winter", "tmax", years_10)
  
  temp_spring_5 <- calculate_seasonal_temp_avg(final_data_y, "Spring", "tmax", years_5)
  temp_summer_5 <- calculate_seasonal_temp_avg(final_data_y, "Summer", "tmax", years_5)
  temp_fall_5 <- calculate_seasonal_temp_avg(final_data_y, "Fall", "tmax", years_5)
  temp_winter_5 <- calculate_seasonal_temp_avg(final_data_y, "Winter", "tmax", years_5)
  
  temp_spring_1 <- calculate_seasonal_temp_avg(final_data_y, "Spring", "tmax", years_1)
  temp_summer_1 <- calculate_seasonal_temp_avg(final_data_y, "Summer", "tmax", years_1)
  temp_fall_1 <- calculate_seasonal_temp_avg(final_data_y, "Fall", "tmax", years_1)
  temp_winter_1 <- calculate_seasonal_temp_avg(final_data_y, "Winter", "tmax", years_1)
  
  # Calculate the seasonal average for wind speed (non-accumulative) for different years
  windspeed_spring_30 <- calculate_seasonal_windspeed_avg(final_data_y, "Spring", "windspeed", years_30)
  windspeed_summer_30 <- calculate_seasonal_windspeed_avg(final_data_y, "Summer", "windspeed", years_30)
  windspeed_fall_30 <- calculate_seasonal_windspeed_avg(final_data_y, "Fall", "windspeed", years_30)
  windspeed_winter_30 <- calculate_seasonal_windspeed_avg(final_data_y, "Winter", "windspeed", years_30)
  
  windspeed_spring_10 <- calculate_seasonal_windspeed_avg(final_data_y, "Spring", "windspeed", years_10)
  windspeed_summer_10 <- calculate_seasonal_windspeed_avg(final_data_y, "Summer", "windspeed", years_10)
  windspeed_fall_10 <- calculate_seasonal_windspeed_avg(final_data_y, "Fall", "windspeed", years_10)
  windspeed_winter_10 <- calculate_seasonal_windspeed_avg(final_data_y, "Winter", "windspeed", years_10)
  
  windspeed_spring_5 <- calculate_seasonal_windspeed_avg(final_data_y, "Spring", "windspeed", years_5)
  windspeed_summer_5 <- calculate_seasonal_windspeed_avg(final_data_y, "Summer", "windspeed", years_5)
  windspeed_fall_5 <- calculate_seasonal_windspeed_avg(final_data_y, "Fall", "windspeed", years_5)
  windspeed_winter_5 <- calculate_seasonal_windspeed_avg(final_data_y, "Winter", "windspeed", years_5)
  
  windspeed_spring_1 <- calculate_seasonal_windspeed_avg(final_data_y, "Spring", "windspeed", years_1)
  windspeed_summer_1 <- calculate_seasonal_windspeed_avg(final_data_y, "Summer", "windspeed", years_1)
  windspeed_fall_1 <- calculate_seasonal_windspeed_avg(final_data_y, "Fall", "windspeed", years_1)
  windspeed_winter_1 <- calculate_seasonal_windspeed_avg(final_data_y, "Winter", "windspeed", years_1)
  
  
  # gdd (accumulative) for different years
  gdd_spring_30 <- calculate_seasonal_avg(final_data_y, "Spring", "gdd", years_30)
  gdd_summer_30 <- calculate_seasonal_avg(final_data_y, "Summer", "gdd", years_30)
  gdd_fall_30 <- calculate_seasonal_avg(final_data_y, "Fall", "gdd", years_30)
  gdd_winter_30 <- calculate_seasonal_avg(final_data_y, "Winter", "gdd", years_30)
  
  gdd_spring_10 <- calculate_seasonal_avg(final_data_y, "Spring", "gdd", years_10)
  gdd_summer_10 <- calculate_seasonal_avg(final_data_y, "Summer", "gdd", years_10)
  gdd_fall_10 <- calculate_seasonal_avg(final_data_y, "Fall", "gdd", years_10)
  gdd_winter_10 <- calculate_seasonal_avg(final_data_y, "Winter", "gdd", years_10)
  
  gdd_spring_5 <- calculate_seasonal_avg(final_data_y, "Spring", "gdd", years_5)
  gdd_summer_5 <- calculate_seasonal_avg(final_data_y, "Summer", "gdd", years_5)
  gdd_fall_5 <- calculate_seasonal_avg(final_data_y, "Fall", "gdd", years_5)
  gdd_winter_5 <- calculate_seasonal_avg(final_data_y, "Winter", "gdd", years_5)
  
  gdd_spring_1 <- calculate_seasonal_avg(final_data_y, "Spring", "gdd", years_1)
  gdd_summer_1 <- calculate_seasonal_avg(final_data_y, "Summer", "gdd", years_1)
  gdd_fall_1 <- calculate_seasonal_avg(final_data_y, "Fall", "gdd", years_1)
  gdd_winter_1 <- calculate_seasonal_avg(final_data_y, "Winter", "gdd", years_1)
  
  
  
  # Merge all the results into a single dataframe
  seasonal_data <- precip_spring_30 %>%
    rename(precip_avg_spring_30yr = var_avg) %>%
    left_join(precip_summer_30 %>% rename(precip_avg_summer_30yr = var_avg), by = "pointID") %>%
    left_join(precip_fall_30 %>% rename(precip_avg_fall_30yr = var_avg), by = "pointID") %>%
    left_join(precip_winter_30 %>% rename(precip_avg_winter_30yr = var_avg), by = "pointID") %>%
    
    # Add the 10-year precipitation averages
    left_join(precip_spring_10 %>% rename(precip_avg_spring_10yr = var_avg), by = "pointID") %>%
    left_join(precip_summer_10 %>% rename(precip_avg_summer_10yr = var_avg), by = "pointID") %>%
    left_join(precip_fall_10 %>% rename(precip_avg_fall_10yr = var_avg), by = "pointID") %>%
    left_join(precip_winter_10 %>% rename(precip_avg_winter_10yr = var_avg), by = "pointID") %>%
    
    # Add the 5-year precipitation averages
    left_join(precip_spring_5 %>% rename(precip_avg_spring_5yr = var_avg), by = "pointID") %>%
    left_join(precip_summer_5 %>% rename(precip_avg_summer_5yr = var_avg), by = "pointID") %>%
    left_join(precip_fall_5 %>% rename(precip_avg_fall_5yr = var_avg), by = "pointID") %>%
    left_join(precip_winter_5 %>% rename(precip_avg_winter_5yr = var_avg), by = "pointID") %>%
    
    # Add the 1-year precipitation averages
    left_join(precip_spring_1 %>% rename(precip_avg_spring_1yr = var_avg), by = "pointID") %>%
    left_join(precip_summer_1 %>% rename(precip_avg_summer_1yr = var_avg), by = "pointID") %>%
    left_join(precip_fall_1 %>% rename(precip_avg_fall_1yr = var_avg), by = "pointID") %>%
    left_join(precip_winter_1 %>% rename(precip_avg_winter_1yr = var_avg), by = "pointID") %>%
    
    # Add the 30-year temperature averages (max temperature)
    left_join(temp_spring_30 %>% rename(temp_avg_spring_30yr = var_avg), by = "pointID") %>%
    left_join(temp_summer_30 %>% rename(temp_avg_summer_30yr = var_avg), by = "pointID") %>%
    left_join(temp_fall_30 %>% rename(temp_avg_fall_30yr = var_avg), by = "pointID") %>%
    left_join(temp_winter_30 %>% rename(temp_avg_winter_30yr = var_avg), by = "pointID") %>%
    
    # Add the 10-year temperature averages
    left_join(temp_spring_10 %>% rename(temp_avg_spring_10yr = var_avg), by = "pointID") %>%
    left_join(temp_summer_10 %>% rename(temp_avg_summer_10yr = var_avg), by = "pointID") %>%
    left_join(temp_fall_10 %>% rename(temp_avg_fall_10yr = var_avg), by = "pointID") %>%
    left_join(temp_winter_10 %>% rename(temp_avg_winter_10yr = var_avg), by = "pointID") %>%
    
    # Add the 5-year temperature averages
    left_join(temp_spring_5 %>% rename(temp_avg_spring_5yr = var_avg), by = "pointID") %>%
    left_join(temp_summer_5 %>% rename(temp_avg_summer_5yr = var_avg), by = "pointID") %>%
    left_join(temp_fall_5 %>% rename(temp_avg_fall_5yr = var_avg), by = "pointID") %>%
    left_join(temp_winter_5 %>% rename(temp_avg_winter_5yr = var_avg), by = "pointID") %>%
    
    # Add the 1-year temperature averages
    left_join(temp_spring_1 %>% rename(temp_avg_spring_1yr = var_avg), by = "pointID") %>%
    left_join(temp_summer_1 %>% rename(temp_avg_summer_1yr = var_avg), by = "pointID") %>%
    left_join(temp_fall_1 %>% rename(temp_avg_fall_1yr = var_avg), by = "pointID") %>%
    left_join(temp_winter_1 %>% rename(temp_avg_winter_1yr = var_avg), by = "pointID") %>%
    
    # Add the 30-year windspeed averages
    left_join(windspeed_spring_30 %>% rename(windspeed_avg_spring_30yr = var_avg), by = "pointID") %>%
    left_join(windspeed_summer_30 %>% rename(windspeed_avg_summer_30yr = var_avg), by = "pointID") %>%
    left_join(windspeed_fall_30 %>% rename(windspeed_avg_fall_30yr = var_avg), by = "pointID") %>%
    left_join(windspeed_winter_30 %>% rename(windspeed_avg_winter_30yr = var_avg), by = "pointID") %>%
    
    # Add the 10-year windspeed averages
    left_join(windspeed_spring_10 %>% rename(windspeed_avg_spring_10yr = var_avg), by = "pointID") %>%
    left_join(windspeed_summer_10 %>% rename(windspeed_avg_summer_10yr = var_avg), by = "pointID") %>%
    left_join(windspeed_fall_10 %>% rename(windspeed_avg_fall_10yr = var_avg), by = "pointID") %>%
    left_join(windspeed_winter_10 %>% rename(windspeed_avg_winter_10yr = var_avg), by = "pointID") %>%
    
    # Add the 5-year windspeed averages
    left_join(windspeed_spring_5 %>% rename(windspeed_avg_spring_5yr = var_avg), by = "pointID") %>%
    left_join(windspeed_summer_5 %>% rename(windspeed_avg_summer_5yr = var_avg), by = "pointID") %>%
    left_join(windspeed_fall_5 %>% rename(windspeed_avg_fall_5yr = var_avg), by = "pointID") %>%
    left_join(windspeed_winter_5 %>% rename(windspeed_avg_winter_5yr = var_avg), by = "pointID") %>%
    
    # Add the 1-year windspeed averages
    left_join(windspeed_spring_1 %>% rename(windspeed_avg_spring_1yr = var_avg), by = "pointID") %>%
    left_join(windspeed_summer_1 %>% rename(windspeed_avg_summer_1yr = var_avg), by = "pointID") %>%
    left_join(windspeed_fall_1 %>% rename(windspeed_avg_fall_1yr = var_avg), by = "pointID") %>%
    left_join(windspeed_winter_1 %>% rename(windspeed_avg_winter_1yr = var_avg), by = "pointID") %>% 
    
    # gdd
    left_join(gdd_spring_30 %>% rename(gdd_avg_spring_30yr = var_avg), by = "pointID") %>%
    left_join(gdd_summer_30 %>% rename(gdd_avg_summer_30yr = var_avg), by = "pointID") %>%
    left_join(gdd_fall_30 %>% rename(gdd_avg_fall_30yr = var_avg), by = "pointID") %>%
    left_join(gdd_winter_30 %>% rename(gdd_avg_winter_30yr = var_avg), by = "pointID") %>%
    
    # Add the 10-year gdditation averages
    left_join(gdd_spring_10 %>% rename(gdd_avg_spring_10yr = var_avg), by = "pointID") %>%
    left_join(gdd_summer_10 %>% rename(gdd_avg_summer_10yr = var_avg), by = "pointID") %>%
    left_join(gdd_fall_10 %>% rename(gdd_avg_fall_10yr = var_avg), by = "pointID") %>%
    left_join(gdd_winter_10 %>% rename(gdd_avg_winter_10yr = var_avg), by = "pointID") %>%
    
    # Add the 5-year gdditation averages
    left_join(gdd_spring_5 %>% rename(gdd_avg_spring_5yr = var_avg), by = "pointID") %>%
    left_join(gdd_summer_5 %>% rename(gdd_avg_summer_5yr = var_avg), by = "pointID") %>%
    left_join(gdd_fall_5 %>% rename(gdd_avg_fall_5yr = var_avg), by = "pointID") %>%
    left_join(gdd_winter_5 %>% rename(gdd_avg_winter_5yr = var_avg), by = "pointID") %>%
    
    # Add the 1-year gdditation averages
    left_join(gdd_spring_1 %>% rename(gdd_avg_spring_1yr = var_avg), by = "pointID") %>%
    left_join(gdd_summer_1 %>% rename(gdd_avg_summer_1yr = var_avg), by = "pointID") %>%
    left_join(gdd_fall_1 %>% rename(gdd_avg_fall_1yr = var_avg), by = "pointID") %>%
    left_join(gdd_winter_1 %>% rename(gdd_avg_winter_1yr = var_avg), by = "pointID")
    
  final_df <- rbind(final_df, seasonal_data)
  
}




# Add soil data
# Read the shapefile
shape_22 <- st_read(paste0(path_to_data, "soil_data/Shapefile_2022.shp"))
shape_23 <- st_read(paste0(path_to_data, "soil_data/Shapefile_2023.shp"))

cols <- c("pointID", "muname")
soil_data <- rbind(shape_22[cols], shape_23[cols])
soil_data$soil_type <- soil_data$muname

soil_data$soil_type <- sub(",.*", "", soil_data$soil_type)

# Perform the left join
final_df <- final_df %>%
  left_join(select(soil_data, pointID, soil_type), by = "pointID")

# Move the soil_type column to the first position
final_df <- final_df %>%
  select(soil_type, everything())

write.csv(final_df, file = paste0(path_to_data, "env_data.csv"), row.names = FALSE)

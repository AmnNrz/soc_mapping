# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.6
#   kernelspec:
#     display_name: base
#     language: python
#     name: python3
# ---

# +
##############################################
#         Download a single netcdf file      #
##############################################

import os
import requests
from bs4 import BeautifulSoup

# Step 1: Scrape the webpage to get the URLs of the NetCDF files
def get_netcdf_links(url, file_extension="nc", desired_files=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers, timeout=10)  # Added headers and timeout
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links with the .nc file extension
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith(file_extension):
            file_name = href.split("/")[-1]  # Extract file name from the URL
            
            # Only add the link if the file name is in the list of desired files
            if desired_files and file_name in desired_files:
                if not href.startswith('http'):
                    href = os.path.join(url, href)  # Handle relative URLs
                links.append(href)
    
    return links

# Step 2: Download the NetCDF files from the URLs
def download_netcdf_files(links, destination_folder="netcdf_files"):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for link in links:
        file_name = os.path.join(destination_folder, link.split("/")[-1])

        try:
            # Download the file
            response = requests.get(link, timeout=10)  # Added timeout
            response.raise_for_status()  # Raises an error for bad responses (4xx or 5xx)

            with open(file_name, 'wb') as file:
                file.write(response.content)

            print(f"Downloaded: {file_name}")
        
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {link}. Error: {e}")

# Usage
url = 'https://www.northwestknowledge.net/metdata/data/'  # The actual URL containing the NetCDF files
desired_files = ['spei14d.nc']  # List of specific NetCDF files you want to download

# Get the URLs for only the files you want
file_links = get_netcdf_links(url, file_extension='nc', desired_files=desired_files)

# Download the selected files
download_netcdf_files(file_links)

# +
##############################################
#         Download multiple netcdf file      #
##############################################
import os
import requests
from bs4 import BeautifulSoup

# Step 1: Scrape the webpage to get the URLs of the NetCDF files
def get_netcdf_links(url, file_extension="nc", desired_files=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all links with the .nc file extension
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith(file_extension):
            file_name = href.split("/")[-1]  # Extract file name from the URL
            
            # Only add the link if the file name is in the list of desired files
            if desired_files and file_name in desired_files:
                if not href.startswith('http'):
                    href = url + href  # Handle relative URLs
                links.append(href)
    
    return links

# Step 2: Download the NetCDF files from the URLs
def download_netcdf_files(links, destination_folder="netcdf_files"):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for link in links:
        file_name = os.path.join(destination_folder, link.split("/")[-1])

        # Download the file
        response = requests.get(link)
        with open(file_name, 'wb') as file:
            file.write(response.content)

        print(f"Downloaded: {file_name}")

# Usage
url = 'https://www.northwestknowledge.net/metdata/data/'  # The actual URL containing the NetCDF files
years = [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
for year in years:
    desired_files = [f'pr_{year}.nc']  # List of specific NetCDF files you want to download

    # Get the URLs for only the files you want
    file_links = get_netcdf_links(url, file_extension='nc', desired_files=desired_files)

    # Download the selected files
    download_netcdf_files(file_links)

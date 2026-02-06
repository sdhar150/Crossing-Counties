# Crossing Counties

An interactive Streamlit web application for comparing housing costs and
income levels across U.S. counties using HUD Fair Market Rent data and
U.S. Treasury median income data.

## Overview

Crossing Counties is a county-level comparison tool that enables
side-by-side analysis of:

-   HUD Fair Market Rent (1--4 bedroom units)
-   40% of median annual income by household size (1--8 members)
-   Rent relative to national average
-   Rent as a percentage of income (affordability metric)

The application processes housing data covering 3,000+ U.S. counties and
dynamically loads income data by state from a multi-sheet Excel
workbook.

This project is built with Python and Streamlit and includes a data
cleaning and normalization pipeline implemented in Pandas.

## Features

### County Comparison Interface

-   Dual-panel layout for selecting two counties
-   State dropdown (USPS two-letter codes)
-   County dropdown filtered by state
-   Bedroom selection (1--4 bedrooms)
-   FIPS-based internal lookup for accurate data joins

### Rent Statistics

For each selected county:

-   Fair Market Rent for selected bedroom count
-   Comparison to national average rent (mean across all counties)
-   Ratio of county rent to U.S. average

### Income Visualization

-   Scatter plot of 40% of median annual income
-   Household sizes 1--8
-   Data dynamically loaded from state-specific Excel sheets
-   County-level filtering using normalized 5-digit FIPS codes

### Rent Comparison Visualization

-   Bar chart comparing 1--4 bedroom rents
-   Side-by-side county comparison
-   Matplotlib-based rendering

### Affordability Analysis

-   Uses:
    -   2-bedroom rent
    -   4-person household income (40% median)
-   Computes:
    -   Rent as a percentage of monthly income
-   Displays:
    -   Horizontal bar chart
    -   30% affordability threshold reference line

## Tech Stack

-   Python 3.8+
-   Streamlit
-   Pandas
-   NumPy
-   Matplotlib
-   openpyxl (Excel support)

## Data Processing Pipeline

The data pipeline is implemented in `Process_Data.py`.

### Rent Data Processing

1.  File discovery across multiple directories
2.  Load `FY25_FMRs_revised` sheet from HUD Excel file
3.  Remove duplicate FIPS codes
4.  Replace invalid rent values (≤ 0) with NaN
5.  Median imputation for missing rent values
6.  Drop rows missing:
    -   county name
    -   state code
    -   FIPS
7.  Normalize FIPS codes to 5-digit zero-padded strings

### Income Data Processing

-   Dynamically loads state sheet based on selected county
-   Skips metadata rows
-   Drops unused columns
-   Standardizes column names:
    -   FIPS
    -   Household sizes 1--8
-   Normalizes FIPS to 5-digit strings
-   Filters to county-level record

No caching or persistent storage layer is used. Data is processed at
runtime.

## Installation

### 1. Clone the repository

    git clone https://github.com/sdhar150/Crossing-Counties.git
    cd Crossing-Counties

### 2. Install dependencies

    pip install -r requirements.txt

### 3. Download Required Data Files

#### Fair Market Rent Data

-   Source: U.S. Department of Housing and Urban Development
-   Download: FY2025 Fair Market Rents

#### Income Data

-   Source: U.S. Department of Treasury

### 4. Place Files

The application searches for data files in:

-   Current working directory
-   Script directory
-   `Code/` subdirectory
-   Parent directory

### 5. Run the Application

    streamlit run Display_Data.py

## Project Structure

    Crossing-Counties/
    │
    ├── Code/
    │   ├── Display_Data.py
    │   ├── Process_Data.py
    │   └── requirements.txt
    │
    ├── Fair_Market_Rents.xlsx
    ├── Income_Data.xlsx
    ├── README.md
    └── LICENSE

## Implementation Notes

-   Rent data is loaded at module initialization.
-   Income data is loaded per-state on demand.
-   All county joins are performed using normalized 5-digit FIPS codes.
-   National average rent is calculated dynamically using a mean across
    all counties.

## License

MIT License

## Author

Soham Dhar

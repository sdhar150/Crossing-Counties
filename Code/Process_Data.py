import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os

# Global variable for rent data
rent_data = None

def get_data_file_path(filename):
    """
    Find data file in common locations.
    
    Args:
        filename (str): Name of the data file
        
    Returns:
        str: Full path to file, or None if not found
    """
    # Possible locations to check
    search_paths = [
        os.getcwd(),  # Current working directory
        os.path.dirname(os.path.abspath(__file__)),  # Script directory
        os.path.join(os.getcwd(), 'Code'),  # Code subdirectory
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # Parent directory
    ]
    
    for path in search_paths:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            return full_path
    
    return None

def load_and_process_data():
    """
    Load and process rent data with comprehensive data cleaning pipeline.
    
    Returns:
        pd.DataFrame: Cleaned and processed rent data
    """
    try:
        # Find the rent data file
        rent_file = get_data_file_path('Fair_Market_Rents.xlsx')
        
        if rent_file is None:
            print("\n" + "="*60)
            print("ERROR: Fair_Market_Rents.xlsx NOT FOUND")
            print("="*60)
            print("Searched in:")
            print(f"  1. {os.getcwd()}")
            print(f"  2. {os.path.dirname(os.path.abspath(__file__))}")
            print(f"  3. {os.path.join(os.getcwd(), 'Code')}")
            print(f"  4. {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
            print("\nPlease download the file from:")
            print("  https://www.huduser.gov/portal/datasets/fmr.html#data_2025")
            print("="*60 + "\n")
            return pd.DataFrame()
        
        print(f"✓ Loading rent data from: {rent_file}")
        
        # Load rent data
        data = pd.read_excel(rent_file, sheet_name='FY25_FMRs_revised')
        print(f"✓ Loaded {len(data)} county records")
        
        # Data cleaning pipeline
        data = clean_rent_data(data)
        print(f"✓ Data cleaned: {len(data)} records after removing duplicates/invalid")
        
        data = normalize_fips_codes(data)
        
        # Validate FIPS codes
        valid_fips = data['fips'].str.len().eq(5).sum()
        print(f"✓ FIPS codes normalized: {valid_fips}/{len(data)} are 5 digits")
        
        if valid_fips == 0:
            print("⚠ WARNING: No valid FIPS codes found - data may not work properly")
            print(f"  Sample FIPS values: {data['fips'].head().tolist()}")
        
        print(f"✓ Data cleaning complete: {len(data)} counties ready")
        
        return data
        
    except Exception as e:
        print(f"\nERROR loading data: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()

def clean_rent_data(data):
    """
    Clean rent data by handling missing values, duplicates, and invalid entries.
    
    Args:
        data (pd.DataFrame): Raw rent data
        
    Returns:
        pd.DataFrame: Cleaned rent data
    """
    # Remove duplicate FIPS codes
    data = data.drop_duplicates(subset=['fips'], keep='first')
    
    # Handle missing values in rent columns
    rent_columns = ['fmr_1', 'fmr_2', 'fmr_3', 'fmr_4']
    for col in rent_columns:
        if col in data.columns:
            # Replace negative or zero values with NaN
            data[col] = data[col].apply(lambda x: x if pd.notna(x) and x > 0 else np.nan)
            # Fill missing values with median
            data[col].fillna(data[col].median(), inplace=True)
    
    # Remove rows with missing critical data
    data = data.dropna(subset=['countyname', 'stusps', 'fips'])
    
    return data.reset_index(drop=True)

def normalize_fips_codes(data):
    """
    Normalize FIPS codes to 5-digit zero-padded format.
    
    Args:
        data (pd.DataFrame): Rent data with FIPS codes
        
    Returns:
        pd.DataFrame: Data with normalized FIPS codes
    """
    # Handle the FIPS column - it might be float, int, or string
    def fix_fips(val):
        try:
            # Remove any decimals if float
            if pd.isna(val):
                return ''
            # Convert to int first to remove decimals, then to string
            val_str = str(int(float(val)))
            # Pad with zeros to 5 digits
            return val_str.zfill(5)
        except:
            # If all else fails, just convert to string and pad
            return str(val).zfill(5)
    
    data['fips'] = data['fips'].apply(fix_fips)
    
    # Also normalize state FIPS if it exists
    if 'state' in data.columns:
        data['state'] = data['state'].apply(lambda x: str(int(float(x))).zfill(2) if pd.notna(x) else '')
    
    return data

# Initialize data on module load
print("\n" + "="*60)
print("Initializing Crossing Counties Data Processing")
print("="*60)
rent_data = load_and_process_data()

if rent_data is not None and not rent_data.empty:
    print(f"✓ System ready with {len(rent_data)} counties")
    print(f"✓ States available: {rent_data['stusps'].nunique()}")
else:
    print("✗ FAILED to load data - application will not work")
print("="*60 + "\n")

def get_States():
    """
    Get list of unique state codes from rent data.
    
    Returns:
        list: Sorted list of state codes (USPS format)
    """
    if rent_data is not None and not rent_data.empty:
        return sorted(rent_data['stusps'].unique().astype(str))
    return []

def get_Counties(state):
    """
    Get list of counties for a given state.
    
    Args:
        state (str): Two-letter state code
        
    Returns:
        list: Sorted list of county names
    """
    if rent_data is not None and not rent_data.empty:
        counties = rent_data[rent_data['stusps'] == state]['countyname'].astype(str)
        return sorted(counties.unique())
    return []

def get_County_Rent(fips, rooms):
    """
    Retrieve fair market rent for a county and number of rooms.
    
    Args:
        fips (str): Five-digit FIPS code
        rooms (int): Number of bedrooms (1-4)
        
    Returns:
        float: Fair market rent value
    """
    try:
        if rent_data is None or rent_data.empty:
            return 0
        county_info = rent_data[rent_data['fips'].astype(str) == str(fips)]
        if county_info.empty:
            return 0
        rent_value = county_info[f'fmr_{rooms}'].iloc[0]
        return float(rent_value) if pd.notna(rent_value) else 0
    except Exception as e:
        print(f"Error getting rent for FIPS {fips}: {e}")
        return 0

def get_County_FIPS(county_name, state):
    """
    Retrieve FIPS code for a given county and state.
    
    Args:
        county_name (str): Name of the county
        state (str): Two-letter state code
        
    Returns:
        str: Five-digit FIPS code, or empty string if not found
    """
    try:
        if rent_data is None or rent_data.empty:
            return ''
        county = rent_data[(rent_data['countyname'] == county_name) & 
                          (rent_data['stusps'] == state)]
        if county.empty:
            return ''
        return str(county.iloc[0]['fips'])
    except Exception as e:
        print(f"Error getting FIPS for {county_name}, {state}: {e}")
        return ''

def get_County_Name(fips):
    """
    Retrieve county name from FIPS code.
    
    Args:
        fips (str): Five-digit FIPS code
        
    Returns:
        str: County name, or 'Unknown' if not found
    """
    try:
        if rent_data is None or rent_data.empty:
            return 'Unknown'
        county = rent_data[rent_data['fips'].astype(str) == str(fips)]
        if county.empty:
            return 'Unknown'
        return str(county.iloc[0]['countyname'])
    except Exception as e:
        print(f"Error getting county name for FIPS {fips}: {e}")
        return 'Unknown'

def get_State(fips):
    """
    Get state code from FIPS code.
    
    Args:
        fips (str): Five-digit FIPS code
        
    Returns:
        str: Two-letter state code
    """
    try:
        if rent_data is None or rent_data.empty:
            return ''
        county = rent_data[rent_data['fips'].astype(str) == str(fips)]
        if county.empty:
            return ''
        return str(county.iloc[0]['stusps'])
    except Exception as e:
        print(f"Error getting state for FIPS {fips}: {e}")
        return ''

def get_State_Income_Data(fips):
    """
    Load and process income data for the state containing the given FIPS code.
    
    Args:
        fips (str): Five-digit FIPS code
        
    Returns:
        pd.DataFrame: Processed income data for the state
    """
    try:
        state = get_State(fips)
        if not state:
            return pd.DataFrame()
        
        # Find the income data file
        income_file = get_data_file_path('Income_Data.xlsx')
        
        if income_file is None:
            # Only show error once
            if not hasattr(get_State_Income_Data, 'error_shown'):
                print("\nWARNING: Income_Data.xlsx not found - income visualizations will be unavailable")
                print("Download from: https://home.treasury.gov/system/files/136/SLFRF-LMI-tool.xlsx\n")
                get_State_Income_Data.error_shown = True
            return pd.DataFrame()
        
        # Load income data for the specific state sheet
        income_data = pd.read_excel(income_file, sheet_name=state, skiprows=1)
        
        # Data cleaning and normalization
        income_data = income_data.drop(0).reset_index(drop=True)
        
        # Drop unnecessary columns (keep only first 12)
        drop_cols = income_data.columns[12:]
        income_data = income_data.drop(columns=drop_cols)
        
        # Standardize column names
        col_names = ['Locality', 'State', 'HUD_Area', 'fips', 
                     '1', '2', '3', '4', '5', '6', '7', '8']
        income_data.columns = col_names
        
        # Normalize FIPS codes
        income_data['fips'] = income_data['fips'].apply(
            lambda x: str(int(float(x))).zfill(5) if pd.notna(x) else ''
        )
        
        return income_data
        
    except ValueError as e:
        # Sheet doesn't exist - this is OK, just return empty
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading income data for {fips}: {e}")
        return pd.DataFrame()

def get_County_Income(fips):
    """
    Retrieve income data for a specific county.
    
    Args:
        fips (str): Five-digit FIPS code
        
    Returns:
        pd.DataFrame: Income data for the county
    """
    try:
        income_data = get_State_Income_Data(fips)
        if income_data.empty:
            return pd.DataFrame()
        county_income = income_data[income_data['fips'].astype(str) == str(fips)]
        return county_income
    except Exception as e:
        print(f"Error getting income for FIPS {fips}: {e}")
        return pd.DataFrame()

def graph_Income_By_House_Size(fips1, fips2):
    """
    Create scatter plot comparing income levels by household size for two counties.
    
    Args:
        fips1 (str): FIPS code for first county
        fips2 (str): FIPS code for second county
    """
    try:
        household_size = [1, 2, 3, 4, 5, 6, 7, 8]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        plt.title('Income Levels by County per Household Size', fontsize=14, fontweight='bold')
        plt.xlabel('Number of Members in Household', fontsize=12)
        plt.ylabel('40% of Median Annual Income (USD)', fontsize=12)
        
        # Get income data for both counties
        income1 = get_County_Income(fips1)
        income2 = get_County_Income(fips2)
        
        plots_made = 0
        
        # Plot data if available
        if not income1.empty:
            try:
                income_values1 = income1.iloc[0, 4:12].astype(int)
                ax.scatter(household_size, income_values1, 
                          label=get_County_Name(fips1), s=100, alpha=0.7)
                plots_made += 1
            except:
                pass
        
        if not income2.empty:
            try:
                income_values2 = income2.iloc[0, 4:12].astype(int)
                ax.scatter(household_size, income_values2, 
                          label=get_County_Name(fips2), s=100, alpha=0.7)
                plots_made += 1
            except:
                pass
        
        if plots_made > 0:
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.warning("Income data not available for the selected counties.")
            
    except Exception as e:
        st.error(f"Error generating income graph: {str(e)}")

def get_County_Stats(fips, rooms):
    """
    Generate statistics summary for a county's rental market.
    
    Args:
        fips (str): Five-digit FIPS code
        rooms (int): Number of bedrooms
        
    Returns:
        str: Formatted statistics string
    """
    try:
        if not isinstance(fips, str) or fips == '' or rent_data is None or rent_data.empty:
            return "Please select a valid county to view statistics."
        
        rent = get_County_Rent(fips, rooms)
        if rent == 0:
            return "Rental data not available for this county."
        
        avg = average_rent(rooms)
        if avg == 0:
            return "Unable to calculate average rent."
        
        ratio = round(float(rent) / avg, 2)
        
        result = f'**Fair Market Rent:** ${rent:,.0f} per month\n\n'
        result += f'**Compared to US Average:** {ratio}x\n\n'
        result += f'This county\'s rent is {ratio} times the national average '
        result += f'for a {rooms}-bedroom unit.\n'
        
        return result
        
    except Exception as e:
        return f"Error retrieving statistics: {str(e)}"

def average_rent(rooms):
    """
    Calculate average rent across all US counties for given number of rooms.
    
    Args:
        rooms (int): Number of bedrooms
        
    Returns:
        float: Average rent value
    """
    try:
        if rent_data is None or rent_data.empty:
            return 0
        rent_column = f'fmr_{rooms}'
        if rent_column in rent_data.columns:
            avg = rent_data[rent_column].mean()
            return float(avg) if pd.notna(avg) else 0
        return 0
    except Exception as e:
        print(f"Error calculating average rent: {e}")
        return 0

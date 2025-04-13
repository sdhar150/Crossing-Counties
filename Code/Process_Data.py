import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

rent_data = pd.read_excel('Fair_Market_Rents.xlsx',sheet_name='FY25_FMRs_revised')#import rent data

def get_States():
    return rent_data['stusps'].unique().astype(str)

def get_Counties(state):
    return rent_data[rent_data['stusps'] == state]['countyname'].astype(str)

def fix_Format():
    #The following code fixes some formatting issues when importing data from the sheet
    for row in range(478):
        rent_data.iloc[row,7] = '0' + str(rent_data.iloc[row,7])
        rent_data.iloc[row,1] = '0' + str(rent_data.iloc[row,1])

def get_County_Rent(fips,rooms):
    county_info = rent_data[fips == rent_data['fips'].astype(str)]
    return county_info[str('fmr_'+str(rooms))].iloc[0]

def get_County_FIPS(county_name,state):
    county = rent_data[(rent_data['countyname'] == county_name) & (rent_data['stusps'] == state)]
    return str(county.iloc[0,7])

def get_County_Name(fips):
    county = rent_data[rent_data['fips'].astype(str) == fips]
    return str(county.iloc[0,3])


def get_County_Income(fips):
    income_data = get_State_Income_Data(fips)
    return income_data[income_data['fips'].astype(str) == fips]

def get_State_Income_Data(fips):
    #Finds the usps state code for the fips value
    income_data = pd.read_excel('Income_Data.xlsx',sheet_name=get_State(fips),skiprows=1)#import income data
    income_data = income_data.drop(0)
    income_data = income_data.reset_index(drop=True)

    drop_cols = income_data.columns[12:]
    income_data = income_data.drop(columns=drop_cols)

    income_data = income_data.reset_index(drop=True)
    col_names = 'Locality	State	HUD_Area	fips	' \
    '1    2     3	 4	   5	  6	    7	   8	'
    income_data.columns = col_names.split()
    return income_data

def get_State(fips):
    find_state = rent_data[rent_data['countyname'] == get_County_Name(fips)]['stusps']
    state = str(find_state.iloc[0])
    return state

def graph_Income_By_House_Size(fips1,fips2):
    household_size = [1,2,3,4,5,6,7,8]
    fig, ax = plt.subplots()
    plt.title('Income levels by county per household size')
    plt.xlabel('Number of members in a household')
    plt.ylabel('40 percent of Median annual income (in USD)')
    ax.scatter(household_size,get_County_Income(fips1).iloc[0,4:].astype(int),label=get_County_Name(fips1))
    ax.scatter(household_size,get_County_Income(fips2).iloc[0,4:].astype(int),label=get_County_Name(fips2))
    ax.legend()
    st.pyplot(fig)

def get_County_Stats(fips,rooms):
    if(isinstance(fips,str) & (fips != '')):
        result = ''
        result += 'For your apartment, expect a fair market rent of $' + str(get_County_Rent(fips,rooms)) + ' per month\n'
        result += '\nRent in this county should be: ' +  str(round(float(get_County_Rent(fips,rooms))/average_rent(rooms),2))   
        result += ' times the average rent across the US for a house with '  + str(rooms) + ' rooms \n'
        return result

def average_rent(rooms):
    average_US_rent = sum(rent_data[str('fmr_'+str(rooms))])/len(rent_data)
    return average_US_rent

fix_Format()
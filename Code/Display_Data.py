import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Process_Data as processor

# Configure page settings
st.set_page_config(
    page_title="Crossing Counties - County Comparison Tool",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏘️ Crossing Counties</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Compare housing costs and income levels across US counties to find your ideal location</div>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("About This Tool")
    st.write("""
    This interactive application helps you compare:
    - **Fair Market Rent** across counties
    - **Income levels** by household size
    - **Cost of living** relative to national averages
    
    Data sources:
    - HUD Fair Market Rents (2025)
    - US Treasury Median Income Data
    """)
    
    st.header("How to Use")
    st.write("""
    1. Select states and counties for comparison
    2. Choose number of bedrooms
    3. View side-by-side statistics
    4. Analyze income trends by household size
    """)

# Check if data is loaded
if processor.rent_data is None or processor.rent_data.empty:
    st.error("⚠️ Data files not found. Please ensure Fair_Market_Rents.xlsx and Income_Data.xlsx are in the Code/ directory.")
    st.info("📥 Download instructions are available in the README.md file.")
    st.stop()

# Main comparison interface
st.markdown("---")
st.subheader("County Comparison")

# Create two columns for side-by-side comparison
county1, county2 = st.columns(2)

# County 1 Selection
with county1:
    st.markdown("### 📍 County 1")
    state_c1 = st.selectbox(
        'State',
        processor.get_States(),
        key='state_1',
        help="Select the state for your first county"
    )
    
    county_c1 = st.selectbox(
        'County',
        processor.get_Counties(state_c1),
        key='county_1',
        help="Select the county to analyze"
    )
    
    rooms_c1 = st.slider(
        'Number of Bedrooms',
        min_value=1,
        max_value=4,
        value=2,
        step=1,
        key='rooms_1',
        help="Select apartment size (bedrooms)"
    )
    
    # Get and display statistics
    st.markdown("#### 📊 Statistics")
    fips_c1 = processor.get_County_FIPS(county_c1, state_c1)
    stats_c1 = processor.get_County_Stats(fips_c1, rooms_c1)
    st.markdown(f'<div class="stat-box">{stats_c1}</div>', unsafe_allow_html=True)

# County 2 Selection
with county2:
    st.markdown("### 📍 County 2")
    state_c2 = st.selectbox(
        'State',
        processor.get_States(),
        key='state_2',
        help="Select the state for your second county"
    )
    
    county_c2 = st.selectbox(
        'County',
        processor.get_Counties(state_c2),
        key='county_2',
        help="Select the county to analyze"
    )
    
    rooms_c2 = st.slider(
        'Number of Bedrooms',
        min_value=1,
        max_value=4,
        value=2,
        step=1,
        key='rooms_2',
        help="Select apartment size (bedrooms)"
    )
    
    # Get and display statistics
    st.markdown("#### 📊 Statistics")
    fips_c2 = processor.get_County_FIPS(county_c2, state_c2)
    stats_c2 = processor.get_County_Stats(fips_c2, rooms_c2)
    st.markdown(f'<div class="stat-box">{stats_c2}</div>', unsafe_allow_html=True)

# Visualization Section
st.markdown("---")
st.subheader("📈 Visualizations")

# Create tabs for different visualizations
viz_tab1, viz_tab2, viz_tab3 = st.tabs([
    "Income by Household Size",
    "Rent Comparison",
    "Affordability Analysis"
])

with viz_tab1:
    st.markdown("#### Income Levels by Household Size")
    st.write("This chart shows how median income (40% threshold) varies with household size for the selected counties.")
    processor.graph_Income_By_House_Size(fips_c1, fips_c2)

with viz_tab2:
    st.markdown("#### Rent Comparison Across Unit Sizes")
    st.write("Compare fair market rent across different apartment sizes.")
    
    try:
        # Create rent comparison bar chart
        room_sizes = [1, 2, 3, 4]
        rents_c1 = [processor.get_County_Rent(fips_c1, r) for r in room_sizes]
        rents_c2 = [processor.get_County_Rent(fips_c2, r) for r in room_sizes]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(room_sizes))
        width = 0.35
        
        ax.bar(x - width/2, rents_c1, width, label=processor.get_County_Name(fips_c1), alpha=0.8)
        ax.bar(x + width/2, rents_c2, width, label=processor.get_County_Name(fips_c2), alpha=0.8)
        
        ax.set_xlabel('Number of Bedrooms', fontsize=12)
        ax.set_ylabel('Fair Market Rent (USD)', fontsize=12)
        ax.set_title('Rent Comparison by Unit Size', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([f'{r} BR' for r in room_sizes])
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Error generating rent comparison: {str(e)}")

with viz_tab3:
    st.markdown("#### Affordability Index")
    st.write("Shows rent as a percentage of median income for a 4-person household.")
    
    try:
        # Calculate affordability metrics
        income_data_c1 = processor.get_County_Income(fips_c1)
        income_data_c2 = processor.get_County_Income(fips_c2)
        
        if not income_data_c1.empty and not income_data_c2.empty:
            # Use 4-person household income (column index 7)
            income_c1_annual = income_data_c1.iloc[0, 7]
            income_c2_annual = income_data_c2.iloc[0, 7]
            
            # Calculate monthly income (40% of median / 12 months)
            income_c1_monthly = float(income_c1_annual) / 12
            income_c2_monthly = float(income_c2_annual) / 12
            
            # Get rent for 2-bedroom units
            rent_c1 = processor.get_County_Rent(fips_c1, 2)
            rent_c2 = processor.get_County_Rent(fips_c2, 2)
            
            # Calculate affordability percentage
            afford_c1 = (rent_c1 / income_c1_monthly) * 100 if income_c1_monthly > 0 else 0
            afford_c2 = (rent_c2 / income_c2_monthly) * 100 if income_c2_monthly > 0 else 0
            
            # Create visualization
            fig, ax = plt.subplots(figsize=(10, 6))
            counties = [processor.get_County_Name(fips_c1), processor.get_County_Name(fips_c2)]
            affordability = [afford_c1, afford_c2]
            
            colors = ['#ff6b6b' if a > 30 else '#4ecdc4' for a in affordability]
            bars = ax.barh(counties, affordability, color=colors, alpha=0.7)
            
            # Add reference line at 30% (recommended threshold)
            ax.axvline(x=30, color='red', linestyle='--', linewidth=2, alpha=0.5, label='30% Threshold')
            
            ax.set_xlabel('Rent as % of Monthly Income', fontsize=12)
            ax.set_title('Housing Affordability Index\n(2BR Rent vs 4-Person Household Income)', 
                        fontsize=14, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add value labels
            for i, (bar, value) in enumerate(zip(bars, affordability)):
                ax.text(value + 1, i, f'{value:.1f}%', va='center', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
            
            st.info("💡 **Note:** Housing costs above 30% of income are generally considered unaffordable.")
        else:
            st.warning("Income data not available for affordability analysis.")
            
    except Exception as e:
        st.error(f"Error generating affordability analysis: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
    Data Sources: U.S. Department of Housing and Urban Development (HUD) | U.S. Department of Treasury<br>
    Built with Streamlit, Pandas, and Matplotlib | Created by Soham Dhar
    </div>
    """, unsafe_allow_html=True)

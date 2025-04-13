import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Process_Data as processor 

st.title('Crossing Counties')
st.write('Considering moving? We can help you learn more about exciting new counties where you may want to settle down!')

county1,county2 = st.columns(2)

state_c1 = county1.selectbox('State',processor.get_States(),key=100)
county_c1 = county1.selectbox('County',processor.get_Counties(state_c1),key=1000)
rooms_c1 = county1.slider('Rooms', min_value=1, max_value=4, value=2, step=1)    
county1.write(processor.get_County_Stats(processor.get_County_FIPS(county_c1,state_c1),rooms_c1))

state_c2 = county2.selectbox('State',processor.get_States(),key=50)
county_c2 = county2.selectbox('County',processor.get_Counties(state_c2),key=500)
rooms_c2 = county2.slider('Rooms', min_value=1, max_value=4, value=2, step=1,key=10)    
county2.write(processor.get_County_Stats(processor.get_County_FIPS(county_c2,state_c2),rooms_c2))

processor.graph_Income_By_House_Size(processor.get_County_FIPS(county_c1,state_c1),processor.get_County_FIPS(county_c2,state_c2))
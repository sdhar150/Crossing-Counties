import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import Process_Data as processor 

st.title('Crossing Counties')
st.write('Considering moving? We can help you learn more about exciting new counties where you may want to settle down!')

fips = st.text_input('Enter County\'s FIPS code')
rooms = st.slider('Rooms', min_value=1, max_value=4, value=2, step=1)    

st.write(processor.get_County_Stats(fips,rooms))
st.stop()

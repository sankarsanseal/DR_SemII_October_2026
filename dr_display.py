
import streamlit as st
import pandas as pd
import os

path_to_the_excel_file = os.path.abspath(__file__)

path_to_excel_file = os.path.join(os.path.dirname(path_to_the_excel_file),"dr_semII_oct_2026.xlsx") 

if os.path.exists(path_to_excel_file):
    dr_df = pd.read_excel(path_to_excel_file)
    st.header(dr_df)
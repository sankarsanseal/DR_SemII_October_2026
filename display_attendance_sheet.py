import streamlit as st
import pandas as pd
import os

path_to_the_dir = os.path.dirname(os.path.abspath(__file__))

path_to_excel_file = os.path.join(path_to_the_dir,"subject_wise_sorted_dr_semII_oct_2026.xlsx")


st.selectbox("Select the Room", [101, 103, 109, 110, 111, 201, 204])



import streamlit as st
import pandas as pd
import os

path_to_the_dir = os.path.dirname(os.path.abspath(__file__))

path_to_excel_file = os.path.join(path_to_the_dir,"dr_semII_oct_2026.xlsx") 


if os.path.exists(path_to_excel_file):

    dr_df = pd.read_excel(path_to_excel_file, sheet_name = "Applicant Data", engine = "openpyxl")
    st.header("DR of Sem 2026")
    st.dataframe(dr_df)

    st.dataframe(dr_df.columns)
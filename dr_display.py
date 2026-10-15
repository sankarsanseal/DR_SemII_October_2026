import streamlit as st
import pandas as pd

st.title("DR of Sem 2026")

@st.cache_data
dr_df = pd.read_excel("dr_semII_oct_2026.xlsx")


st.print(dr_df)
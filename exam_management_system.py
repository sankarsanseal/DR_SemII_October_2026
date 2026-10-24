import streamlit as st
import pandas as pd

st.set_page_config(page_title = "Examination Committee IV", layout = "wide")

exam_details = pd.read_csv(
                            "exam_details.txt", 
                            header = 0,
                            
                            )



st.session_state.exam_sem = exam_details.iloc[0]["semester"]
st.session_state.exam_month = exam_details.iloc[0]["month"]
st.session_state.exam_year = exam_details.iloc[0]["exam_year"]



st.sidebar.title("The University of Burdwan")
st.sidebar.header("Examination of Semester {0}".format(st.session_state.exam_sem))
st.sidebar.header("Examination Month: {0}".format(st.session_state.exam_month))
st.sidebar.header("Examination Year: {0}".format(st.session_state.exam_year))


step_01_01 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/01_Uploading_And_Sorting_Descriptive_Roll.py", 
        title = "01. Upload the Descriptive Roll (DR)",)

step_01_02 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/02_Checking_Subjects_Distribution.py", 
                     title = "02. Checking Subjects' Distribution")

landing_page = st.navigation( pages = {
"Step 01" : [step_01_01, step_01_02],
},
expanded = True,
position = "sidebar"

)

landing_page.run()


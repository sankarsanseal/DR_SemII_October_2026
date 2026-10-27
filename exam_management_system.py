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


step_00_01 = st.Page(page = "00_Building_Details_And_Merging_All_DR/01_Room_Details_Insertion.py",
                        title = "01. Insert Room Details for Examination",
                     )


step_01_01 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/01_Uploading_And_Sorting_Descriptive_Roll.py", 
        title = "01. Upload the Descriptive Roll (DR)",)

step_01_02 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/02_Checking_Subjects_Distribution.py", 
                     title = "02. Checking Subjects' Distribution")

step_01_03 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/03_Setting_Examination_Date_And_Time.py",
                     title = "03. Insert the Exam Date and Timing")
# step_01_04 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/04_serial.py", title = "serial")

landing_page = st.navigation( pages = {

                                        "Step 00" : [step_00_01, ],

                                        "Step 01" : [
                                                        step_01_01, 
                                                        step_01_02,
                                                        step_01_03,
                # step_01_04,
                                                        ],
},
expanded = True,
position = "sidebar"

)

landing_page.run()


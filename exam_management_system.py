import streamlit as st
import pandas as pd
from psycopg import errors as sql_errors
from sqlalchemy import text as sqltext
from streamlit.connections import SQLConnection


conn_sql = st.connection( 
                                name = "neon",
                                type = SQLConnection,
                                ttl = 1, 

                        )


if conn_sql:
    try:
                exam_details_create_sql = sqltext(
                """
                        CREATE TABLE IF NOT EXISTS exam_details
                                (
                                        examination_type VARCHAR(10),
                                        examination_semester VARCHAR(10),
                                        examination_month VARCHAR(20),
                                        examination_year VARCHAR(10),
                                        PRIMARY KEY (
                                                        examination_type, 
                                                        examination_semester, 
                                                        examination_month, 
                                                        examination_year
                                                )
                                )
                """
                                        )

                with conn_sql.session as exam_table_creation_session:
                    exam_table_creation_session.execute( 
                                                                statement = exam_details_create_sql 
                                                        )
                    exam_table_creation_session.commit()

    except sql_errors.DatabaseError as de:
              st.sidebar.error(de)

    try:

        exam_details_fetch_query = sqltext(
            """
                SELECT 
                        examination_type,
                        examination_semester,
                        examination_month,
                        examination_year 
                FROM    
                        exam_details
             """
        )

        with conn_sql.session as exam_session:
            exam_details_resultset = exam_session.execute( 
                                                        statement = exam_details_fetch_query,
                                                        )
            st.session_state.exam_type = ""
            st.session_state.exam_sem = ""
            st.session_state.exam_month = ""
            st.session_state.exam_year = ""
            
            if exam_details_resultset.rowcount == 1:    
                exam_details_row = exam_details_resultset.fetchone()

                st.session_state.exam_type = exam_details_row[0] 
                st.session_state.exam_sem = exam_details_row[1]
                st.session_state.exam_month = exam_details_row[2]
                st.session_state.exam_year = exam_details_row[3]


    except sql_errors.UndefinedTable as de:
        st.sidebar.error(
                                body = f"Table Does not exist {de}",
                                title = "Exam_Details"         
                        )

        
# exam_details = pd.read_csv(
#                             "exam_details.txt", 
#                             header = 0,
                            
#                             )



# st.session_state.exam_sem = exam_details.iloc[0]["semester"]
# st.session_state.exam_month = exam_details.iloc[0]["month"]
# st.session_state.exam_year = exam_details.iloc[0]["exam_year"]


st.set_page_config(page_title = f"Examination Committee {st.session_state.exam_sem}", layout = "wide")

st.sidebar.title("The University of Burdwan")
st.sidebar.header("{} Examination".format(st.session_state.exam_type))
st.sidebar.header("Examination of Semester {0}".format(st.session_state.exam_sem))
st.sidebar.header("Examination Month: {0}".format(st.session_state.exam_month))
st.sidebar.header("Examination Year: {0}".format(st.session_state.exam_year))

step_00_00 = st.Page( 
                        page = "00_Building_Details_And_Merging_All_DR/00_Exam_Details_Insertion.py",
                        title = "00. Exam Details Insertion")

step_00_01 = st.Page(page = "00_Building_Details_And_Merging_All_DR/01_Room_Details_Insertion.py",
                        title = "01. Insert Room Details for Examination",
                     )


step_01_01 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/01_Uploading_And_Sorting_Descriptive_Roll.py", 
        title = "01. Upload the Descriptive Roll (DR)",)

step_01_02 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/02_Checking_Subjects_Distribution.py", 
                     title = "02. Checking Subjects' Distribution")

step_01_03 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/03_Setting_Examination_Date_And_Time.py",
                     title = "03. Insert the Exam Date and Timing")

step_01_04 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/04_Assign_Room_No_To_Students.py", 
                     title = "04. Assigning Room No to Students"
                     )

step_01_05 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/05_RoomWise_Student_Distribution.py",
                     title = "05. Checking Room-Wise Student-Subject Distribution")

step_01_06 = st.Page(page = "01_Uploading_And_Sorting_Descriptive_Roll/06_SubjectWise_Student_Distribution.py",
                     title = "06. Checking Subject-wise Student-Room Distribution")

landing_page = st.navigation( pages = {

                                        "Step 00" : [
                                                        step_00_00, 
                                                        step_00_01, 
                                                     ],

                                        "Step 01" : [
                                                        step_01_01, 
                                                        step_01_02,
                                                        step_01_03,
                                                        step_01_04,
                                                        step_01_05,
                                                        step_01_06,
                # step_01_04,
                                                        ],
},
expanded = True,
position = "sidebar"

)

landing_page.run()


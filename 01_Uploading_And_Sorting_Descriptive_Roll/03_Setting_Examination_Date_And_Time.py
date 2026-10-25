import streamlit as st

from sqlalchemy import text as sqltext
from psycopg import errors as sql_errors


exam_date_time_update_container = st.container(
                                                border =  True,
                                                key = "Exam_Date_Update_Container"
                                                )

col1, col2, col3 = exam_date_time_update_container.columns(3, 
                                                           gap = "xxsmall",
                                                           )

st.session_state.exam_code_list = []

exam_code_selection_box = col1.empty()
try:
    conn_sql = st.connection(
                            name = "neon", 
                            type =  "sql", 
                            ttl = 1
                        )

except sql_errors.ConnectionError as de:
    exam_date_time_update_container.error(de)

if conn_sql:

    with conn_sql.session as exam_date_session:
        try:
            exam_code_query = sqltext("""SELECT exam_course_code FROM exam_dates ORDER BY exam_course_code""") 

            exam_code_resultset = exam_date_session.execute(exam_code_query)



            if exam_code_resultset.rowcount > 0:
                st.session_state.exam_code_list = [ row[0] for row in exam_code_resultset ]
                exam_code_selection_box = col1.selectbox(
                                            label = "Select the exam course code",
                                            options = st.session_state.exam_code_list,
                                            index = None,
                                            key = "Exam_Code_Selection_Box_Updated", 
                                        )

            
        except sql_errors.DatabaseError as de:
            exam_date_time_update_container.error(de)


        col1.text_input( label = f"Selected Exam Code: {exam_code_selection_box}", 
                        value = f"{exam_code_selection_box}",
                        disabled = True,
                        key = f"Selected_Exam_Code_Text_Field_{exam_code_selection_box}"
    
                        )



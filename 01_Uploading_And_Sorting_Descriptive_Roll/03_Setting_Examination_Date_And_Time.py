import streamlit as st

from sqlalchemy import text as sqltext
from psycopg import errors as sql_errors


exam_date_time_update_container = st.container(
                                                border =  True,
                                                key = "Exam_Date_Update_Container"
                                                )
exam_date_time_update_container.title("Exam Date and Start Time Update")

exam_date_time_update_form = exam_date_time_update_container.form(
                                                                    key = "Exam_Date_Time_Update_Form",
                                                                    )


col1, col2, col3 = exam_date_time_update_form.columns(3, 
                                                           gap = "xxsmall",
                                                           )



st.session_state.exam_code_list = []

# exam_code_selection_box = col1.empty()
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
            exam_code_query = sqltext(
                                        """
                                            SELECT exam_course_code 
                                            FROM exam_dates 
                                            ORDER BY exam_course_code
                                        """) 

            exam_code_resultset = exam_date_session.execute(exam_code_query)


            if exam_code_resultset.rowcount > 0:
                st.session_state.exam_code_list = [ row[0] for row in exam_code_resultset ]
                exam_code_selection_box = col1.selectbox(
                                            label = "Select the exam course code",
                                            options = st.session_state.exam_code_list,
                                            index = None,
                                            key = f"Exam_Code_Selection_Box_Updated",
                                        )

            
        except sql_errors.DatabaseError as de:
            exam_date_time_update_container.error(de)


        col1.text_input( 
                        label = f"Selected Exam Code", 
                        value = f"{exam_code_selection_box}",
                        disabled = True,
                        key = f"Selected_Exam_Code_Text_Field_{exam_code_selection_box}"
                        )


        try:

            date_time_query = sqltext(
                                    """
                                    SELECT exam_course_code, exam_date, exam_start_time
                                    FROM exam_dates
                                    WHERE exam_course_code = :exam_code
                                    """
                                    )

            exam_date_time_row = exam_date_session.execute( 
                                                            statement = date_time_query, 
                                                            params = {"exam_code" : exam_code_selection_box},
                                                            )
            if exam_date_time_row.rowcount == 1:
                selected_row = exam_date_time_row.fetchone()
                col2.date_input(
                                label = f"Present Exam Date", 
                                value = selected_row[1], 
                                key = f"Present_Exam_Date_{selected_row[0]}",
                                # placeholder = selected_row[1],
                                disabled = True  
                                )
                exam_date = col2.date_input(    
                                label = f"New Exam Date", 
                                value = selected_row[1], 
                                key = f"New_Exam_Date_{exam_code_selection_box}",
                                # placeholder = selected_row[1],
                                format = "DD/MM/YYYY",
                                )

                col3.time_input(
                                    label = f"Present Exam Start Time",
                                    value = selected_row[2],
                                    key = f"Present_Exam_Start_Time_{selected_row[0]}",
                                    disabled = True,
                                    format = "12h"
                                    )
                    
                exam_start_time = col3.time_input(
                                    label = f"New Exam Start Time",
                                    value = selected_row[2],
                                    key = f"New_Exam_Start_Time_{selected_row[0]}",
                                    # disabled = True,
                                    format = "12h",
                                    )

                exam_date_time_update_form_submit = exam_date_time_update_form.form_submit_button(
                                                                                label = 
                                                                                "Update the Date and Time of the Examnimation", 
                                                                                key = "Exam_Date_Time_UpdateForm_Submit_Button",
                                                                                width = "stretch",
                                                                                )


                try:

                    exam_date_time_update_query = sqltext(
                                                            """
                                                            UPDATE exam_dates
                                                            SET exam_date = :exam_date,
                                                            exam_start_time = :exam_start_time
                                                            WHERE exam_course_code = :exam_course_code
                                                            """
                                                            )
                    if exam_date is not None and exam_start_time is not None:
                        update_status = exam_date_session.execute( 
                                                                statement = exam_date_time_update_query,
                                                                params = { "exam_date" : exam_date.strftime("%Y-%m-%d"),
                                                                          "exam_start_time" : exam_start_time.strftime("%H:%M:%S"),
                                                                          "exam_course_code" : exam_code_selection_box

                                                                }
                                                            )

                        exam_date_session.commit()

                        exam_date_time_update_container.success(    "The update of Exam Date and"
                                                                f" Start Time is successful for {exam_code_selection_box}"
                                                                f" with status code {update_status}.")

                except sql_errors.IntegrityError as ie:
                    exam_date_time_update_container.error(ie)



        except Exception as de:
            exam_date_time_update_container.error(de)

        


        try:

            all_exam_date_time_query = (
                                                """
                                                SELECT * FROM exam_dates
                                                """
            )
            all_exam_date_time_df = conn_sql.query(all_exam_date_time_query, ttl = 10)

            exam_date_time_update_container.dataframe( data = all_exam_date_time_df, height = "content" )

        except sql_errors.DatabaseError as de:
            exam_date_time_update_container.error(de)
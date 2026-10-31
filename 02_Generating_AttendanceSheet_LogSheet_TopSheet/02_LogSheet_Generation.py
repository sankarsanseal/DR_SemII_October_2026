import streamlit as st
import pandas as pd

from sqlalchemy import text as sqltext
from streamlit.connections import SQLConnection





logsheet_container = st.container(
    border = True,
    key = "LogSheet_As_PDF_Generating_Container"
)

col1, col2, col3 = logsheet_container.columns(
    spec = [1,1,1],
    gap = "xxsmall",
)

logsheet_form = logsheet_container.form(
    key = "Logsheet_Generating_Form",
    border = False,

)



selected_date = col1.date_input(
    label = "Select the Date of Examination",
    key = "Exam_Date_Input",
)




logsheet_form_submission_button = logsheet_form.form_submit_button(
    label = "Generate the Log Sheet",
    key = "Logsheet_Generation_Form_Submission_Button",
    width = "stretch",
)


conn_sql = st.connection( 
    name = "neon",
    type = SQLConnection,
    ttl = 1,
    )


if conn_sql:


    if selected_date is not None:

        with conn_sql.session as sql_session:


            time_slots_sql = sqltext(
                """
                SELECT DISTINCT TO_CHAR(exam_start_time,'HH12:MI AM')
                FROM exam_dates
                WHERE exam_date = :exam_date
                """
            )

            time_slots_resultset = sql_session.execute(
                statement = time_slots_sql,
                params = {
                    "exam_date" : selected_date.strftime(
                        format="%Y-%m-%d"
                        )
                }
            )

            
            selected_time = col2.selectbox(
                label = "Select the Start Time of the Examination",
                options = [row[0] for row in time_slots_resultset.fetchall()],
                index = None,
                key = "Exam_Start_Selection_Box",
            )


            if selected_time is not None:

                room_no_sql = sqltext(
                                    """
                                    SELECT concat_ws('-', building_name, room_no, floor_no)
                                    FROM room_details
                                    ORDER BY building_name, room_no, floor_no
                                    """
                                        )


                with conn_sql.session as room_session:

                    room_no_resultset =  room_session.execute(
                        statement = room_no_sql,

                    )

                    selected_room = col3.selectbox(
                        label = "Select the Room No.",
                        options = [row[0] for row in room_no_resultset.fetchall()],
                        index = None,
                        key = "LogSheet_Room_Selection",
                    )                



    if logsheet_form_submission_button and (selected_date is not None 
                                            and selected_time is not None 
                                            and selected_room is not None):

        room_students_list_sql = sqltext(
                                            """
                                            SELECT course_code, nep_program, exam_category, roll_no
                                            FROM all_students_details as S, exam_dates as E
                                            WHERE S.course_code = E.exam_course_code AND
                                            S.room_no = :room_no AND
                                            S.building_name = :building_name AND
                                            E.exam_date = :selected_date AND
                                            E.exam_start_time = :selected_start_time
                                            ORDER BY course_code, nep_program, exam_category, roll_no
                                            """
                                         )

        with conn_sql.session as session:

            room_student_list_resultset = session.execute(
                statement = room_students_list_sql,
                params = {
                    "room_no" : selected_room.split("-")[1],
                    "building_name" : selected_room.split("-")[0],
                    "selected_date" : selected_date.strftime('%Y-%m-%d'),
                    "selected_start_time" : selected_time,
                },
            )

            previous_course_code = ""
            previous_nep_program = ""
            previous_exam_category = ""
            previous_roll_no_prefix = ""

            group_header_list = []
            for row in room_student_list_resultset.fetchall():

                if (previous_course_code != row[0]
                    or previous_nep_program !=row[1][:3]
                    or previous_exam_category != row[2]
                    or previous_roll_no_prefix != row[-1][:8] 
                    ):

                    if len(group_header_list) > 0:
                        st.write(", ".join(group_header_list))
                        st.write("=", len(group_header_list))
                        group_header_list = []
                    group_header_list.append(row[-1][-4:])
                    st.write(row[0], row[1][:3], row[2], row[-1][:8], )
                else:
                    group_header_list.append(row[-1][-4:])

                previous_course_code = row[0]
                previous_nep_program = row[1][:3]
                previous_exam_category = row[2]
                previous_roll_no_prefix = row[-1][:8]
            else:
                st.write(", ".join(group_header_list))
                st.write("=", len(group_header_list))
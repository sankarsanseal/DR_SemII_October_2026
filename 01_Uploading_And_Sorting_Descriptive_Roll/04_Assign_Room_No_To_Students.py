import streamlit as st
import pandas as pd
from sqlalchemy import text as sqltext

from psycopg import errors as sql_errors


conn_sql = st.connection(name = "neon", type = "sql", ttl = 1)

update_container = st.container(border = True)


col1, col2, col3, col4 = update_container.columns(
    spec = [1, 1, 1, 5],
    gap = "xxsmall",
)

update_form = col4.form(
    key = "Room_No_Assignment_To_Students",
    enter_to_submit = False,
) 

col4_1, col4_2, col4_3, col4_4, col4_5 = update_form.columns(
    spec = [1, 2, 2, 1, 1],
    gap = "xxsmall",
    )

if conn_sql:

    all_course_code_list_sql =sqltext(
        """
        SELECT DISTINCT exam_course_code
        FROM exam_dates
        ORDER BY exam_course_code
        """
    )

    course_code_list = []

    with conn_sql.session as sql_session:

        all_course_code_resultset = sql_session.execute(all_course_code_list_sql)

        course_code_list = [ row[0] for row in all_course_code_resultset.fetchall() ]


    selected_course_code = col1.selectbox(
        label = "Course Code",
        options = course_code_list,
        index = None,
        placeholder = "Select one code",
    ) 

    if selected_course_code is not None:

        college_code_list = []

        college_code_list_sql = sqltext(
                                        """
                                        SELECT DISTINCT college_code
                                        FROM all_students_details
                                        WHERE course_code = :course_code
                                        ORDER BY college_code
                                        """
                                        )
        with conn_sql.session as sql_session:

            college_code_list_resultset = sql_session.execute(
                                            statement = college_code_list_sql,
                                            params = {
                                                "course_code" : selected_course_code,
                                            },
                                    )

            college_code_list = [row[0] for row in college_code_list_resultset.fetchall()]
            
            selected_college_code = col2.selectbox(
                label = "Select College",
                options = college_code_list,
                index = None,
                key = "College_Code_Selection_Box",
                placeholder = "40X",
                ) 

            

    if selected_course_code is not None and selected_college_code is not None:

        nep_program_list = []

        nep_program_list_sql = sqltext(
            """
            SELECT DISTINCT nep_program
            FROM all_students_details
            WHERE college_code = :college_code 
            AND course_code = :course_code
            ORDER BY nep_program
            """
        )

        with conn_sql.session as sql_session:
            selected_nep_program_resultset = sql_session.execute(nep_program_list_sql,
                                                       params = {
                                                            "college_code" : selected_college_code,
                                                            "course_code" : selected_course_code,
                                                       },
                                                       )

            nep_program_list = [row[0] for row in selected_nep_program_resultset.fetchall()]

        selected_nep_program = col3.selectbox(
            label = "NEP Program",
            options = nep_program_list,
            index = None,
            key = "NEP_Program_For_Students_Assigned",
            placeholder = "4yr/3yr",
        )



    all_room_no_list = []
    all_building_list = []
    all_floor_no_list = []

    all_room_list_sql =  sqltext(
                                """
                                SELECT DISTINCT room_no, building_name, floor_no
                                FROM room_details
                                ORDER BY room_no, building_name,floor_no
                                """
                                )

    with conn_sql.session as sql_session:

        room_details_resultset = sql_session.execute(
            statement = all_room_list_sql,
        )

        for row in room_details_resultset.fetchall():

            all_room_no_list.append(row[0])
            all_building_list.append(row[1])
            all_floor_no_list.append(row[2])

    
    selected_room = col4_1.selectbox(
        label = "Room No",
        options = pd.Series(all_room_no_list).unique(),
        index = None,
        key = "Selected_Room_No_For_Students",
        placeholder = "Room",
    )  


    selected_building = col4_2.selectbox(
        label = "Building Name", 
        options = pd.Series(all_building_list).unique(),
        index = None,
        key = "Selected_Building_No_For_Students",
        placeholder = "Building",
    )

    selected_floor = col4_3.selectbox(
        label = "Selected Floor",
        options = pd.Series(all_floor_no_list).unique(),
        index = None,
        key ="Selected_Floor_for Students",
        placeholder = "Floor",
    )

    selected_starting_serial_no = col4_4.number_input(
        label = "Starting Serial No",
        min_value = 1,
        max_value = 80,
        value = 1,
        step = 1,
        key = "Starting_Serial_No_Input",
        placeholder = "000",
    )

    selected_ending_serial_no = col4_5.number_input(
        label = "Ending Serial No",
        key = "Ending_Serial_No_Input", 
        min_value = 1,
        max_value = 80,
        value = 1,
        step = 1,
        placeholder = "Greated than start serial no"
    )


    serial_no_assigning_form_button = update_form.form_submit_button(
        label = "Submit the Starting and End Serial No.",
        key = "Serial_No_Assigning_Form_Button",
        width = "stretch",
    )


    if serial_no_assigning_form_button:

        if (selected_course_code is not None and 
            selected_college_code is not None and
            selected_nep_program is not None and
            selected_room is not None and
            selected_building is not None and
            selected_floor is not None and
            selected_starting_serial_no is not None and
            selected_ending_serial_no is not None):

            if selected_starting_serial_no < selected_ending_serial_no:

                serial_no_assigning_sql = sqltext(
                    """
                    UPDATE all_students_details
                    SET 
                    room_no = :room_no,
                    building_name = :building_name
                    WHERE 
                    course_code = :course_code AND
                    college_code = :college_code AND
                    nep_program = :nep_program AND
                    serial_no_in_group BETWEEN 
                                        :starting_serial_no AND 
                                        :ending_serial_no 
                    """
                )

                params_dict_list =[
                    {
                        "course_code" : selected_course_code,
                        "college_code":  selected_college_code,
                        "nep_program" : selected_nep_program,
                        "starting_serial_no" : selected_starting_serial_no,
                        "ending_serial_no" : selected_ending_serial_no,
                        "room_no" : selected_room,
                        "building_name" : selected_building
                    },
                ]

                with conn_sql.session as sql_session:

                    try:

                        serial_no_assigning_resultset = sql_session.execute(
                                            statement = serial_no_assigning_sql,
                                            params = params_dict_list,
                        )


                        if serial_no_assigning_resultset.rowcount > 0:

                            sql_session.commit()

                            update_container.success(
                                    body = f"{serial_no_assigning_resultset.rowcount} students of {selected_nep_program}, are updated to room no. {selected_room}.",
                                    title = selected_course_code,
                            )

                    except sql_errors.IntegrityError as ie:

                        update_container.error(
                            body = ie,
                            title = selected_room,
                        ) 


    
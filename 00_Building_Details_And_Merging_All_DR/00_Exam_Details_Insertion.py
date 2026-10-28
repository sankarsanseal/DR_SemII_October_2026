import streamlit as st
import calendar
from psycopg import errors as sql_errors
from streamlit.connections import SQLConnection
from sqlalchemy import text as sqltext

exam_details_enter_container =  st.container( 
                                                border = True, 
                                                gap = "xxsmall", 
                                                key = "Exam_Details_Container"
                                            )

exam_details_submission_form = exam_details_enter_container.form( 
                                                                key = "Exam_Details_Submission_Form",
                                                                )

col1, col2 , col3, col4 = exam_details_submission_form.columns( 
                                                        spec = [1,1.5,1,2],
                                                        gap = "xxsmall",
                                                        # border = True,
                                                        )

exam_type  = col1.selectbox( 
                            label = "Select the Exam Type",
                            options = ["UG", "PG"],
                            index = 0,
                            key = "Exam_Type_Selection_Box"
                            )

replace_exam_details = col1.checkbox(
    label = "Replace the existing Examination Details",
    key = "Replace_Existing_Examination_Details_Checkbox",
) 
exam_sem = col2.selectbox( 
                            label = "Select the Semester of the Examination",
                            options = [
                                        "I", 
                                        "II",
                                        "III",
                                        "IV",
                                        "V",
                                        "VI",
                                        "VII",
                                        "VIII", 
                                        ],
                            index = None,
                            key = "Exam_Semester_Selection_Box"
                            )

exam_month = col3.selectbox( 
                            label = "Examination Starting Month",
                            options = list(calendar.month_name)[1:],
                            index = None,
                            key = "Exam_Starting_Month", 
                            )

exam_year = col4.text_input( 
                            label = "Examination year as mention in Exam Schedule",
                            placeholder = 2000,
                            key = "Exam_Year_As_Exam_Schedule",
                            required = True,
                            )


exam_detail_submission_button = exam_details_submission_form.form_submit_button( 
                                label = "Click to Save the Examination Details",
                                width = "stretch",
                                key = "Exam_Submission_Button"
                                )


if exam_detail_submission_button and exam_sem is not None and exam_month is not None:

    exam_details_update_sql = sqltext(
                                        """
                                        UPDATE exam_details
                                        SET 
                                        examination_type = :examination_type,
                                        examination_semester = :examination_semester,
                                        examination_month = :examination_month,
                                        examination_year = :examination_year
                                        WHERE 
                                                examination_type = :examination_type AND
                                                examination_semester = :examination_semester AND
                                                examination_month = :examination_month AND
                                                examination_year = :examination_year
                                        """
                                    )

    exam_details_replace_sql = sqltext(
                                        """
                                        UPDATE exam_details
                                        SET 
                                        examination_type = :examination_type,
                                        examination_semester = :examination_semester,
                                        examination_month = :examination_month,
                                        examination_year = :examination_year
                                        WHERE 
                                                examination_type = :old_examination_type AND
                                                examination_semester = :old_examination_semester AND
                                                examination_month = :old_examination_month AND
                                                examination_year = :old_examination_year
                                        """
                                    )

    exam_details_insert_sql = sqltext(
                                    """
                                    INSERT INTO exam_details
                                    (   
                                    examination_type,
                                    examination_semester,
                                    examination_month,
                                    examination_year 
                                    )
                                    VALUES
                                    (
                                    :examination_type,
                                    :examination_semester,
                                    :examination_month,
                                    :examination_year 
                                    )
                                    """
                                    )


    params_dict_list = [
        {
            "examination_type" : exam_type,
            "examination_semester" : exam_sem ,
            "examination_month" : exam_month,
            "examination_year" : exam_year, 

        },
    ] 

    try:
        conn_sql = st.connection( 
                                    name = "neon",
                                    type = SQLConnection,
                                    ttl = 1
                                )

        if conn_sql:

            with conn_sql.session as exam_details_update_session:

                no_of_exam_details_already_inserted = exam_details_update_session.execute(
                        statement = sqltext ("SELECT * FROM exam_details"),
                    )

                if no_of_exam_details_already_inserted.rowcount == 1 and replace_exam_details :

                    selected_row = no_of_exam_details_already_inserted.fetchone()

                    params_dict_list[0]["old_examination_type"] = selected_row[0]
                    params_dict_list[0]["old_examination_semester"] = selected_row[1]
                    params_dict_list[0]["old_examination_month"] = selected_row[2]
                    params_dict_list[0]["old_examination_year"] = selected_row[3] 

                

                    update_resultset = exam_details_update_session.execute(
                                                    statement = exam_details_replace_sql,
                                                    params = params_dict_list,
                    )


                else:

                    update_resultset = exam_details_update_session.execute(
                        statement = exam_details_update_sql,
                        params = params_dict_list,
                    )
                
                if update_resultset.rowcount != 1:


                    if no_of_exam_details_already_inserted.rowcount == 0: 
                        insert_resultset = exam_details_update_session.execute(
                                                statement = exam_details_insert_sql,
                                                params = params_dict_list,
                        )

                if update_resultset.rowcount == 1 or insert_resultset.rowcount == 1:
                    exam_details_update_session.commit()

                    exam_details_enter_container.success( 
                                                            body = "Examination details are "
                                                            "updated." if update_resultset.rowcount == 1
                                                            else "Examination details are "
                                                                "inserted" if insert_resultset.rowcount == 1 
                                                            else "Something is wrong.",
                                                            width = "stretch",
                                                            title = "Examination Details" 
                                                            )





    except sql_errors.DatabaseError as de:
        exam_details_enter_container.error(de)

################################################################################
#
#
#
#
#
################################################################################


exam_subject_type_and_column_form = exam_details_enter_container.form(
    key = "Exam_Subject_Types_andRespective_Columns_in_DR",
    clear_on_submit = True,

)

col1, col2, col3 = exam_subject_type_and_column_form.columns(
    spec = [1,2,2],
    gap = "xxsmall",
)

subject_course_type  = col1.text_input(
    label = "Subject Type",
    help = """Enter Major/Minor/AEC/VAC/MDC,
     If there are more than one Major or Minor
     then enter Major1, Major2,... or 
     Minor1, Minor2...
     """,
     placeholder = "Major/Minor/AEC/VAC/MDC",
     key = "Exam_Subject_Type",
     required = True,
)

subject_course_type_delete_flag = col1.checkbox(
    label = "Delete Subject Type",
    key = "Subject_Type_Delete_Checkbox",
)


column_name_with_course_code = col2.text_input(
    label = "Column Header with Course Code",
    value = "NA",
    help = "provide na for deletion",
    key = "Column_Name_With_Course_code",
    required = True,
)


column_name_with_course_paper_name = col3.text_input(
    label = "Column Header with Course Paper Name",
    value = "NA",
    help = "provide na for deletion",
    key = "Column_Name_Wiith_Course_Paper_Name",
    required = True,
)


exam_subject_type_and_column_form_submission = exam_subject_type_and_column_form.form_submit_button(
    label = "Click to Submit Subject Source Type",
    width = "stretch", 
    key = "Exam_Subject_Type_And_Column_Submission"
)

try:
    conn_sql = st.connection(
        name = "neon",
        type = SQLConnection,
        ttl = 1,
    )
    if conn_sql:

        subject_type_table_creation_sql = sqltext(
            """
            CREATE TABLE IF NOT EXISTS exam_subject_type
                                        (
                                        course_type VARCHAR(20),
                                        course_code_column_header VARCHAR(100) NOT NULL,
                                        course_paper_name_column_header VARCHAR(100) NOT NULL,
                                        PRIMARY KEY (course_type)
                                        )
            """
            )


        subject_type_update_sql = sqltext(
            """
            UPDATE 
            exam_subject_type
            SET 
            course_code_column_header =  :course_code,
            course_paper_name_column_header = :course_paper_name
            WHERE 
            course_type = :course_type
            """
        )


        subject_type_insert_sql = sqltext(
            """
            INSERT INTO
            exam_subject_type
            (
            course_type,
            course_code_column_header,
            course_paper_name_column_header
            )
            VALUES
            (
            :course_type,
            :course_code, 
            :course_paper_name
            )
            """
        )

        subject_type_delete_sql = sqltext(
            """
            DELETE FROM exam_subject_type
            WHERE course_type = :course_type
            """
        )


        params_dict_list = [
            {
            "course_type" : subject_course_type,
            "course_code" : column_name_with_course_code,
            "course_paper_name" : column_name_with_course_paper_name,
            },
        ]

        try:
            with conn_sql.session as exam_subject_type_session:

                exam_subject_type_table_creation_status = exam_subject_type_session.execute(subject_type_table_creation_sql)

                exam_subject_type_session.commit()



                exam_subject_type_existence_check_sql = sqltext(
                    """
                    SELECT * FROM exam_subject_type
                    """
                )

                existing_rows_in_exam_subject_type = exam_subject_type_session.execute(
                    statement = exam_subject_type_existence_check_sql,
                )

                if existing_rows_in_exam_subject_type.rowcount == 0: 
                    exam_details_enter_container.success(
                    body = "Subject Type Table of the Examination is created with"
                   f" status {exam_subject_type_table_creation_status.rowcount}.",
                    title = "EXAM_SUBJECT_TYPE Table"
                    )



                if exam_subject_type_and_column_form_submission  :

                    if not subject_course_type_delete_flag :
                        no_of_rows_updated_for_subject_course_code = exam_subject_type_session.execute(
                            statement =  subject_type_update_sql,
                            params = params_dict_list,
                        )

                        if no_of_rows_updated_for_subject_course_code.rowcount == 0:
                            no_of_rows_inserted_for_subject_course_code = exam_subject_type_session.execute(
                                statement = subject_type_insert_sql,
                                params = params_dict_list,
                            )

                        if ((no_of_rows_updated_for_subject_course_code.rowcount == 1) or 
                                    (no_of_rows_inserted_for_subject_course_code.rowcount == 1)):

                            exam_subject_type_session.commit()

                            exam_details_enter_container.success(
                                                                    f" A row for {subject_course_type}"
                                                                    + (f" is updated with status {no_of_rows_updated_for_subject_course_code.rowcount}." 
                                                                     if  no_of_rows_updated_for_subject_course_code.rowcount == 1 else  
                                                                    f" is inserted with status {no_of_rows_inserted_for_subject_course_code.rowcount}." 
                                                                    if no_of_rows_inserted_for_subject_course_code.rowcount == 1 else "with some issue." 
                                                                    ) 
                                                                    )
                    else:

                        no_of_rows_deleted_for_subject_course_code = exam_subject_type_session.execute(
                            statement = subject_type_delete_sql,
                            params = {
                                "course_type" : subject_course_type,
                                }
                        )

                        if no_of_rows_deleted_for_subject_course_code.rowcount == 1:

                            exam_subject_type_session.commit()

                            exam_details_enter_container.success(f"A row for {subject_course_type} is deleted.")

                    

                    



        except sql_errors.DatabaseError as de:
            exam_details_enter_container.error(
                body = f"There is an error creating the table {de}.",
                title = "EXAM_SUBJECT_TYPE Table",
            )
        
except sql_errors.ConnectionFailure as cf:
    exam_details_enter_container.error(cf)



all_exam_subject_type_df = conn_sql.query(
    sql = "SELECT * FROM exam_subject_type",
    ttl = 1,
    )


all_exam_subject_type_dataframe = exam_details_enter_container.dataframe(
    data = all_exam_subject_type_df,
    height = "content",
    width = "stretch",
    hide_index = True,
    column_config = {
        "course_type" : "Course Type",
        "course_code_column_header" : "Column With Course Code",
        "course_paper_name_column_header" : "Column Header with Course Paper Name",
    },
    key = "All_Exam_Subject_Type_Details",
)
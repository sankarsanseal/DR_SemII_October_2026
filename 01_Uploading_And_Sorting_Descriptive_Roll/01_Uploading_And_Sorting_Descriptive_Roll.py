import streamlit as st
import pandas as pd
from psycopg import errors as sql_errors

from streamlit_gsheets import GSheetsConnection

# import gspread
# from gspread_dataframe import set_with_dataframe

import creating_sorted_dr_in_gsheet_neon as cdr

from sqlalchemy import text as sqltext 

# """
# Container Definition
# 
# 
# 
# """
upload_container = st.container(
                                border = True, 
                                key = "upload_and_sort_dr_container,",
                                )

# 
# 
#   DR Uploader Form 
# 
# 
# 

dr_upload_form = upload_container.form( 
                        key = "file_uploader_form", 
                        clear_on_submit = True,
                        enter_to_submit = True,
                        
                      )


try:                      

    uploaded_dr_file = dr_upload_form.file_uploader(
                                                label = "**Please upload the descriptive roll (DR) provided by the university:**", 
                                                type = ["xls", "xlsx"], 
                                                key = "DR_file_uploader",
                                                width = "stretch",
                                                )
except TypeError as te:
    dr_upload_form.error(te)

dr_uploaded_status = dr_upload_form.form_submit_button(label = "Upload the Descriptive Roll"
                                                                " (DR) and Generate the sorted DR", 
                                                       width =  "stretch")


if dr_uploaded_status:

    try:
        original_dr = pd.read_excel(
                                uploaded_dr_file,
                                sheet_name = "Applicant Data",
                                header = 0,
                                engine = "openpyxl",
                                )

        original_dr.sort_values(
                                by = ["College Code","Roll No"], 
                                inplace = True
                                )
        
        original_dr.reset_index(inplace = True, drop = True)

    except IOError as ie:
        upload_container.error(ie)


    try:
        conn_neon = st.connection(   
                                name = "neon",  
                                type = "sql",
                                ttl = 1,
                             )

        if conn_neon:
            upload_container.success(
                                        "Connection to the database is successful.", 
                                        title = "Database"
                                    )


            with conn_neon.session as truncation_session:

                try:
                    truncate_sql = sqltext(
                                        """
                                        TRUNCATE TABLE exam_dates;
                                        """
                                        )

                    truncation_status = truncation_session.execute(truncate_sql)

                    truncation_session.commit()

                    upload_container.success("The truncation of Table exam_dates is"
                                             " successful with status {0}.".format(truncation_status.rowcount))
                except sql_errors.DatabaseError as de:
                    upload_container.error(de)

            
            for subj_type, full_column_name in cdr.subject_type_dict.items():
                
                subj_type_sorted_df = cdr.return_subject_type_based_student_details(
                                                                                    original_dr, 
                                                                                    full_column_name, 
                                                                                    cdr.subject_name_dict[full_column_name],
                                                                                    *cdr.student_related_columns[3:],
                                                                                    )

                with conn_neon.session as sql_session:

                    truncate_sql = sqltext(f"""TRUNCATE TABLE {subj_type}_STUDENT_COUNT;""")

                    try:
                        truncation_status = sql_session.execute(truncate_sql)

                        sql_session.commit()

                        upload_container.success(f"Truncation of Table {subj_type}_count" 
                                                 " is successful with status {0}.".format(truncation_status.rowcount))
                    except sql_errors.DatabaseError as de:

                        upload_container.error(de)

                    try:

                        for indx, row in subj_type_sorted_df.iterrows():

                            insert_query = sqltext(
                                                    f""" INSERT INTO {subj_type}_student_count
                                                    ( {subj_type}_course_code,
                                                        {subj_type}_course_paper_name,
                                                        {subj_type}_no_of_years,
                                                        {subj_type}_college_code,
                                                        {subj_type}_college_name,
                                                        {subj_type}_exam_category,
                                                        {subj_type}_roll_count
                                                    ) 
                                                    VALUES(
                                                    :code, 
                                                    :paper_name,
                                                    :no_of_years,
                                                    :college_code,
                                                    :college_name,
                                                    :exam_category,
                                                    :student_count
                                                    );
                                                    """
                                                )


                            sql_session.execute(insert_query, params= {
                                                                        "code" : row[full_column_name],
                                                                        "paper_name" : row[cdr.subject_name_dict[full_column_name]],
                                                                        "no_of_years" : row["NEP program"][:14].strip(),
                                                                        "college_code" : row["College Code"],
                                                                        "college_name" : row["College Name"],
                                                                        "exam_category" : row["Exam Category"],
                                                                        "student_count" : row["Roll No"] ,
                                                                        })

                        sql_session.commit()

                        upload_container.success(f"Insertion to Table {subj_type}_student_count is complete.")
                    except ValueError as ve:
                        upload_container.error(ve)



                    try:

                        insert_exam_course_code_sql = sqltext("""
                                                                INSERT INTO exam_dates (exam_course_code)
                                                                SELECT DISTINCT {0}_COURSE_CODE FROM {0}_STUDENT_COUNT
                                                        """.format(subj_type))


                        insertion_status = sql_session.execute(insert_exam_course_code_sql)

                        sql_session.commit()

                        upload_container.success(
                                                    body = "Insertion to Table EXAM_DATES is"
                                                            " complete with insertion status {0}."
                                                            .format(insertion_status.rowcount)
                                                            ,
                                                    title = f"{subj_type.upper()}")
                    except sql_errors.UniqueViolation as de:
                        st.error(de)


            with conn_neon.session as sql_session:

                try:

                    truncate_sql = sqltext(
                                            """
                                            TRUNCATE TABLE ALL_STUDENTS_DETAILS
                                            """
                                            ) 

                    sql_session.execute(truncate_sql)

                    upload_container.success("The truncation of Table all_student_details is complete.")

                except sql_errors.DatabaseError as de:
                    upload_container.error(de)

                total_rows = len(original_dr)
                all_student_upload_progress_bar = upload_container.progress(0.0, text = "Student Insertion Progress")

                for indx, row in original_dr.iterrows():

                    all_student_upload_progress_bar.progress(
                                                                value = indx / total_rows, 
                                                                text = "Student Insertion Progress"
                                                            )

                    for paper_code, paper_name in cdr.subject_name_dict.items():
                        try:


                            if pd.notna(row[paper_code])  :

                                student_insertion_query = sqltext("""
                                                            INSERT INTO ALL_STUDENTS_DETAILS
                                                            (
                                                                ROLL_NO,
                                                                REGISTRATION_NO,
                                                                REGISTRATION_YEAR,
                                                                NEP_Program,
                                                                COLLEGE_CODE,
                                                                COLLEGE_NAME,
                                                                EXAM_CATEGORY,
                                                                COURSE_CODE,
                                                                COURSE_PAPER_NAME
                                                            )
                                                            VALUES 
                                                            (
                                                                :roll_no,
                                                                :registration_no,
                                                                :registration_year,
                                                                :nep_program,
                                                                :college_code,
                                                                :college_name,
                                                                :exam_category,
                                                                :course_code,
                                                                :course_paper_name
                                                            )
                                                        """)

                                sql_session.execute(statement = student_insertion_query, 
                                                                params = {  
                                                                "roll_no" : row["Roll No"] ,
                                                                "registration_no" :  row[ "Registration No" ],
                                                                "registration_year" : row[ "Registration Year" ],
                                                                "nep_program" : row [ "NEP program" ][:14].strip(),
                                                                "college_code" :  row[ "College Code" ],
                                                                "college_name" : row [ "College Name" ],
                                                                "exam_category" : row[ "Exam Category" ],
                                                                "course_code" : getattr(row, paper_code),
                                                                "course_paper_name" : getattr(row, paper_name)
                                                                }
                                                                )
                            
                            
                        except sql_errors.IntegrityError as ie:
                            upload_container.error(ie)


                sql_session.commit()
                upload_container.success("All Student Details are inserted.")


                try:

                    grouping_query = sqltext(
                                        """
                                        SELECT  college_code, 
                                                course_code, 
                                                exam_category, 
                                                nep_program, 
                                                roll_no
                                        FROM all_students_details
                                        ORDER BY college_code, 
                                                course_code,
                                                exam_category, 
                                                nep_program, 
                                                roll_no
                                        """
                                            )

                    grouping_result_set = sql_session(
                                                        statement = grouping_query,

                                                    )
                    group_serial_no_insertion_progress = upload_container.progress( 
                                                            value = 0.0,
                                                            text = 
                                                            "Assigning student's serial no in progress"
                                                            )

                    no_of_all_students = grouping_result_set.rowcount
                    no_of_students_processed = 0
                    
                    previous_nep_program = ""
                    serial_number_in_a_group = 0

                    for row in grouping_result_set:

                        group_serial_no_insertion_progress.progress(
                                            value = no_of_students_processed / no_of_all_students,
                                            text = 
                                            "Assigning student's serial no in progress"
                                            )

                        no_of_students_processed += 1

                        if previous_nep_program != row[3]:
                            serial_number_in_a_group = 1
                        else:
                            serial_number_in_a_group += 1
                            

                        insert_serial_number_query = sqltext(
                                                            """
                                                            UPDATE all_students_details
                                                            SET serial_no_in_group = :indx
                                                            WHERE   college_code = :college_code AND 
                                                                    exam_category  = :exam_category AND
                                                                    nep_program = :nep_program AND
                                                                    course_code = :course_code AND
                                                                    roll_no = :roll_no 
                                                            """
                                                            )   


                        sql_session.execute(
                                            statement = insert_serial_number_query,
                                            params = {
                                                        "college_code" : row[0],
                                                        "course_code" : row[1],
                                                        "exam_category" : row[2],
                                                        "nep_program" : row[3],
                                                        "roll_no" : row[4]
                                                        }
                                            )   

                    sql_session.commit()

                    upload_container.success("Assigning Serial No to students in done.")                  

                            

                        



                except sql_errors.DatabaseError as de:
                    st.error(de)
                


            

    except ConnectionError as ce:

        upload_container.error(ce)


    # 
    # 
    #  Dataframe Display
    # 
    #



    upload_container.subheader("Uploaded DR with important columns only:")
    upload_container.dataframe(
                                original_dr, 
                                key = "uploaded_dr_dataframe", 
                                column_order = cdr.important_columns,
                                )

# major_sorting_status = upload_container.subheader("Major") 


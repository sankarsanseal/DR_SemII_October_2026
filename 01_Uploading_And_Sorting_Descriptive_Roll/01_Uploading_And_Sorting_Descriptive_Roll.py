import streamlit as st
import pandas as pd

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
                                                )
except TypeError as te:
    dr_upload_form.error(te)

dr_uploaded_status = dr_upload_form.form_submit_button(label = "Upload the Descriptive Roll (DR) and Generate the sorted DR")


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

            
            for subj_type, full_column_name in cdr.subject_type_dict.items():
                
                subj_type_sorted_df = cdr.return_subject_type_based_student_details(
                                                                                    original_dr, 
                                                                                    full_column_name, 
                                                                                    cdr.subject_name_dict[full_column_name],
                                                                                    *cdr.student_related_columns[3:],
                                                                                    )

                with conn_neon.session as sql_session:

                    truncate_sql = f"""TRUNCATE TABLE {subj_type}_STUDENT_COUNT;"""

                    upload_container.success(f"Truncation of Table {subj_type}_count is successful.")

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

                        upload_container.success(f"Insertion to table {subj_type}_student_count is complete.")
                    except ValueError as ve:
                        upload_container.error(ve)
                        

            


            

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


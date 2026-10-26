import streamlit as st
import pandas as pd
from sqlalchemy import text as sqltext

from psycopg import errors as sql_errors


conn_sql = st.connection(name = "neon", type = "sql", ttl = 1)

upload_container = st.container(border = True)

if conn_sql:
            with conn_sql.session as sql_session: 
                try:

                    grouping_query = sqltext(
                                        """
                                        SELECT  college_code, 
                                                course_code, 
                                                nep_program, 
                                                exam_category, 
                                                roll_no
                                        FROM all_students_details
                                        ORDER BY college_code, 
                                                course_code,
                                                nep_program, 
                                                exam_category, 
                                                roll_no
                                        """
                                            )

                    grouping_result_set = sql_session.execute(
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

                    params_dict_list = []

                    for row in grouping_result_set.fetchall():

                        group_serial_no_insertion_progress.progress(
                                            value = no_of_students_processed / no_of_all_students,
                                            text = 
                                            "Assigning student's serial no in progress"
                                            )

                        no_of_students_processed += 1

                        if previous_nep_program != row[2]:
                            serial_number_in_a_group = 1
                        else:
                            serial_number_in_a_group += 1
                        previous_nep_program = row[2]

                        params_dict_list.append({
                                                        "indx" : serial_number_in_a_group,
                                                        "college_code" : row[0],
                                                        "course_code" : row[1],
                                                        "nep_program" : row[2],
                                                        "exam_category" : row[3],
                                                        "roll_no" : row[4]
                                                        })
                            

                    insert_serial_number_query = sqltext(
                                                            """
                                                            UPDATE all_students_details
                                                            SET serial_no_in_group = :indx
                                                            WHERE   college_code = :college_code AND 
                                                                    course_code = :course_code AND
                                                                    nep_program = :nep_program AND
                                                                    exam_category  = :exam_category AND
                                                                    roll_no = :roll_no 
                                                            """
                                                            )   


                    sql_session.execute(
                                            statement = insert_serial_number_query,
                                            params = params_dict_list, 
                                        )   

                    sql_session.commit()

                    upload_container.success("Assigning Serial No to students in done.")                  

                            

                        



                except sql_errors.DatabaseError as de:
                    st.error(de)
 
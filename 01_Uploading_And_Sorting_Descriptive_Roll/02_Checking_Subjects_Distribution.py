import streamlit as st
import pandas

import creating_sorted_dr_in_gsheet_neon as cdr

from sqlalchemy import text as sqltext


subject_type_data_distribution_container = st.container(
                                        border = True, 
                                        key = "Subjects_and_Their_Student_Count",
                                        )

col1, col2 = subject_type_data_distribution_container.columns(2, gap = "xxsmall")

conn_sql = st.connection(   name = "neon", 
                                type ="sql", 
                                ttl = 1,
                            )

subject_course_type = conn_sql.query(
    sql = """
            SELECT course_type  
            FROM exam_subject_type 
            ORDER BY course_type
        """,
    ttl = 1,
) 


selected_subject_type = col1.selectbox( 
                                                    label = "Select the Course Type", 
                                                   options = subject_course_type["course_type"].to_list(), 
                                                   index = None,
                                                   key= "Course_Type_Selection"
                                                   )

selected_no_years_of_subject = col2.selectbox(
                                                label = "Select Duration of the Course", 
                                              options = ["4-Year Honours", "3-Year Degree", "All"], 
                                              key = "Selection_of_Number_of_Years",
                                              index = None,
                                              )
if selected_subject_type is not None:

    
    sql_query = """
                SELECT {0}_course_code, {0}_course_paper_name, {0}_college_code """.format(selected_subject_type)

    
    if selected_no_years_of_subject is None or selected_no_years_of_subject == "All":
        sql_query += """, sum({0}_roll_count) as {0}_Roll_Count FROM {0}_student_count 
                        GROUP BY {0}_course_code, {0}_course_paper_name, {0}_college_code
                    """.format(selected_subject_type)
    
    else:
        sql_query += """, {0}_no_of_years, sum({0}_roll_count) as {0}_Roll_Count FROM {0}_student_count
                        WHERE {0}_no_of_years = '{1}'
                GROUP BY {0}_course_code, {0}_course_paper_name, {0}_college_code, {0}_no_of_years
                """.format(selected_subject_type, selected_no_years_of_subject)


    sql_query += """ ORDER BY {0}_COURSE_CODE;""".format(selected_subject_type) 

    subject_type_student_count_df = conn_sql.query(sql = sql_query, 
                                                #    params={ "no_of_years" : selected_no_years_of_subject

                                                #                 } ,
                                                        ttl = 1
                                                )


    subject_type_student_count_df.columns = [column.upper() for column in subject_type_student_count_df.columns]


    # subject_type_student_count_df.sort_values(
    #                                             by = "{0}_COURSE_CODE".format(selected_subject_type), 
    #                                             inplace = True
    #                                         )

    subject_type_student_count_df.reset_index(inplace = True, drop = True)

    subject_type_data_distribution_container.title(f"{selected_subject_type} Subjects and Their Student Count")
    subject_type_data_distribution_container.dataframe(
                                                        subject_type_student_count_df, 
                                                        height = "content",
                                                        key = "Distribution_DataFrame"
                                                        )

    subject_type_data_distribution_container.header("Total Number of Students: *{0}*"
                                                    .format(subject_type_student_count_df[f"{selected_subject_type}_roll_count".upper()].sum()
                                                            )
                                                    )
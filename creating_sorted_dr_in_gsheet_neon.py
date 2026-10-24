import streamlit as st
import pandas as pd
import os


def return_subject_type_based_student_details(
                                                dr_dataframe: pd.DataFrame, 
                                                subject_type_code : str,
                                                subject_paper_name : str,
                                                no_of_year_of_course : str,
                                                college_code : str,
                                                college_name : str,
                                                exam_category : str,
                                              ) -> pd.DataFrame:
    
    counts = (
                dr_dataframe.groupby( by = [
                                                    subject_type_code, 
                                                    subject_paper_name, 
                                                    no_of_year_of_course,
                                                    college_code,
                                                    college_name,
                                                    exam_category,
                                            ], as_index = False)["Roll No"]
                .count()
            )

    return counts





subject_type  = ["Major", "Minor", "AEC", "VAC", "SEC", "Multi/Interdisciplinary",  ]


group_columns = [f"{col} Subject BU Paper Code" for col in subject_type]

subject_name_list = [f"{col} Subject Paper Name" for col in subject_type] 

subject_name_dict = dict(zip(group_columns, subject_name_list))


subject_type_dict = dict(   [ 
                            ("mdc" if subj_type.startswith("Multi") else subj_type.lower(), full_column_name) 
                            for subj_type, full_column_name  in zip(subject_type, group_columns)  
                             
                            ]
                        )

student_related_columns = [   
                            "Roll No", 
                            "Registration No", 
                            "Registration Year", 
                            "NEP program", 
                            "College Code",
                            "College Name",
                            "Exam Category",
                        ]
 
important_columns = student_related_columns.copy() 


for exam_couser_paper_code, exam_course_paper_name  in subject_name_dict.items():
    important_columns += [ exam_couser_paper_code, exam_course_paper_name ]
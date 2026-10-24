import streamlit as st
import pandas as pd
import os






subject_type  = ["Major", "Minor", "AEC", "VAC", "SEC", "Multi/Interdisciplinary",  ]

group_columns = [f"{col} Subject BU Paper Code" for col in subject_type]

subject_name_list = [f"{col} Subject Paper Name" for col in subject_type] 

subject_name_dict = dict(zip(group_columns, subject_name_list))

important_columns = [   "Roll No", 
                        "Registration No", 
                        "Registration Year", 
                        "NEP program", ] 



for exam_couser_paper_code, exam_course_paper_name  in subject_name_dict.items():
    important_columns += [ exam_couser_paper_code, exam_course_paper_name ]
import streamlit as st
import pandas as pd
import os

path_to_the_dir = os.path.dirname(os.path.abspath(__file__))

path_to_excel_file = os.path.join(path_to_the_dir,"dr_semII_oct_2026.xlsx") 

path_to_subject_wise_counting = os.path.join(path_to_the_dir,"sorted_dr_semII_oct_2026.xlsx")

path_to_subject_wise_sorted_dr = os.path.join(path_to_the_dir,"subject_wise_sorted_dr_semII_oct_2026.xlsx")


subject_type  = ["Major", "Minor", "AEC", "VAC", "SEC", "Multi/Interdisciplinary",  ]

group_columns = [f"{col} Subject BU Paper Code" for col in subject_type]

subject_name_list = [f"{col} Subject Paper Name" for col in subject_type] 

subject_name_dict = dict(zip(group_columns, subject_name_list))

if os.path.exists(path_to_excel_file):
    dr_df = pd.read_excel(path_to_excel_file, sheet_name = "Applicant Data", engine = "openpyxl")

    print(*dr_df.columns, sep = "\n")

    major_student_count = 0
    minor_student_count = 0





    with pd.ExcelWriter(path_to_subject_wise_counting, engine="openpyxl") as writer:
        for column in group_columns:
            counts = (
                dr_df.groupby(column)
                .size()
                .reset_index(name="count")
            )

            for subject_code in counts[column]:
                with pd.ExcelWriter( path_to_subject_wise_sorted_dr, 
                                                    engine="openpyxl", 
                                                    mode="a" if os.path.exists(path_to_subject_wise_sorted_dr) else "w", 
                                                    if_sheet_exists="replace" if os.path.exists(path_to_subject_wise_sorted_dr) else None 
                                                    ) as student_writer:
                    if pd.notna(subject_code):
                        student_list = dr_df[dr_df[column] == subject_code][["Roll No", "Registration No", "Registration Year", "NEP program", 
                                                                                column, subject_name_dict.get(column, "")]]
                        student_list.to_excel(student_writer, sheet_name=subject_code.replace("/", "_"), index=False)
            
            counts.to_excel(writer, sheet_name=column.replace("/", "_"), index=False)

            
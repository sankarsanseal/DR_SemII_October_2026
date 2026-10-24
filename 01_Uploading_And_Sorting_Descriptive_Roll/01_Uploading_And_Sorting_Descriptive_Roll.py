import streamlit as st
import pandas as pd

from streamlit_gsheets import GSheetsConnection


import creating_sorted_dr_in_gsheet_neon as cdr

upload_container = st.container(
                                border = True, 
                                key = "upload_and_sort_dr_container,",
                                )


dr_upload_form = upload_container.form( 
                        key = "file_uploader_form", 
                        clear_on_submit = True,
                        enter_to_submit = True,

                      )


try:                      

    uploaded_dr_file = dr_upload_form.file_uploader(
                                                label = "Please upload the descriptive roll (DR) provided from the university.", 
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

        original_dr.sort_values(by = "Roll No")

    except IOError as ie:
        upload_container.error(ie)
    
    upload_container.subheader("Uploaded DR with important columns only:")
    upload_container.dataframe(
                                original_dr, 
                                key = "uploaded_dr_dataframe", 
                                column_order = cdr.important_columns,
                                )

# major_sorting_status = upload_container.subheader("Major") 


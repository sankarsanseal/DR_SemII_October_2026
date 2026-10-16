import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    @media print {
        .st-key-room_selector {
            display: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


path_to_the_dir = os.path.dirname(os.path.abspath(__file__))

path_to_excel_file = os.path.join(path_to_the_dir,"subject_wise_sorted_dr_semII_oct_2026.xlsx")


room_no=st.selectbox("Select the Room", [101, 103, 109, 110, 111, 201, 204], key="room_selector")

roll_df = pd.DataFrame(columns=["Roll No", "Registration No.", "Signature", """Objective Type \n Answer Sheet No.""", "Main\n Script No.", "NEP program", "Subject Code"])


with pd.ExcelFile(path_to_excel_file, engine = "openpyxl") as xls:
    sheet_names = xls.sheet_names
    for sheet_name in sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        numberic_columns = df.select_dtypes(include=['number']).columns
        df[numberic_columns] = df[numberic_columns].astype("Int64")
        if "Room No" in df.columns:

            subject_code_column = None            
            for column in df.columns:
                if column.endswith("BU Paper Code"):
                    subject_code_column = column
                    break

            filtered_df = df.loc[df["Room No"] == room_no]

            if "Subject Code" in roll_df.columns:
                roll_df = roll_df.rename(columns= {"Subject Code" : subject_code_column})
            roll_df = pd.concat([roll_df, filtered_df[["Roll No", "NEP program", subject_code_column]]], ignore_index=True)

        
roll_df.reset_index(drop=True, inplace=True)

total_number_of_rows = len(roll_df)
number_of_rows_per_page = 24



table_html = """
<style>
@media print {
    @page { size: A4 portrait; margin: 12mm; }
    .print-page {
        position: relative;
        height: 273mm;
        box-sizing: border-box;
        break-after: page;
        page-break-after: always;
     }
    .page-footer {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            width: 100%;
        }

}
table {
    border-collapse: collapse;
}

th, td {
    border: 2px solid black;
}

th, td {
    border: 4px solid black;
}
</style>
<section class="print-page">
<p style = 'text-align: right; font-weight : bold;'>  Attendance Sheet </p>
<h3 style = 'text-align: center;'>  THE UNIVERSITY OF BURDWAN </h3>
<p style = 'text-align: center;'>........................................................Examination, 202_ </p>
<p style = 'text-align: center;'>  Subject...............................................................</p>
<table style="border-collapse: collapse; width: 100%; border: 1px solid black; padding:0px; font-size: 11px;"> 
                <colgroup>
                    <col style="width:25%;">
                    <col style="width:25%;">
                    <col style="width:25%;">
                    <col style="width:15%;">
                    <col style="width:10%;">
                </colgroup>
                            <thead>
                                    <tr>
                                    <th>Roll No</th>
                                    <th>Registration<br>No.</th>
                                    <th>    Signature   </th>
                                    <th>Objective Type <br> Answer Sheet No.</th>
                                    <th>Main<br> Script No.</th> 
                                    </tr> 
                            </thead> 
                            <tbody> 
                            """
prev_roll_no = None

for position, (index, row) in enumerate(roll_df.iterrows()):

    if str(row["Roll No"])[:4] != str(prev_roll_no)[:4]:
        table_html += f"""<tr>
                            <td>{row[subject_code_column]}:{row["NEP program"][:6]}   {row["Roll No"]} </td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>"""

    else:
        table_html += f"""<tr>
                            <td>{row["Roll No"]} </td>
                            <td></td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>"""
    
    
    prev_roll_no = row["Roll No"]

                    


    if position % number_of_rows_per_page == 0 and position != 0:
        table_html += """</tbody> 
                    </table>
                    <br>
                    <div class= "page-footer" style="display:flex; justify-content:space-between; width:100%;">
                        <span>Signature of the Officer-in-Charge</span>
                        <span>Signature of the Invigilators</span>
                    </div>
                    </section>
                    """
        st.markdown(table_html, unsafe_allow_html=True)

        table_html = """
            <style>
@media print {
    @page { size: A4 portrait; margin: 12mm; }
    .print-page {
        position: relative;
        height: 273mm;
        box-sizing: border-box;
        break-after: page;
        page-break-after: always;
        }
    }

    .page-footer {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            width: 100%;
        }

}
th, td {
    border: 4px solid black;
}
</style>
<section class="print-page">
<p style = 'text-align: right; font-weight : bold;'>  Attendance Sheet </p>
<h3 style = 'text-align: center;'>  THE UNIVERSITY OF BURDWAN </h3>
<p style = 'text-align: center;'>........................................................Examination, 202_ </p>
<p style = 'text-align: center;'>  Subject...............................................................</p>
  <table style="border-collapse: collapse; width: 100%; border: 1px solid black; padding:0px; font-size: 11px;">
             <colgroup>
                <col style="width:25%">
                <col style="width:25%">
                <col style="width:25%">
                <col style="width:15%">
                <col style="width:10%">
            </colgroup>
                            <thead>
                                    <tr>
                                    <th>Roll No</th>
                                    <th>Registration<br>No.</th>
                                    <th>    Signature   </th>
                                    <th>Objective Type <br> Answer Sheet No.</th>
                                    <th>Main<br> Script No.</th> 
                                    </tr> 
                            </thead> 
                            <tbody> 
                            """

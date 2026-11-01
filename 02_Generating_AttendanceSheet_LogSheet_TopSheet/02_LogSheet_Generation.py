import streamlit as st
import pandas as pd

from sqlalchemy import text as sqltext
from streamlit.connections import SQLConnection


from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_table(filename="data_report.pdf", data : str = "" ):
    # 1. Setup document container with margins
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    # 2. Setup typography styles
    styles = getSampleStyleSheet()
    
    # Custom style for the document title
    title_style = ParagraphStyle(
        "ReportTitle", 
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        # textColor=colors.HexColor("#1A365D"),
        spaceAfter=15
    )
    
    # Custom styles for table cells to force automatic text wrapping
    header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.whitesmoke,
        fontName="Helvetica-Bold"
    )
    
    body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#2D3748")
    )

    # Add a title to the document flow
    story.append(Paragraph('CHANDERNAGORE COLLEGE\n LOG SHEET', title_style))
    story.append(Spacer(1, 10))

    # 3. Define raw table data
    headers = ["Roll No.s of Students Allotted to the Room", "Roll No of Absent Students",]
    
    # raw_rows = [
    #     ["INV-001", "GigaBit Network Router Enterprise Pro", "Hardware", "45", "Optimal stock level. No reorder required."],
    #     ["INV-002", "UltraWide 34-inch 4K Monitor", "Electronics", "12", "Low stock warning. Reorder threshold triggered."],
    #     ["INV-003", "Ergonomic Mesh Office Chair v2", "Furniture", "85", "Overstocked. Temporary hold on new procurement orders."],
    #     ["INV-004", "USB-C Dual Docking Station Hub", "Accessories", "3", "Critical level. Backorder requested immediately."],
    #     ["INV-005", "Cat6e Shielded Ethernet Cable (100ft)", "Hardware", "150", "Optimal stock level. Moving steadily."],
    # ]
    
    # Duplicate rows to demonstrate multi-page handling and repeated headers
    # raw_rows = raw_rows * 6 

    # 4. Wrap all string cell values in Paragraph components
    formatted_data = []
    
    # Process headers
    formatted_data.append([Paragraph(h, header_style) for h in headers])
    
    # Process body rows
    # for row in data_rows:
    formatted_data.append([Paragraph(cell, body_style) for cell in data])

    # 5. Define column widths (Total width available on Letter page with 36pt margins = 540pt)
    column_widths = [400, 100]

    # 6. Initialize Table object
    # repeatRows=1 ensures headers appear at the top of every new page
    table = Table(formatted_data, colWidths=column_widths, repeatRows=1)

    # 7. Apply structural and visual styles
    table_style = TableStyle([
        # Header configurations
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        
        # Grid line and border layouts
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor("#0D1B2A")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        
        # Row padding configurations
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ])

    # Dynamic styling rule: Add alternating light-grey rows for readability
    for i in range(1, len(formatted_data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor("#F7FAFC"))

    table.setStyle(table_style)
    story.append(table)

    # 8. Build document into file
    doc.build(story)


selected_room = None
selected_date = None
selected_time = None


logsheet_container = st.container(
    border = True,
    key = "LogSheet_As_PDF_Generating_Container"
)

col1, col2, col3 = logsheet_container.columns(
    spec = [1,1,1],
    gap = "xxsmall",
)

logsheet_form = logsheet_container.form(
    key = "Logsheet_Generating_Form",
    border = False,

)



selected_date = col1.date_input(
    label = "Select the Date of Examination",
    key = "Exam_Date_Input",
)




logsheet_form_submission_button = logsheet_form.form_submit_button(
    label = "Generate the Log Sheet",
    key = "Logsheet_Generation_Form_Submission_Button",
    width = "stretch",
)


conn_sql = st.connection( 
    name = "neon",
    type = SQLConnection,
    ttl = 1,
    )


if conn_sql:


    if selected_date is not None:

        with conn_sql.session as sql_session:


            time_slots_sql = sqltext(
                """
                SELECT DISTINCT TO_CHAR(exam_start_time,'HH12:MI AM')
                FROM exam_dates
                WHERE exam_date = :exam_date
                """
            )

            time_slots_resultset = sql_session.execute(
                statement = time_slots_sql,
                params = {
                    "exam_date" : selected_date.strftime(
                        format="%Y-%m-%d"
                        )
                }
            )

            
            selected_time = col2.selectbox(
                label = "Select the Start Time of the Examination",
                options = [row[0] for row in time_slots_resultset.fetchall()],
                index = None,
                key = "Exam_Start_Selection_Box",
            )


            if selected_time is not None:

                room_no_sql = sqltext(
                                    """
                                    SELECT concat_ws('-', building_name, room_no, floor_no)
                                    FROM room_details
                                    ORDER BY building_name, room_no, floor_no
                                    """
                                        )


                with conn_sql.session as room_session:

                    room_no_resultset =  room_session.execute(
                        statement = room_no_sql,

                    )

                    selected_room = col3.selectbox(
                        label = "Select the Room No.",
                        options = [row[0] for row in room_no_resultset.fetchall()],
                        index = None,
                        key = "LogSheet_Room_Selection",
                    )                


    logsheet_content_string = ""

    if logsheet_form_submission_button and (selected_date is not None 
                                            and selected_time is not None 
                                            and selected_room is not None):

        room_students_list_sql = sqltext(
                                            """
                                            SELECT course_code, nep_program, exam_category, roll_no
                                            FROM all_students_details as S, exam_dates as E
                                            WHERE S.course_code = E.exam_course_code AND
                                            S.room_no = :room_no AND
                                            S.building_name = :building_name AND
                                            E.exam_date = :selected_date AND
                                            E.exam_start_time = :selected_start_time
                                            ORDER BY course_code, nep_program, exam_category, roll_no
                                            """
                                         )

        with conn_sql.session as session:

            room_student_list_resultset = session.execute(
                statement = room_students_list_sql,
                params = {
                    "room_no" : selected_room.split("-")[1],
                    "building_name" : selected_room.split("-")[0],
                    "selected_date" : selected_date.strftime('%Y-%m-%d'),
                    "selected_start_time" : selected_time,
                },
            )

            previous_course_code = ""
            previous_nep_program = ""
            previous_exam_category = ""
            previous_roll_no_prefix = ""

            group_header_list = []
            for row in room_student_list_resultset.fetchall():

                if (previous_course_code != row[0]
                    or previous_nep_program !=row[1][:3]
                    or previous_exam_category != row[2]
                    or previous_roll_no_prefix != row[-1][:8] 
                    ):

                    if len(group_header_list) > 0:
                        logsheet_content_string += (", ".join(group_header_list))
                        logsheet_content_string += ("=", len(group_header_list))
                        group_header_list = []
                    group_header_list.append(row[-1][-4:])
                    logsheet_content_string += (" ".join((row[0], row[1][:3], row[2], row[-1][:8], )))
                else:
                    group_header_list.append(row[-1][-4:])

                previous_course_code = row[0]
                previous_nep_program = row[1][:3]
                previous_exam_category = row[2]
                previous_roll_no_prefix = row[-1][:8]
            else:
                logsheet_content_string += (", ".join(group_header_list))
                logsheet_content_string += ("=", len(group_header_list))


    generate_pdf_table(filename = f"LogSheet_RoomNo{selected_room}_{selected_date}_{selected_time}.pdf",
                       data = [logsheet_content_string]
                       )



    pdf_display = logsheet_container.pdf( 
        data = f"LogSheet_RoomNo{selected_room}_{selected_date}_{selected_time}.pdf",
        
        )



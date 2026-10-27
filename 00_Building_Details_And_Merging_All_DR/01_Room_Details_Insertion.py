import streamlit as st

from sqlalchemy import text as sqltext

from psycopg import errors as sql_errors
from streamlit.connections import SQLConnection 


room_details_insertion_container = st.container(border = True,)

room_details_insertion_container.title(
                                        body = "Use This Page to Insert Room Details"
                                       " Where Examinations will be held"
                                       )

room_details_insertion_form = room_details_insertion_container.form( 
                                        key = "Room_Details_Insertion_Form",
                                        border = True,
                                        )

col1, col2, col3, col4, col5, col6 = room_details_insertion_form.columns(6, 
                                                            gap = "xxsmall", 
                                                            )

room_no = col1.text_input(
                            label = "Enter the Room No", 
                            placeholder = "000",
                            key = "room_no_input_text_field",
                            required = True,
                            )
building_name = col2.selectbox( 
                                label = "Select the Building Name",
                                options = [
                                            "Gurudev Bhawan", 
                                            "Administrative Building"
                                            ],
                                index = None,
                                placeholder = "Building Name",
                                key = "building_name_selection_dropdown_box",
                                
                                )

floor_no = col3.selectbox(
                            label = "Select the floor of the room",
                            options = [
                                            "Ground Floor", 
                                            "First Floor", 
                                            "Second Floor",
                                            "Third Floor",
                                            "Fourth Floor",
                                        ],
                            index = None,
                            placeholder = "Floor no",
                            key = "floor_no_selection_dropdown_box",
                            )

no_of_benches_in_a_room = col4.number_input( label = "Enter the number of Benches",
                                            min_value = 5, 
                                          placeholder = 0,
                                          key ="no_of_bench_in_a_room",
                                          ) 

no_of_students_on_a_bench = col5.number_input(
                                                label = "The number of students per bench",
                                              min_value = 1,
                                              max_value = 3,
                                              placeholder = 0,
                                              key = "no_of_students_in_a_bench"
                                              )

remark_comment = col6.text_input(
                                label= "Provide Remark if any room like CLT, Commerce",
                                placeholder = "Chemistry Lecture Theatre, Commerce, etc",
                                key = "Remark_If_any"

                                    )

room_details_insertion_submit_button = room_details_insertion_form.form_submit_button( 
                                label = "Submit the Room Details",
                                key = "Room_No_Submission_Form_Button",
                                width = "stretch",
                                )


if room_details_insertion_submit_button:

    try:
        conn_sql =  st.connection( 
                                name = "neon",
                                type = SQLConnection,
                                ttl = 1, 
                                )

        room_details_insertion_update_sql = sqltext(
                                                    """
                                                    UPDATE room_details
                                                    SET room_no = :room_no,
                                                    building_name = :building_name,
                                                    floor_no = :floor_no,
                                                    no_of_benches = :no_of_benches,
                                                    no_of_students_per_bench = :no_of_students_per_bench,
                                                    remark = :remark
                                                    WHERE
                                                    room_no = :room_no AND
                                                    building_name = :building_name AND
                                                    floor_no = :floor_no
                                                    """
                                                    )

        room_details_insertion_insert_sql = sqltext(
                                                    """
                                                    INSERT INTO room_details
                                                    (
                                                    room_no,
                                                    building_name,
                                                    floor_no,
                                                    no_of_benches,
                                                    no_of_students_per_bench,
                                                    remark
                                                    )
                                                    VALUES
                                                    (
                                                    :room_no,
                                                    :building_name,
                                                    :floor_no,
                                                    :no_of_benches,
                                                    :no_of_students_per_bench,
                                                    :remark
                                                    )
                                                    """
                                                    )

        params_dict_list = [
                            {
                                "room_no" : room_no,
                                "building_name" : building_name,
                                "floor_no" : floor_no,
                                "no_of_benches" : no_of_benches_in_a_room,
                                "no_of_students_per_bench" : no_of_students_on_a_bench,
                                "remark" : remark_comment,
                            },
                            ]

        with conn_sql.session as sql_session:

            try:

                no_of_rows_updated = sql_session.execute( statement = room_details_insertion_update_sql,
                                                        params = params_dict_list, 
                                                        ) 
                no_of_rows_inserted = None
                if no_of_rows_updated.rowcount != 1 :

                    no_of_rows_inserted = sql_session.execute( 
                                                                statement = room_details_insertion_insert_sql,
                                                                params = params_dict_list,
                                                            )
                        

                if (no_of_rows_updated.rowcount == 1) or (no_of_rows_inserted.rowcount == 1):
                    sql_session.commit()

                    if no_of_rows_inserted is not None and no_of_rows_inserted.rowcount == 1:

                        room_details_insertion_container.success(
                                                                f"Room No: {room_no} "
                                                                f"in the {building_name} details are"
                                                                " inserted." 
                                                                )
                    elif no_of_rows_updated.rowcount == 1:
                        room_details_insertion_container.success(
                                                                f"Room No: {room_no} "
                                                                f"in the {building_name} details are"
                                                                " updated." 
                                                                )

            except sql_errors.IntegrityError as ie:
                room_details_insertion_container.error(ie)

            all_room_details_df = conn_sql.query("SELECT * FROM room_details", ttl = 1, )
            room_details_all_room_dataframe = room_details_insertion_container.dataframe( 
                                                                            data = all_room_details_df,
                                                                            height = "content",
                                                                            width = "stretch",
                                                                            key = "All_Room_Details_Dataframe",
                                                                            )


    except (        sql_errors.ConnectionException, 
                    sql_errors.ConnectionFailure,  
                    sql_errors.ConnectionTimeout,
            ) as de:
        room_details_insertion_container.error(de)


import streamlit as st
import pandas as pd
import os
import io

# Show a title and header for the app
st.title("FileZempic")
st.header("... for files that need to lose a little weight.")

# Invite the user to upload the data file and an optional filter file
initial_file = st.file_uploader("Upload the file for slimming", type = ["xlsx", "xls", "csv"])
filter_file = st.file_uploader("Upload filter list (optional; one name per line)", type = "txt")

# Once the user has told us what file to upload, we can get going.
if initial_file is not None:

    # check the file extension to see if it's a CSV or an Excel file and behave accordingly.
    root, ext = os.path.splitext(initial_file.name)
    if ext == ".csv":
        df = pd.read_csv(initial_file)
    else:
        df = pd.read_excel(initial_file)

    # Build a list of columns present in the df
    cols = df.columns.tolist()

    # If the user has specified a filter file, read it and convert to a Python list called keep_columns
    if filter_file is not None:
        content = filter_file.read().decode("utf-8")
        keep_columns = content.splitlines()

    # If no filter file, then allow the user to build keep_columns via a picklist of columns in the df
    else:
        keep_columns = st.multiselect( "Select the columns to retain:", cols) 

    # Check to make sure that keep_columns is a subset of the actual columns. 
    good_list = set(keep_columns).issubset(cols)  

    # If keep_columns has items not in the dataframe, display an error message
    if good_list == False:
        missing = set(keep_columns) - set(cols)
        st.write(f"Your filter is asking for columns not present in the dataframe: {missing}.")

    # If keep_columns is a subset of the datafame, we can continue.
    else: 

        # Slim the dataframe using the filter defined by the user (whether uploaded or selected from picklist)
        df_slimmed = df[keep_columns]

        # Display the slimmed dataframe on screen
        st.write(df_slimmed)

        # Ask the user for a file name (via text input) and an extension (via radio button)
        export_file = st.text_input("Export name (without extension)", "slimmed") 
        export_type = st.radio( "Choose export format", ["CSV", "Excel"], horizontal=True)

        # Convert the dataframe to an appropriate data object depending on whether the user wants CSV or Excel
        if export_type == "CSV":
            data = df_slimmed.to_csv(index=False).encode("utf-8")
            download_name = f"{export_file}.csv"
            mime = "text/csv"
        else:  
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df_slimmed.to_excel(writer, index=False, sheet_name="Sheet1")
            data = buffer.getvalue()
            download_name = f"{export_file}.xlsx"
            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        # Convert the "filter" to a text object with one item per line for potential re-use
        columns_text = "\n".join(keep_columns)

        # Set up two columns so buttons appear side-to-side
        col1, col2 = st.columns(2) 

        with col1: 
                # Download the file if the user presses this button
                st.download_button(
                    label = "Download file",
                    data = data,
                    file_name = download_name,
                    mime = mime
                )

        with col2: 
            # Download the filter if the user presses this button
            st.download_button(
                label = "Download filter list",
                data = columns_text,
                file_name = "Filter.txt",
                mime = "text/plain"
            )


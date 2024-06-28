"""
This module provides functionalities for processing data sheets uploaded by users. \
    It supports reading from CSV and Excel files,
displaying the original data, and performing specified processing tasks on the data.
"""

import platform
import os
import streamlit as st
import pandas as pd

st.title("RISE Data Sheet Processor")


def read_file(uploaded_file):
    """
    Reads the uploaded file and returns its content as a pandas DataFrame.

    This function supports CSV and Excel files. It checks the file type of the uploaded \
        file and reads it accordingly.
    If the file is empty or an unsupported file type is uploaded, \
        an error message is displayed to the user.

    Parameters:
    uploaded_file (UploadedFile): The file uploaded by the user.

    Returns:
    pandas.DataFrame or None: The content of the uploaded file as a DataFrame, \
        or None if an error occurs.
    """
    try:
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
        elif (
            uploaded_file.type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file type. Please upload a CSV or Excel file.")
            return None

        if df.empty:
            st.error("The uploaded file is empty.")
            return None

        return df
    except pd.errors.EmptyDataError:
        st.error("No columns to parse from file. Please check the file content.")
        return None
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return None


def process_file(df, remove_types, column_name):
    """
    Processes the given DataFrame by removing specified types and sorting by a specified column.

    This function filters out rows based on the values in a specified column \
        and sorts the remaining data
    by that column in ascending order. If the specified column is not found \
        in the DataFrame, an error message
    is displayed to the user.

    Parameters:
    df (pandas.DataFrame): The DataFrame to process.
    remove_types (list): A list of values to remove from the DataFrame based on the column_name.
    column_name (str): The name of the column to filter and sort by.

    Returns:
    pandas.DataFrame or None: The processed DataFrame, or None if the specified column is not found.
    """
    try:
        if df is not None:
            st.write("Original Row Count:", df.shape[0])

            if column_name not in df.columns:
                st.error(f"Column '{column_name}' not found in the file.")
                st.write("Available columns:", df.columns.tolist())
                return None

            df = df[~df[column_name].isin(remove_types)].sort_values(
                column_name, ascending=True
            )

            st.write("Post-Processing Row Count:", df.shape[0])

            return df
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

    return None


def save_file(df, filename):
    """
    Saves the DataFrame to a CSV file with the given filename.

    This function exports the DataFrame to a CSV file without the index. \
        After saving, it notifies the user
    and attempts to open the file using the default application based on the operating system.

    Parameters:
    df (pandas.DataFrame): The DataFrame to be saved.
    filename (str): The name of the file to save the DataFrame to.

    Returns:
    None
    """
    df.to_csv(filename, index=False)
    st.write("File Saved")
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        os.system(f"open {filename}")


def save_excel_with_sheets(original_df, processed_df, filename):
    """
    Saves the original and processed DataFrames to an Excel file with separate sheets.

    This function exports two DataFrames to a single Excel file, \
        placing each DataFrame on a separate sheet.
    After saving, it notifies the user and attempts to open the \
        file using the default application based on
    the operating system.

    Parameters:
    original_df (pandas.DataFrame): The original DataFrame to be saved on the first sheet.
    processed_df (pandas.DataFrame): The processed DataFrame to be saved on the second sheet.
    filename (str): The name of the Excel file to save the DataFrames to.

    Returns:
    None
    """
    with pd.ExcelWriter(filename) as writer:
        original_df.to_excel(writer, sheet_name="PTG", index=False)
        processed_df.to_excel(writer, sheet_name="EA Upload", index=False)
    st.write("File Saved")
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        os.system(f"open {filename}")


def process_pipeline_instances(df, people_df, remove_status, remove_step):
    """
    Processes pipeline instances by filtering out specified statuses and \
        steps, and optionally merges with people data.

    This function filters the input DataFrame based on specified statuses \
        and steps to remove, sorts the remaining
    data by the 'Step' column, and if a people DataFrame is provided, it \
        merges the filtered data with the people
    DataFrame based on a set of required columns.

    Parameters:
    df (pandas.DataFrame): The DataFrame containing pipeline instances to process.
    people_df (pandas.DataFrame): The DataFrame containing people data to \
        merge with the pipeline instances.
    remove_status (list): A list of statuses to remove from the pipeline instances DataFrame.
    remove_step (list): A list of steps to remove from the pipeline instances DataFrame.

    Returns:
    pandas.DataFrame or None: The processed DataFrame after filtering and \
        optional merging, or None if the input DataFrame is None.
    """
    try:
        if df is not None:
            df = df[~df["Status"].isin(remove_status)]
            df = df[~df["Step"].isin(remove_step)].sort_values("Step", ascending=True)

            if people_df is not None:
                required_columns = [
                    "Reach ID",
                    "First Name",
                    "Preferred Name",
                    "Middle Name",
                    "Last Name",
                    "Suffix",
                    "Phone Country Code",
                    "Phone",
                    "Email",
                    "Address Line 1",
                    "Address Line 2",
                    "City",
                    "State",
                    "Zip",
                ]
                people_df = people_df[required_columns]

                merged_df = pd.merge(df, people_df, on="Reach ID", how="left")

                merged_df["Created Timestamp"] = pd.to_datetime(
                    merged_df["Created Timestamp"]
                ).dt.date
                merged_df["Updated Timestamp"] = pd.to_datetime(
                    merged_df["Updated Timestamp"]
                ).dt.date
                merged_df["Recorded Timestamp"] = pd.to_datetime(
                    merged_df["Recorded Timestamp"]
                ).dt.date

                return merged_df
    except Exception as e:
        st.error(f"An error occurred during pipeline processing: {e}")

    return None


tab1, tab2, tab3, tab4 = st.tabs(
    ["Contact Actions", "People", "Pipeline Instances", "Pivot Tables"]
)

######################################

with tab1:
    uploaded_file = st.file_uploader(
        "Upload Contact Actions Sheet Downloaded From Reach", type=["csv", "xlsx"]
    )
    remove_action_types = [
        "Person Added",
        "Up Vote",
        "Updated Address",
        "Updated Name",
        "Mark as Wrong",
        "Opt Out",
        "External Message",
    ]
    if uploaded_file:
        original_df = read_file(uploaded_file)
        df = process_file(original_df, remove_action_types, "Action Type")
        if df is not None:
            email_addresses = df[
                df["Contact Info Value"].astype(str).str.contains("@", na=False)
            ]["Contact Info Value"]
            df["Contact Info Value"] = df["Contact Info Value"].apply(
                lambda x: "" if x in email_addresses.values else x
            )
            df["Email"] = email_addresses
            df = df.rename(columns={"Contact Info Value": "Phone"})
            df["Combined Name"] = df["User First Name"] + " " + df["User Last Name"]
        if df is not None and st.button("Save Contact Actions File"):
            save_file(df, "xx_to_xx_Contact_Actions_Export.csv")

######################################

with tab2:
    uploaded_file = st.file_uploader(
        "Upload People Sheet Downloaded From Reach", type=["csv", "xlsx"]
    )
    remove_reach_add = ["Reach Add"]
    if uploaded_file:
        original_df = read_file(uploaded_file)
        if original_df is not None:
            df = process_file(original_df, remove_reach_add, "Source Tag")
            if df is not None and st.button("Save People File"):
                save_excel_with_sheets(original_df, df, "xx_to_xx_People_Export.xlsx")
                save_file(df, "xx_to_xx_People_Export_EA_Upload.csv")

######################################

with tab3:
    uploaded_file = st.file_uploader(
        "Upload Pipeline Instances Sheet Downloaded From Reach", type=["csv", "xlsx"]
    )
    people_file = st.file_uploader(
        "Upload People Sheet for Merge", type=["csv", "xlsx"]
    )
    remove_status = ["canceled"]
    remove_step = ["initial", "linkSentViaEmail", "linkSentViaMessaging"]
    if uploaded_file and people_file:
        pipeline_df = read_file(uploaded_file)
        people_df = read_file(people_file)
        if pipeline_df is not None and people_df is not None:
            df = process_pipeline_instances(
                pipeline_df, people_df, remove_status, remove_step
            )
            if df is not None and st.button("Save Pipeline Instances File"):
                st.download_button(df, "xx_to_xx_Pipeline_Instances_Export.csv")
                save_file(df, "xx_to_xx_Pipeline_Instances_Export.csv")

with tab4:
    st.write("Work in Progress...")

# import streamlit as st 
# import os
# import pandas as pd
# import platform

# st.title('RISE Data Sheet Processor')

# def process_file(uploaded_file, remove_types, column_name):
#     if uploaded_file is not None:
#         if uploaded_file.type == 'text/csv':
#             df = pd.read_csv(uploaded_file)
#         elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
#             df = pd.read_excel(uploaded_file)
        
#         #st.dataframe(df)
#         st.write('Original Row Count:', df.shape[0])
        
#         df = df[~df[column_name].isin(remove_types)].sort_values(column_name, ascending=True)

#         #st.dataframe(df)
#         st.write('Post-Processing Row Count:', df.shape[0])
        
#         return df

# # def excel_copy(uploaded_file):
# #     df_copy = None
# #     if uploaded_file is not None:
# #         if uploaded_file.type == 'text/csv':
# #             df_copy = pd.read_csv(uploaded_file)
# #         elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
# #             df_copy = pd.read_excel(uploaded_file)
# #     with pd.ExcelWriter('xx_to_xx_People_Export.xlsx') as writer:  
# #         df_copy.to_excel(writer, sheet_name='PTG')
    
# #     return df_copy


# def save_file(df, filename):
#     df.to_csv(filename, index=False)
#     st.write('File Saved')
#     if platform.system() == "Windows":
#         os.startfile(filename)
#     elif platform.system() == "Darwin":
#         os.system(f'open {filename}')

# tab1, tab2, tab3 = st.tabs(['Contact Actions', 'People', 'Pipeline Instances'])

# with tab1:
#     uploaded_file = st.file_uploader('Upload Contact Actions Sheet Downloaded From Reach', type=['csv', 'xlsx'])
#     remove_action_types = ['Person Added', 'Up Vote', 'Updated Address', 'Updated Name', 'Mark as Wrong', 'Opt Out', 'External Message']
#     df = process_file(uploaded_file, remove_action_types, 'Action Type')
#     if df is not None:
#         # Highlight all the email addresses
#         email_addresses = df[df['Contact Info Value'].astype(str).str.contains('@', na=False)]['Contact Info Value']

#         # Assuming the column to paste the cut cells is 'AE2'
#         df['Contact Info Value'] = df['Contact Info Value'].apply(lambda x: '' if x in email_addresses.values else x)
#         df['Email'] = email_addresses

#         # Rename the "Contact Info Value" column to "Phone"
#         df = df.rename(columns={'Contact Info Value': 'Phone'})

#         # Enter the formula in Cell AF2
#         df['Combined Name'] = df['User First Name'] + ' ' + df['User Last Name']

#     if df is not None and st.button('Save Contact Actions File'):
#         save_file(df, 'xx_to_xx_Contact_Actions_Export.csv')

# with tab2:
#     uploaded_file = st.file_uploader('Upload People Sheet Downloaded From Reach', type=['csv', 'xlsx'])
#     remove_reach_add = ['Reach Add']
#     # df_copy = excel_copy(uploaded_file)
#     df = process_file(uploaded_file, remove_reach_add, 'Source Tag')

#     # with pd.ExcelWriter('xx_to_xx_People_Export.xlsx', mode='a', engine='openpyxl') as writer:  
#         # df.to_excel(writer, sheet_name='EA Upload')

#     if df is not None and st.button('Save People File'):
#         save_file(df, 'xx_to_xx_People_Export_EA_Upload.csv')

# with tab3:
#     uploaded_file = st.file_uploader('Upload Pipeline Instances Sheet Downloaded From Reach', type=['csv', 'xlsx'])
#     remove_status = ['canceled'] # 'waiting_for_voter', 'waiting_for_you', 
#     remove_step = ['initial', 'LinkSentViaEmail', 'LinkSentViaMessaging']
#     df = process_file(uploaded_file, remove_status, 'Status')
#     #############################
#     if df is not None:
#         df = df[~df['Step'].isin(remove_step)].sort_values('Step', ascending=True) 
    
#     if df is not None and st.button('Save Pipeline Instances File'):
#         save_file(df, 'xx_to_xx_Pipeline_Instances_Export.csv')

import streamlit as st 
import os
import pandas as pd
import platform

st.title('RISE Data Sheet Processor')

def read_file(uploaded_file):
    try:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
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
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return None

def process_file(df, remove_types, column_name):
    try:
        if df is not None:
            st.write('Original Row Count:', df.shape[0])
            
            if column_name not in df.columns:
                st.error(f"Column '{column_name}' not found in the file.")
                st.write("Available columns:", df.columns.tolist())
                return None
            
            df = df[~df[column_name].isin(remove_types)].sort_values(column_name, ascending=True)
            
            st.write('Post-Processing Row Count:', df.shape[0])
            
            return df
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")

    return None

def save_file(df, filename):
    df.to_csv(filename, index=False)
    st.write('File Saved')
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        os.system(f'open {filename}')

def save_excel_with_sheets(original_df, processed_df, filename):
    with pd.ExcelWriter(filename) as writer:  
        original_df.to_excel(writer, sheet_name='PTG', index=False)
        processed_df.to_excel(writer, sheet_name='EA Upload', index=False)
    st.write('File Saved')
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        os.system(f'open {filename}')

def process_pipeline_instances(df, people_df, remove_status, remove_step):
    try:
        if df is not None:
            df = df[~df['Status'].isin(remove_status)]
            df = df[~df['Step'].isin(remove_step)].sort_values('Step', ascending=True)
            
            if people_df is not None:
                required_columns = ['Reach ID', 'First Name', 'Preferred Name', 'Middle Name', 'Last Name', 'Suffix', 'Phone Country Code', 'Phone', 'Email', 'Address Line 1', 'Address Line 2', 'City', 'State', 'Zip']
                people_df = people_df[required_columns]
                
                merged_df = pd.merge(df, people_df, on='Reach ID', how='left')

                merged_df['Created Timestamp'] = pd.to_datetime(merged_df['Created Timestamp']).dt.date
                merged_df['Updated Timestamp'] = pd.to_datetime(merged_df['Updated Timestamp']).dt.date
                merged_df['Recorded Timestamp'] = pd.to_datetime(merged_df['Recorded Timestamp']).dt.date

                return merged_df
    except Exception as e:
        st.error(f"An error occurred during pipeline processing: {e}")

    return None

tab1, tab2, tab3, tab4 = st.tabs(['Contact Actions', 'People', 'Pipeline Instances', 'Pivot Tables'])

######################################

with tab1:
    uploaded_file = st.file_uploader('Upload Contact Actions Sheet Downloaded From Reach', type=['csv', 'xlsx'])
    remove_action_types = ['Person Added', 'Up Vote', 'Updated Address', 'Updated Name', 'Mark as Wrong', 'Opt Out', 'External Message']
    if uploaded_file:
        original_df = read_file(uploaded_file)
        df = process_file(original_df, remove_action_types, 'Action Type')
        if df is not None:
            email_addresses = df[df['Contact Info Value'].astype(str).str.contains('@', na=False)]['Contact Info Value']
            df['Contact Info Value'] = df['Contact Info Value'].apply(lambda x: '' if x in email_addresses.values else x)
            df['Email'] = email_addresses
            df = df.rename(columns={'Contact Info Value': 'Phone'})
            df['Combined Name'] = df['User First Name'] + ' ' + df['User Last Name']
        if df is not None and st.button('Save Contact Actions File'):
            save_file(df, 'xx_to_xx_Contact_Actions_Export.csv')

######################################

with tab2:
    uploaded_file = st.file_uploader('Upload People Sheet Downloaded From Reach', type=['csv', 'xlsx'])
    remove_reach_add = ['Reach Add']
    if uploaded_file:
        original_df = read_file(uploaded_file)
        if original_df is not None:
            df = process_file(original_df, remove_reach_add, 'Source Tag')
            if df is not None and st.button('Save People File'):
                save_excel_with_sheets(original_df, df, 'xx_to_xx_People_Export.xlsx')
                save_file(df, 'xx_to_xx_People_Export_EA_Upload.csv')

######################################

with tab3:
    uploaded_file = st.file_uploader('Upload Pipeline Instances Sheet Downloaded From Reach', type=['csv', 'xlsx'])
    people_file = st.file_uploader('Upload People Sheet for Merge', type=['csv', 'xlsx'])
    remove_status = ['canceled']
    remove_step = ['initial', 'linkSentViaEmail', 'linkSentViaMessaging']
    if uploaded_file and people_file:
        pipeline_df = read_file(uploaded_file)
        people_df = read_file(people_file)
        if pipeline_df is not None and people_df is not None:
            df = process_pipeline_instances(pipeline_df, people_df, remove_status, remove_step)
            if df is not None and st.button('Save Pipeline Instances File'):
                save_file(df, 'xx_to_xx_Pipeline_Instances_Export.csv')

with tab4: 
    st.write('Work in Progress...')
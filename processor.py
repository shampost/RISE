import streamlit as st
import os
import pandas as pd
import platform

st.title('RISE Data Sheet Processor')

def process_file(uploaded_file, remove_types, column_name):
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            df = pd.read_excel(uploaded_file)
        
        st.dataframe(df)
        st.write('Row Count:', df.shape[0])
        
        df = df[~df[column_name].isin(remove_types)].sort_values(column_name, ascending=True)

        st.dataframe(df)
        st.write('Row Count:', df.shape[0])

        return df
    return None

def save_file(df, filename):
    df.to_csv(filename, index=False)
    st.write('File Saved')
    if platform.system() == "Windows":
        os.startfile(filename)
    elif platform.system() == "Darwin":
        os.system(f'open {filename}')

tab1, tab2, tab3 = st.tabs(['Contact Actions', 'People', 'Pipeline Instances'])

with tab1:
    uploaded_file = st.file_uploader('Upload Contact Actions Sheet Downloaded From Reach', type=['csv', 'xlsx'])
    remove_action_types = ['Person Added', 'Up Vote', 'Updated Address', 'Updated Name', 'Mark as Wrong', 'Opt Out', 'External Message']
    df = process_file(uploaded_file, remove_action_types, 'Action Type')
    if df is not None and st.button('Save Contact Actions File'):
        save_file(df, 'contact_actions_processed.csv')

with tab2:
    uploaded_file = st.file_uploader('Upload People Sheet Downloaded From Reach', type=['csv', 'xlsx'])
    remove_reach_add = ['Reach Add']
    df = process_file(uploaded_file, remove_reach_add, 'Source Tag')
    if df is not None and st.button('Save People File'):
        save_file(df, 'people_processed.csv')

with tab3:
    uploaded_file = st.file_uploader('Upload Pipeline Instances Sheet Downloaded From Reach', type=['csv', 'xlsx'])
    remove_status = ['waiting_for_voter', 'waiting_for_you', 'canceled']
    df = process_file(uploaded_file, remove_status, 'Status')
    if df is not None and st.button('Save Pipeline Instances File'):
        save_file(df, 'pipeline_instances_processed.csv')
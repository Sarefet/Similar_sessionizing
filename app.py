#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# %pip install streamlit plotly pandas


# In[1]:


import streamlit as st
import pandas as pd
import plotly.express as px
import glob
from utils import load_and_process_data, session_page_sequence, num_sessions, num_unique_visited_sites, median_session_length, most_visited_pages


# In[2]:


st.title("Sessionizing App")

# visitor_id will be much bigger with scale, so I leave him as a string in the below schema. 
#The URLs can be category as theres not many, and it saves on memory usage: 

schema = {
    "visitor_id": str,
    "site_url": "category",
    "page_view_url": "category",
    "timestamp": "int64"
}

column_names = ["visitor_id", "site_url", "page_view_url", "timestamp"]


# In[6]:


# Version for only 3 files:
#files = ["input_1.csv", "input_2.csv", "input_3.csv"]
#dfs = [pd.read_csv(file, names=column_names, dtype=schema) for file in files]

# Load and process data
csv_files = glob.glob('*.csv')
df_filtered, column_consistency_message, loaded_files = load_and_process_data(csv_files, column_names, schema)


# In[10]:


# Streamlit UI setup

st.header("Query Options")

# Display column consistency message
st.subheader("Column Consistency Check")
st.write(column_consistency_message)

# Display file loading status
if df_filtered.empty:
    st.write("No CSV files found or failed to load.")
else:
    st.write("CSV files loaded and processed successfully.")
    st.write("Loaded files:")
    for file in loaded_files:
        st.write(file)

# Only 3 queries
# query_option = st.selectbox("Select a query", ("Num Sessions", "Median Session Length", "Num Unique Visited Sites"))

# With bonus queries 
query_option = st.selectbox("Select a query", ("Num Sessions", "Median Session Length", "Num Unique Visited Sites", "Most Visited Pages", "Session Page Sequence"))

if query_option == "Num Sessions":
    site_url = st.text_input("Enter site URL")
    if st.button("Execute"):
        result = num_sessions(df_filtered, site_url)
        if result == "Site URL not found":
            st.error(result)
        else:
            st.write(f"Number of sessions for {site_url}: {result}")
elif query_option == "Median Session Length":
    site_url = st.text_input("Enter site URL")
    if st.button("Execute"):
        result = median_session_length(df_filtered, site_url)
        if result == "Site URL not found":
            st.error(result)
        else:
            st.write(f"Median session length for {site_url}: {result} seconds")
elif query_option == "Num Unique Visited Sites":
    visitor_id = st.text_input("Enter visitor ID")
    if st.button("Execute"):
        result = num_unique_visited_sites(df_filtered, visitor_id)
        if result == "Visitor ID not found":
            st.error(result)
        else:
            st.write(f"Number of unique visited sites for {visitor_id}: {result}")
elif query_option == "Most Visited Pages":  # Bonus query
    site_url = st.text_input("Enter site URL")
    if st.button("Execute"):
        result = most_visited_pages(df_filtered, site_url)
        if isinstance(result, str) and result == "Site URL not found":
            st.error(result)
        else:
            st.write(f"Most visited pages for {site_url}:")
            st.dataframe(result, use_container_width=True)
elif query_option == "Session Page Sequence":  # Bonus query
    visitor_id = st.text_input("Enter visitor ID")
    site_url = st.text_input("Enter site URL")
    session_id = st.number_input("Enter session ID", min_value=1, step=1)
    if st.button("Execute"):
        result = session_page_sequence(df_filtered, visitor_id, site_url, session_id)
        if isinstance(result, str) and (result == "Visitor ID not found" or result == "Site URL not found" or result == "Session ID not found"):
            st.error(result)
        else:
            st.write(f"Page sequence for visitor {visitor_id} on site {site_url} in session {session_id}:")
            st.dataframe(result, use_container_width=True)


# In[11]:


# Display final data that the queries use, and visualizations
st.header("Data")
st.dataframe(df_filtered, use_container_width=True)

st.header("Visualizations")

# Actual Session Length count BoxPlot
fig_session_length = px.box(df_filtered, y="actual_session_length")
fig_session_length.update_layout(
    title_text="Actual Session Length Distribution",
    yaxis_title="Length"
)
st.plotly_chart(fig_session_length)

# Grouping by 'session_id' and counting occurrences bar graph
session_id_counts = df_filtered.groupby('session_id').size().reset_index(name='counts')

fig_session_id = px.bar(session_id_counts, x='session_id', y='counts', labels={'counts': 'Count'})
fig_session_id.update_layout(
    title_text="Sessions Distribution",
    xaxis_title="Session IDs",
    yaxis_title="Count"
)
st.plotly_chart(fig_session_id)



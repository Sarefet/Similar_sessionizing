#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import streamlit as st

@st.cache_data
def load_and_process_data(csv_files, column_names, schema):
    # Check if there are any CSV files
    if not csv_files:
        print("No CSV files found.")
        return pd.DataFrame(), "No CSV files found.", []

    # Check column consistency
    column_counts = {}
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            column_counts[file] = len(df.columns)
        except Exception as e:
            return pd.DataFrame(), f"Error loading file {file} for column check: {e}", []

    # Check if all files have the same number of columns
    if len(set(column_counts.values())) == 1:
        column_consistency_message = "All files have the same number of columns."
    else:
        column_consistency_message = "Files have different number of columns:\n"
        for file, count in column_counts.items():
            column_consistency_message += f"{file}: {count} columns\n"

    # Load all CSV files
    dfs = []
    loaded_files = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, names=column_names, dtype=schema)
            dfs.append(df)
            loaded_files.append(file)
            print(f"Loaded file: {file}")
        except Exception as e:
            print(f"Error loading file {file}: {e}")

    # Concatenate, sort, and reset index
    df = pd.concat(dfs, ignore_index=True)
    df = df.dropna().drop_duplicates()
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    # Sort the DataFrame and reset the index
    df = df.sort_values(['timestamp', 'visitor_id', 'site_url', 'page_view_url']).reset_index(drop=True)

    # Process the DataFrame
    df['next_timestamp'] = df.groupby(['visitor_id', 'site_url'])['timestamp'].shift(-1)
    df['session_length'] = (df['next_timestamp'] - df['timestamp']).dt.total_seconds()
    df.loc[df['session_length'].isnull(), 'session_length'] = 0
    df['new_session'] = (df['session_length'] > 30*60).astype(int)
    df['session_id'] = df.groupby(['visitor_id', 'site_url'])['new_session'].cumsum() + 1

    # Calculate the actual session length as the difference between the first and last timestamp in each session
    df['session_start'] = df.groupby(['visitor_id', 'site_url', 'session_id'])['timestamp'].transform('min')
    df['session_end'] = df.groupby(['visitor_id', 'site_url', 'session_id'])['timestamp'].transform('max')
    df['actual_session_length'] = (df['session_end'] - df['session_start']).dt.total_seconds()

    df_filtered = df[df['actual_session_length'].notnull()]
    return df_filtered, column_consistency_message, loaded_files

def session_page_sequence(df_filtered, visitor_id, site_url, session_id):
    if df_filtered[df_filtered["visitor_id"] == visitor_id].empty:
        return "Visitor ID not found"
    if df_filtered[df_filtered["site_url"] == site_url].empty:
        return "Site URL not found"
    session_df = df_filtered[(df_filtered['visitor_id'] == visitor_id) & 
                             (df_filtered['site_url'] == site_url) & 
                             (df_filtered['session_id'] == session_id)]
    if session_df.empty:
        return "Session ID not found"
    return session_df[['timestamp', 'page_view_url']].sort_values('timestamp').reset_index(drop=True)

def num_sessions(df_filtered, site_url):
    if df_filtered[df_filtered["site_url"] == site_url].empty:
        return "Site URL not found"
    return df_filtered[df_filtered["site_url"] == site_url].groupby(['visitor_id', 'session_id']).ngroups

def num_unique_visited_sites(df_filtered, visitor_id):
    if df_filtered[df_filtered["visitor_id"] == visitor_id].empty:
        return "Visitor ID not found"
    return df_filtered[df_filtered["visitor_id"] == visitor_id]["site_url"].nunique()

def median_session_length(df_filtered, site_url):
    if df_filtered[df_filtered["site_url"] == site_url].empty:
        return "Site URL not found"
    session_lengths = df_filtered[df_filtered["site_url"] == site_url].drop_duplicates(subset=['visitor_id', 'site_url', 'session_id'])['actual_session_length']
    return session_lengths.median()

def most_visited_pages(df_filtered, site_url):
    if df_filtered[df_filtered["site_url"] == site_url].empty:
        return "Site URL not found"
    result = df_filtered[df_filtered["site_url"] == site_url]["page_view_url"].value_counts().head(5).reset_index()
    result.columns = ['page_view_url', 'count']  # Rename columns for clarity
    return result
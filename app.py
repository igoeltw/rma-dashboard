"""RMA Dashboard - Streamlit app for RMA tracking."""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.clean_data import (
    load_and_clean_data,
    get_status_distribution,
    get_time_in_status,
    get_longest_waiting,
    get_volume_over_time,
    get_categories,
)


st.set_page_config(page_title="RMA Dashboard", page_icon="🔧", layout="wide")

st.title("🔧 RMA Dashboard")
st.markdown("Track GPU node RMA status and workflow metrics")

JSON_PATH = "data/analyzed_RMA.json"

try:
    df = load_and_clean_data(JSON_PATH)
except FileNotFoundError:
    st.error(f"Data file not found: {JSON_PATH}")
    st.info("Run: tw-atlas pull --project RMA --output-dir data/rma")
    st.stop()

if df.empty:
    st.error("No data available")
    st.stop()

st.sidebar.header("Filters")

if "created" in df.columns:
    df = df.sort_values("created")
    min_date = df["created"].min().date()
    max_date = df["created"].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df = df[(df["created"].dt.date >= start_date) & (df["created"].dt.date <= end_date)]

if "status" in df.columns:
    statuses = ["All"] + sorted(df["status"].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("Status", statuses)
    if selected_status != "All":
        df = df[df["status"] == selected_status]

st.write(f"**Total RMA Tickets:** {len(df)}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Status Distribution")
    status_df = get_status_distribution(df)
    if not status_df.empty:
        fig = px.bar(
            status_df,
            x="count",
            y="status",
            orientation="h",
            title="Tickets by Status",
            labels={"status": "Status", "count": "Count"},
            color="count",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No status data available")

with col2:
    st.subheader("Time in Status")
    time_df = get_time_in_status(df)
    if not time_df.empty:
        fig2 = px.bar(
            time_df,
            x="status",
            y="avg_days",
            title="Average Days in Status",
            labels={"status": "Status", "avg_days": "Avg Days"},
            color="avg_days",
            color_continuous_scale="RdYlGn_r"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No time data available")

st.subheader("Stalled Tickets (>7 days)")
stalled = df[df.get("days_in_status", 0) > 7][["key", "summary", "status", "days_in_status"]]
if not stalled.empty:
    st.write(f"**{len(stalled)} tickets stalled**")
    st.dataframe(stalled.sort_values("days_in_status", ascending=False), use_container_width=True)
else:
    st.write("No stalled tickets")

st.subheader("Longest Waiting Tickets")
longest = get_longest_waiting(df, 20)
if not longest.empty:
    st.dataframe(longest, use_container_width=True)
else:
    st.info("No time data available")

st.subheader("RMA Volume Over Time")
volume_df = get_volume_over_time(df)
if not volume_df.empty:
    fig3 = px.line(
        volume_df,
        x="created_date",
        y="count",
        title="RMAs Created Over Time",
        labels={"created_date": "Date", "count": "New RMAs"}
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No date data available")

st.subheader("Root Cause Categories")
cat_df = get_categories(df)
if not cat_df.empty:
    fig4 = px.pie(
        cat_df,
        values=cat_df.columns[1],
        names=cat_df.columns[0],
        title="Issues by Category",
        hole=0.4
    )
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No category data available (run Timmy analysis to populate)")
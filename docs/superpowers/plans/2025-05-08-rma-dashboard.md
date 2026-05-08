# RMA Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a Streamlit dashboard for tracking GPU node RMA workflow, displaying status distribution, time-in-status metrics, longest-waiting tickets, root cause categories, and volume trends.

**Architecture:** Single-page Streamlit app with sidebar filters. Data loaded from CSV, transformed in-memory. Visualizations via Plotly.

**Tech Stack:** Streamlit, Pandas, Plotly, Python 3.9+

---

## File Structure

```
rma-dashboard/
├── app.py                    # Main dashboard (entry point)
├── requirements.txt          # Dependencies
├── README.md                # Quick start
├── data/                    # Data files
│   └── cleaned_rmas.csv    # Combined RMA data (source of truth)
└── src/
    ├── __init__.py
    └── clean_data.py       # Data cleaning & transformation
```

---

### Task 1: Set up project structure

**Files:**
- Create: `rma-dashboard/requirements.txt`
- Create: `rma-dashboard/src/__init__.py`
- Create: `rma-dashboard/src/clean_data.py`

- [ ] **Step 1: Create requirements.txt**

```txt
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
```

- [ ] **Step 2: Create src/__init__.py**

```python
"""RMA Dashboard package."""
```

- [ ] **Step 3: Create src/clean_data.py**

```python
"""Data cleaning and transformation for RMA dashboard."""

import pandas as pd
from datetime import datetime


def load_and_clean_data(csv_path: str = "data/cleaned_rmas.csv") -> pd.DataFrame:
    """Load and clean RMA ticket data."""
    df = pd.read_csv(csv_path)
    
    # Parse dates
    date_cols = ["created", "updated"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    
    # Calculate days in current status
    if "created" in df.columns and "updated" in df.columns:
        df["days_in_status"] = (df["updated"] - df["created"]).dt.days
    
    return df


def get_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get count of tickets per status."""
    if "status" not in df.columns:
        return pd.DataFrame()
    return df["status"].value_counts().reset_index()


def get_longest_waiting(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Get tickets that have been in RMA longest."""
    if "days_in_status" not in df.columns:
        return pd.DataFrame()
    return df.nlargest(n, "days_in_status")[["key", "summary", "status", "days_in_status", "created"]]
```

- [ ] **Step 4: Commit**

```bash
cd rma-dashboard
git add requirements.txt src/
git commit -m "Add project structure and basic data cleaning"
```

---

### Task 2: Build main dashboard with status distribution

**Files:**
- Modify: `rma-dashboard/app.py`

- [ ] **Step 1: Write basic app.py with status distribution**

```python
"""RMA Dashboard - Streamlit app for RMA tracking."""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.clean_data import load_and_clean_data, get_status_distribution


st.set_page_config(page_title="RMA Dashboard", page_icon="🔧", layout="wide")

st.title("🔧 RMA Dashboard")
st.markdown("Track GPU node RMA status and workflow metrics")

# Load data
DATA_PATH = "data/cleaned_rmas.csv"

try:
    df = load_and_clean_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"Data file not found: {DATA_PATH}")
    st.info("Run: tw-atlas pull --project RMA --output-dir data/rma")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

# Vendor filter (from issuetype)
if "issuetype" in df.columns:
    vendors = ["All"] + list(df["issuetype"].dropna().unique())
    selected_vendor = st.sidebar.selectbox("Vendor", vendors)
    if selected_vendor != "All":
        df = df[df["issuetype"] == selected_vendor]

# Status filter
if "status" in df.columns:
    statuses = ["All"] + list(df["status"].dropna().unique())
    selected_status = st.sidebar.selectbox("Status", statuses)
    if selected_status != "All":
        df = df[df["status"] == selected_status]

st.write(f"**Total RMA Tickets:** {len(df)}")

# Status distribution chart
st.subheader("Status Distribution")
status_df = get_status_distribution(df)
if not status_df.empty:
    fig = px.bar(
        status_df,
        x="status",
        y="count",
        orientation="h",
        title="Tickets by Status",
        labels={"status": "Status", "count": "Count"},
        color="count",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No status data available")
```

- [ ] **Step 2: Run test**

Run: `cd rma-dashboard && python3 -m streamlit run app.py`
Expected: Error about missing data file (expected)

- [ ] **Step 3: Commit**

```bash
git add app.py
git commit -m "Add basic dashboard with status distribution"
```

---

### Task 3: Add Time in Status metrics

**Files:**
- Modify: `rma-dashboard/app.py`
- Modify: `rma-dashboard/src/clean_data.py`

- [ ] **Step 1: Add time_in_status to clean_data.py**

```python
def get_time_in_status(df: pd.DataFrame) -> pd.DataFrame:
    """Get tickets grouped by status with average days."""
    if "status" not in df.columns or "days_in_status" not in df.columns:
        return pd.DataFrame()
    
    result = df.groupby("status").agg(
        count=("key", "count"),
        avg_days=("days_in_status", "mean"),
        max_days=("days_in_status", "max")
    ).reset_index()
    
    return result.sort_values("count", ascending=False)
```

- [ ] **Step 2: Add Time in Status section to app.py**

```python
# Time in Status section
st.subheader("Time in Status")
time_df = get_time_in_status(df)
if not time_df.empty:
    # Color code: green < 7 days, yellow 7-14, red > 14
    def color_days(days):
        if pd.isna(days):
            return "gray"
        if days < 7:
            return "green"
        if days < 14:
            return "yellow"
        return "red"
    
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
    
    # Highlight stalled (> 7 days)
    stalled = df[df["days_in_status"] > 7][["key", "summary", "status", "days_in_status"]]
    st.markdown(f"**Stalled Tickets (>7 days):** {len(stalled)}")
    if not stalled.empty:
        st.dataframe(stalled.sort_values("days_in_status", ascending=False), use_container_width=True)
```

- [ ] **Step 3: Commit**

```bash
git add app.py src/clean_data.py
git commit -m "Add time in status metrics and stalled tickets"
```

---

### Task 4: Add Longest Waiting table

**Files:**
- Modify: `rma-dashboard/app.py`

- [ ] **Step 1: Add longest waiting section**

```python
# Longest Waiting section
st.subheader("Longest Waiting Tickets")
longest = df.nlargest(20, "days_in_status")[["key", "summary", "status", "days_in_status", "created"]]
if not longest.empty:
    st.dataframe(longest, use_container_width=True)
else:
    st.info("No time data available")
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "Add longest waiting tickets table"
```

---

### Task 5: Add Root Cause Categories (Timmy analysis)

**Files:**
- Modify: `rma-dashboard/app.py`
- Modify: `rma-dashboard/src/clean_data.py`

- [ ] **Step 1: Add category helpers to clean_data.py**

```python
def get_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Get ticket counts by root cause category."""
    cat_col = None
    for col in ["timmy_category", "category", "root_cause_category"]:
        if col in df.columns:
            cat_col = col
            break
    
    if not cat_col:
        return pd.DataFrame()
    
    return df[cat_col].value_counts().reset_index()
```

- [ ] **Step 2: Add Categories section to app.py**

```python
# Root Cause Categories
st.subheader("Root Cause Categories")
cat_df = get_categories(df)
if not cat_df.empty:
    fig3 = px.pie(
        cat_df,
        values=cat_df.columns[1],
        names=cat_df.columns[0],
        title="Issues by Category",
        hole=0.4
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No category data available (run Timmy analysis to populate)")
```

- [ ] **Step 3: Commit**

```bash
git add app.py src/clean_data.py
git commit -m "Add root cause categories visualization"
```

---

### Task 6: Add RMA Volume over time

**Files:**
- Modify: `rma-dashboard/app.py`

- [ ] **Step 1: Add volume chart**

```python
# RMA Volume over time
st.subheader("RMA Volume Over Time")
if "created" in df.columns:
    df["created_date"] = df["created"].dt.date
    volume = df.groupby("created_date").size().reset_index(name="count")
    
    fig4 = px.line(
        volume,
        x="created_date",
        y="count",
        title="RMAs Created Over Time",
        labels={"created_date": "Date", "count": "New RMAs"}
    )
    st.plotly_chart(fig4, use_container_width=True)
```

- [ ] **Step 2: Commit**

```bash
git add app.py
git commit -m "Add RMA volume over time chart"
```

---

### Task 7: Add sample data and verify

**Files:**
- Create: `rma-dashboard/data/cleaned_rmas.csv`

- [ ] **Step 1: Pull real data (after user runs tw-atlas)**

- [ ] **Step 2: Commit**

---

## Execution

**Plan complete and saved to `docs/superpowers/plans/2025-05-08-rma-dashboard.md`. Two execution options:**

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
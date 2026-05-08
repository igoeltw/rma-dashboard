# RMA Dashboard

Streamlit-based dashboard for tracking GPU node RMA (Return Merchandise Authorization) status. Provides insights into RMA workflow stages, bottlenecks, and root cause analysis.

## Quick Start

```bash
git clone https://github.com/igoeltw/rma-dashboard.git
cd rma-dashboard
pip install streamlit pandas plotly
python3 -m streamlit run app.py
```

Then open **http://localhost:8501** (or 8502 if already in use).

---

## How It Works

### End-to-End Data Pipeline

```
Jira RMA Board  →  tw-atlas pull  →  flattened_RMA.json  →  tw-atlas analyze  →  analyzed_RMA.json  →  Dashboard
```

| Step | Command | Description |
|------|---------|-------------|
| **1. Pull** | `tw-atlas pull --project RMA --output-dir data` | Fetches all tickets from Jira RMA board and flattens them to JSON |
| **2. Analyze** | `tw-atlas analyze -i data/flattened_RMA.json -o data/analyzed_RMA.json --project-type rma` | Uses Timmy (AI) to categorize root causes, symptoms, affected components |
| **3. Visualize** | `python3 -m streamlit run app.py` | Displays metrics in Streamlit dashboard |

### What Data Gets Analyzed

Each RMA ticket is analyzed for:
- **Category** - Root cause (GPU Failure, Power Supply, Cooling/Thermal, etc.)
- **Affected Component** - Which hardware failed
- **Symptom** - What was observed
- **Root Cause** - Why it failed
- **Resolution** - How it was resolved
- **Vendor** - Supplier (Supermicro, EdgeCore, Other)

### Current Data

- **658 analyzed RMA tickets** (June 2025 - May 2026)
- Categories include: GPU Failure (172), GPU Memory/VRAM (130), Power Supply (72), Motherboard/PCB (50), No Issue Found (47), Cooling/Thermal (42), Network Card (39), SSD/NVMe (38), and more

---

## Dashboard Features

- **Date Range Filter** - Filter by ticket creation date
- **Status Filter** - Filter by RMA workflow stage
- **Status Distribution** - Bar chart of tickets per status
- **Time in Status** - Average days per status, identify bottlenecks
- **Stalled Tickets** - Tickets stuck >7 days highlighted
- **Longest Waiting** - Top 20 tickets by time in RMA
- **Volume Over Time** - Trend of RMAs created
- **Root Cause Categories** - Pie chart of issue types

---

## Refreshing Data

To get latest tickets from Jira:

```bash
# 1. Pull new tickets
cd ../tensorwave-atlassian-automation
tw-atlas pull --project RMA --output-dir data

# 2. Analyze with Timmy (use --project-type rma for hardware categories)
tw-atlas analyze -i data/flattened_RMA.json -o ../rma-dashboard/data/analyzed_RMA.json --model timothy-ishika --project-type rma

# 3. Restart dashboard
cd ../rma-dashboard
python3 -m streamlit run app.py
```

---

## Tech Stack

- **Dashboard**: Streamlit
- **Data**: Pandas, JSON
- **Visualization**: Plotly
- **Analysis**: Timmy (Tensorwave AI)
- **Source**: Jira RMA board via tensorwave-atlassian-automation
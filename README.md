# RMA Dashboard

Streamlit-based dashboard for tracking GPU node RMA (Return Merchandise Authorization) status. Provides insights into RMA workflow stages, bottlenecks, and root cause analysis.

## Quick Start

```bash
git clone https://github.com/igoeltw/rma-dashboard.git
cd rma-dashboard
pip install streamlit pandas plotly
python3 -m streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## Data Source

This dashboard comes pre-loaded with **658 analyzed RMA tickets** including:
- Status, timestamps, node names
- Timmy categories: Hardware Failure (551), GPU Firmware (91), Storage (6), etc.

To refresh data:

```bash
cd ../tensorwave-atlassian-automation
tw-atlas pull --project RMA --output-dir data/rma
tw-atlas analyze -i data/flattened_RMA.json -o data/analyzed_RMA.json --model timothy-ishika
```

## Tech Stack

- Streamlit
- Pandas
- Plotly
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

This dashboard visualizes data from the Jira RMA board. To refresh data:

```bash
cd ../tensorwave-atlassian-automation
tw-atlas pull --project RMA --output-dir data/rma
```

## Tech Stack

- Streamlit
- Pandas
- Plotly
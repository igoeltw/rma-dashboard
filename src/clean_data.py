"""Data cleaning and transformation for RMA dashboard."""

import pandas as pd
from datetime import datetime


def load_and_clean_data(json_path: str = "data/analyzed_RMA.json") -> pd.DataFrame:
    """Load and clean RMA ticket data from analyzed JSON (with Timmy categories)."""
    import json
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    date_cols = ["created", "updated"]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce", utc=True)
    
    if "created" in df.columns and "updated" in df.columns:
        df["days_in_status"] = (df["updated"].dt.tz_localize(None) - df["created"].dt.tz_localize(None)).dt.days
    
    if "summary" in df.columns:
        df["node_name"] = df["summary"].str.extract(r'^([a-z0-9\-]+)', flags=0)
    
    return df


def get_status_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get count of tickets per status."""
    if "status" not in df.columns:
        return pd.DataFrame()
    return df["status"].value_counts().reset_index()


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


def get_longest_waiting(df: pd.DataFrame, n: int = 20) -> pd.DataFrame:
    """Get tickets that have been in RMA longest."""
    if "days_in_status" not in df.columns:
        return pd.DataFrame()
    return df.nlargest(n, "days_in_status")[["key", "summary", "status", "days_in_status", "created"]]


def get_volume_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Get RMA volume by date."""
    if "created" not in df.columns:
        return pd.DataFrame()
    df_copy = df.copy()
    df_copy["created_date"] = df_copy["created"].dt.date
    return df_copy.groupby("created_date").size().reset_index(name="count")


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
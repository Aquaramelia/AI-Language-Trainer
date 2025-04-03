import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_helpers import load_css, set_background
from database.db_helpers_exercises import get_practice_data


st.set_page_config(page_title="Home - chart", page_icon="📖", layout="wide")

load_css()
set_background()

# Fetch practice data
data = get_practice_data(user_id=1)

if data.empty:
    st.write("No data available for the heatmap.")
else:
    # Ensure date is in correct format
    data["date"] = pd.to_datetime(data["date"])

    # Extract year, week number, and weekday
    data["week_start"] = data["date"] - pd.to_timedelta(data["date"].dt.weekday, unit='D')  # Monday of the week
    data["week_range"] = data["week_start"].dt.strftime("%d/%m") + " - " + (data["week_start"] + pd.Timedelta(days=6)).dt.strftime("%d/%m")
    data["weekday"] = data["date"].dt.weekday  # Monday = 0, Sunday = 6
    data["weekday_name"] = data["date"].dt.day_name()

    # Create full week range (all Mondays in the year)
    min_date = pd.to_datetime("2025-01-01")  
    max_date = pd.to_datetime("2025-12-31")  

    all_mondays = pd.date_range(start=min_date, end=max_date, freq="W-MON")
    all_week_ranges = [f"{monday.strftime('%d/%m')} - {(monday + pd.Timedelta(days=6)).strftime('%d/%m')}" for monday in all_mondays]
    
    all_week_df = pd.DataFrame({"week_start": all_mondays, "week_range": all_week_ranges})

    # Ensure all weekdays (Monday-Sunday) exist in each week
    weekdays = pd.DataFrame({"weekday": np.arange(7), "weekday_name": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]})

    # Create full cartesian product (all weeks × all weekdays)
    full_weeks = all_week_df.merge(weekdays, how="cross")

    # Merge full dataset with database data
    full_data_filled = full_weeks.merge(data[["week_range", "weekday", "practice_count"]], 
                                        on=["week_range", "weekday"], how="left")

    # Fill missing practice counts with 0
    full_data_filled["practice_count"] = full_data_filled["practice_count"].fillna(0)

    # Compute exact date for each cell
    full_data_filled["exact_date"] = full_data_filled["week_start"] + pd.to_timedelta(full_data_filled["weekday"], unit="D")
    full_data_filled["exact_date_str"] = full_data_filled["exact_date"].dt.strftime("%A, %d/%m")

    # Pivot for heatmap
    pivoted_data = full_data_filled.pivot(index="weekday_name", columns="week_range", values="practice_count")
    customdata = full_data_filled.pivot(index="weekday_name", columns="week_range", values="exact_date_str")

    # Ensure correct row order (Monday-Sunday)
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivoted_data = pivoted_data.reindex(index=weekday_order)
    customdata = customdata.reindex(index=weekday_order)

    # Ensure column order matches all_week_ranges
    pivoted_data = pivoted_data.reindex(columns=all_week_ranges)
    customdata = customdata.reindex(columns=all_week_ranges)

    # Convert customdata to NumPy array for correct hover tooltips
    customdata_np = customdata.to_numpy()

    # Create heatmap
    fig = px.imshow(
        pivoted_data,
        labels=dict(x="Week", y="Day", color="Exercises"),
        x=all_week_ranges,
        y=weekday_order,
        color_continuous_scale="Purples_r",
        title="Your progress over time"
    )

    # Update hover tooltips to show exact date
    fig.update_traces(
        hovertemplate="Week: %{x}<br>Date: %{customdata}<br>Exercises: %{z}<extra></extra>",
        customdata=customdata_np
    )

    # Improve layout
    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        title_x=0.1
    )

    # Rotate x-axis labels
    fig.update_xaxes(tickangle=45)

    # Display heatmap in Streamlit
    with st.container(key="heatmap-container"):
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

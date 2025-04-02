import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_helpers import load_css, set_background
from database.db_helpers_exercises import get_practice_data

st.set_page_config(page_title="Home - chart", page_icon="📖", layout="wide")

load_css()
set_background()

# Generate dummy data
# date_range = pd.date_range(start="2024-01-01", end="2024-12-31")
data = get_practice_data(user_id=1)

if data.empty:
    st.write("No data available for the heatmap.")
else:
    # Extract year, week number, and weekday to position the heatmap
    data["year"] = data["date"].dt.year
    data["week_start"] = data["date"] - pd.to_timedelta(data["date"].dt.weekday, unit='D')  # Get Monday of the week
    data["week_range"] = data["week_start"].dt.strftime("%d/%m") + " - " + (data["week_start"] + pd.Timedelta(days=6)).dt.strftime("%d/%m")

    # Convert date to weeks for columns
    week_labels = data.drop_duplicates(subset="week_range")[["week_range", "week_start"]].sort_values("week_start")

    # Convert to correct datetime
    data["date"] = pd.to_datetime(data["date"])
    data["weekday"] = data["date"].dt.weekday

    # Generate the date for each weekday in the week range
    data["weekday_date"] = data["week_start"] + pd.to_timedelta(data["weekday"], unit='D')

    # Convert weekday_date to string format for the tooltip (e.g., "01/01" or "1 January")
    data["weekday_date_str"] = data["weekday_date"].dt.strftime("%d/%m")
    
    # Create a full set of weeks for the year (52 or 53 weeks)
    full_week_range = pd.date_range(start=f"{data['year'].min()}-01-01", end=f"{data['year'].max()}-12-31", freq="W-MON")
    full_week_range = full_week_range.to_frame(index=False, name="week_start")
    full_week_range["week_range"] = full_week_range["week_start"].dt.strftime("%d/%m") + " - " + (full_week_range["week_start"] + pd.Timedelta(days=6)).dt.strftime("%d/%m")
    
    # Merge with the actual data to ensure all weeks are included
    full_data = pd.merge(full_week_range, data, on="week_range", how="left")

    # Pivot the data
    pivoted_data = full_data.pivot(index="weekday", columns="week_range", values="practice_count").fillna(0)
    
    # Ensure pivoted_data has 7 rows (for 7 days of the week)
    if pivoted_data.shape[0] < 7:
        # Add missing rows for any days not in the data (fill with zeros or None)
        missing_days = 7 - pivoted_data.shape[0]
        pivoted_data = pd.concat([pivoted_data, pd.DataFrame(np.zeros((missing_days, pivoted_data.shape[1])), columns=pivoted_data.columns)], axis=0)
        
    # Create a full set of week ranges for the year
    all_week_ranges = full_week_range["week_range"].tolist()
    print(all_week_ranges)

    # Create a 2D array of dates corresponding to the heatmap's cells
    customdata = np.empty((7, pivoted_data.shape[1]), dtype="object")

    # Loop through weeks and assign the weekday_date_str to customdata
    for i, week_range in enumerate(all_week_ranges):
        # Extract the week's data
        week_data = full_data[full_data["week_range"] == week_range].sort_values("weekday")
        
        # Check if the length of week_data matches the number of days (7)
        if len(week_data) == 7:
            customdata[:, i] = week_data["weekday_date_str"].values
        else:
            # If there are missing days, fill with None or an appropriate value
            customdata[:, i] = np.concatenate([week_data["weekday_date_str"].values, [None]*(7-len(week_data))])
    
    # Adjust the order of the y-axis labels to match weekdays correctly
    y_labels = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    # Create the heatmap
    fig = px.imshow(
        pivoted_data,
        labels=dict(x="Week", y="Day", color="Exercises"),
        x=all_week_ranges,  # Display date ranges instead of week numbers
        y=y_labels, # Days as y-axis
        color_continuous_scale="Purples_r",
        title="Your progress over time"
    )

    fig.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the plot area
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background for the whole paper area
        title_x=0.1,
        # title_y=0.85,  # Moves the title closer to the chart (default is 0.95)
        # title_yanchor="top",  # Ensures the title is anchored from the top
    )

    # Add hover tooltips with the date next to the day
    fig.update_traces(
        hovertemplate="Week: %{x}<br>Date: %{y}, %{customdata}<br>Exercises: %{z}<extra></extra>",
        customdata=customdata
    )

    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)

    with st.container(key="heatmap-container"):
        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

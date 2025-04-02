import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Home - chart", page_icon="📖", layout="wide")

# Generate dummy data (replace with your actual data)
date_range = pd.date_range(start="2024-01-01", end="2024-12-31")
data = pd.DataFrame({
    "date": date_range,
    "answers": np.random.randint(0, 10, size=len(date_range))  # Random activity levels
})

# Extract year, week number, and weekday to position the heatmap
data["year"] = data["date"].dt.year
data["week_start"] = data["date"] - pd.to_timedelta(data["date"].dt.weekday, unit='D')  # Get Monday of the week
data["week_range"] = data["week_start"].dt.strftime("%d/%m") + " - " + (data["week_start"] + pd.Timedelta(days=6)).dt.strftime("%d/%m")

# Convert date to weeks for columns
week_labels = data.drop_duplicates(subset="week_range")[["week_range", "week_start"]].sort_values("week_start")

data["date"] = pd.to_datetime(data["date"])
data["weekday"] = data["date"].dt.weekday

weekday_dates = []
for index, row in data.iterrows():
    weekday_dates.append(row["week_start"] + pd.Timedelta(days=row["weekday"]))

data["weekday_date"] = weekday_dates

# Pivot the data
pivoted_data = data.pivot(index="weekday", columns="week_range", values="answers").fillna(0)

# Create a 2D array of dates corresponding to the heatmap's cells
customdata = np.array([data.groupby(["weekday", "week_range"])["weekday_date"].first().reset_index()["weekday_date"].values.tolist()] * len(pivoted_data.columns))

# Create the heatmap
fig = px.imshow(    
    pivoted_data,
    labels=dict(x="Week", y="Day", color="Answers"),
    x=week_labels["week_range"],  # Display date ranges instead of week numbers
    y=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],  # Days as y-axis
    color_continuous_scale="Purples",
    title="User Question Answers Over Time"
)

# Add hover tooltips with the date next to the day
fig.update_traces(
    hovertemplate="Week: %{x}<br>Day: %{y}<br>Date: %{customdata[0]}<br>Answers: %{z}",
    customdata=customdata
)

# Rotate x-axis labels for better readability
fig.update_xaxes(tickangle=45)

# Display in Streamlit
st.plotly_chart(fig, use_container_width=True)
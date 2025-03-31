import streamlit as st
import easychart
from custom_easychart import rendering

# Ensure the chart is responsive
easychart.config.rendering.responsive = True
easychart.config.theme = "easychart"

# Define labels and values
labels = ["O", "A", "B", "AB"]
values = [45, 40, 11, 4]

# Create a donut (pie) chart
chart = easychart.new("pie", title="Distribution of Blood Types")
chart.subtitle = "Source: American Red Cross"
chart.tooltip = "{point.percentage:.0f}%"

# Apply a soft contrasting color palette
chart.colors = ["#ff9ff3", "#feca57", "#1dd1a1", "#5f27cd"]

# Add data
chart.plot(
    [{"name": label, "y": value, "sliced": True if i == 0 else False} for i, (label, value) in enumerate(zip(labels, values))]
)

# Make it a donut chart
chart.options["plotOptions"] = {
    "pie": {
        "innerSize": "60%",  # Donut effect
        "dataLabels": {
            "enabled": True,
            "style": {
                "fontFamily": "Delius, cursive",
                "fontSize": "20px",
                "color": "#ffffff",
                "textOutline": "0px contrast",  # Removes the default harsh text outline
            },
        },
    }
}

# Render the chart in Streamlit
st.components.v1.html(rendering.render(chart), height=400)

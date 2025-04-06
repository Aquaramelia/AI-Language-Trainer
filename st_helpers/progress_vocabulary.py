import pandas as pd
from database.db_helpers_dashboard import vocabulary_statistics
import easychart
import streamlit as st
from custom_easychart import rendering

def return_chart(level, levelTitle, graphTitle, colormap, caption):
    vocabulary_stats = vocabulary_statistics(level)

    explored_vocabulary = vocabulary_stats["explored_vocabulary"]
    learnt_vocabulary = vocabulary_stats["learnt_vocabulary"]
    practice_vocabulary = vocabulary_stats["practice_vocabulary"]
    total_vocabulary = vocabulary_stats["total_vocabulary"]
    unexplored_vocabulary = total_vocabulary - explored_vocabulary
    
    # Ensure the chart takes 100% of the available width
    easychart.config.rendering.responsive = True
    easychart.config.save()

    # Data for pie chart
    labels = [
        "Vocabulary - Learnt", 
        "Vocabulary - In progress", 
        "Vocabulary - Unexplored"
        ]
    values = [
        learnt_vocabulary, 
        practice_vocabulary, 
        unexplored_vocabulary
        ]

    # Create pie chart
    easychart.config.scripts.append("https://code.highcharts.com/modules/variable-pie.js")
    easychart.config.save()
    chart = easychart.new("variablepie")
    chart.title = graphTitle
    chart.subtitle = levelTitle
    chart.tooltip.headerFormat = ""
    chart.tooltip.useHTML = True
    chart.tooltip.pointFormat = """
        <div style="text-align: center;">
            <span style="color: {point.color};"><b>{point.name}</b></span><br/>
            {point.y:.0f} words - {point.percentage:.0f}%
        </div>
    """
    chart.tooltip.style = {"color": "#ffffff"}
    chart.tooltip.backgroundColor = "#222222"
    # Add data
    chart.cAxis = colormap
    chart.chart.backgroundColor = "rgba(0, 0, 0, 0)"
    chart.title.style = {"color": "#ffffff", "font-size": "1.6em"}
    chart.title.align = "center"
    chart.subtitle.style = {"color": "#ffffff", "font-size": "1em"}
    chart.subtitle.align = "center"
    chart.legend.enabled = False
    chart.exporting.enabled = False
    chart.yAxis.labels.style = {"color": "#ffffff"}
    # "sliced": True if i == 0 else False to have the first piece protrude a litle
    chart.plot(
        [{"name": label, "y": value, "sliced": True if i == 0 else False} for i, (label, value) in enumerate(zip(labels, values))],
        innerSize="60%"
    )

    # Render the chart in Streamlit
    st.components.v1.html(rendering.render(chart), height=400)
    st.caption(caption)
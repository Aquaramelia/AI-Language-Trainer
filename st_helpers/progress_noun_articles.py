import pandas as pd
from database.db_helpers_dashboard import noun_article_statistics
import easychart
import streamlit as st
from custom_easychart import rendering

def return_chart():
    noun_article_stats = noun_article_statistics()

    learnt_regular = noun_article_stats["learnt_regular"]
    learnt_irregular = noun_article_stats["learnt_irregular"]
    practice_regular = noun_article_stats["practice_regular"]
    practice_irregular = noun_article_stats["practice_irregular"]
    total_regular = noun_article_stats["total_regular"]
    total_irregular = noun_article_stats["total_irregular"]
    unexplored_regular = total_regular - noun_article_stats["explored_regular"]
    unexplored_irregular = total_irregular - noun_article_stats["explored_irregular"]
    
    # Ensure the chart takes 100% of the available width
    easychart.config.rendering.responsive = True
    easychart.config.save()

    # Data for pie chart
    labels = [
        "Regular articles - Learnt", 
        "Regular articles - In progress", 
        "Irregular articles - Learnt", 
        "Irregular articles - In progress", 
        "Regular articles - Unexplored",
        "Irregular articles - Unexplored"
        ]
    values = [
        learnt_regular, 
        practice_regular, 
        learnt_irregular, 
        practice_irregular,
        unexplored_regular,
        unexplored_irregular
        ]

    # Create pie chart
    chart = easychart.new("pie")
    chart.title = ("Noun articles learning progress").title()
    chart.subtitle = "Progress is saved after each answered question."
    chart.tooltip.headerFormat = ""
    chart.tooltip.useHTML = True
    chart.tooltip.pointFormat = """
        <div style="text-align: center;">
            <span style="color: {point.color};"><b>{point.name}</b></span><br/>
            {point.y:.0f} nouns - {point.percentage:.0f}%
        </div>
    """
    chart.tooltip.style = {"color": "#ffffff"}
    chart.tooltip.backgroundColor = "#222222"
    # Add data
    chart.cAxis = "piyg"
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

    
    df = pd.DataFrame({
        "Category": ["Regular article nouns", "Irregular article nouns"],
        "Explored": [unexplored_regular, unexplored_irregular],
        "Learnt": [learnt_regular, learnt_irregular],
        "Needs Practice": [practice_regular, practice_irregular],
        "Total Exercises": [total_regular, total_irregular]
    })
    df = df.astype({
        "Category": str,  # Ensure it's a string
        "Explored": int,
        "Learnt": int,
        "Needs Practice": int,
        "Total Exercises": int
    })
    df = df.reset_index(drop=True)  # Drop the default index
    df = df.T  # Transpose
    df.columns = df.iloc[0]  # Set first row as column names
    df = df[1:]  # Remove the first row

    st.table(df)
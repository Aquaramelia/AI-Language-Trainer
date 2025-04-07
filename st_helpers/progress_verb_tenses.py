import pandas as pd
from database.db_helpers_dashboard import verb_tense_statistics
import easychart
import streamlit as st
from custom_easychart import rendering

def return_chart():
    verb_tense_stats = verb_tense_statistics()

    explored_verbs = verb_tense_stats["explored_verbs"]
    learnt_verbs = verb_tense_stats["learnt_verbs"]
    practice_verbs = verb_tense_stats["practice_verbs"]
    total_verbs = verb_tense_stats["total_verbs"]
    unexplored_verbs = total_verbs - explored_verbs
    
    # Ensure the chart takes 100% of the available width
    easychart.config.rendering.responsive = True
    easychart.config.save()

    # Data for pie chart
    labels = [
        "Verb tense forms - Learnt", 
        "Verb tense forms - In progress", 
        "Verb tense forms - Unexplored"
        ]
    values = [
        learnt_verbs, 
        practice_verbs, 
        unexplored_verbs
        ]

    # Create pie chart
    chart = easychart.new("pie")
    chart.title = ("Verb tense forms learning progress").title()
    chart.subtitle = "Progress is saved after each answered question."
    chart.tooltip.headerFormat = ""
    chart.tooltip.useHTML = True
    chart.tooltip.pointFormat = """
        <div style="text-align: center;">
            <span style="color: {point.color}; text-shadow: 0 0 6px #e4d4ff"><b>{point.name}</b></span><br/>
            {point.y:.0f} verbs - {point.percentage:.0f}%
        </div>
    """
    chart.tooltip.style = {"color": "#ffffff"}
    chart.tooltip.backgroundColor = "#caabffaa"
    chart.cAxis = "rdpu"
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
        "Category": ["Verb tense forms"],
        "Explored": [unexplored_verbs],
        "Learnt": [learnt_verbs],
        "Needs Practice": [practice_verbs],
        "Total Exercises": [total_verbs]
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
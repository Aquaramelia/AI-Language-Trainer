import streamlit as st
import streamlit_highcharts as hct

chart_def = {
   "chart": {
      "type": "column",
      "backgroundColor": "#0000FF"  # Deep Blue Background
   },
   "title": {
      "text": "🚀 INSANELY LARGE TITLE 🚀",
      "align": "left",
      "style": {"color": "#FF0000", "fontSize": "50px", "fontWeight": "bold"}  # Bright Red, Gigantic
   },
   "xAxis": {
      "categories": ["🔥 Jet fuel", "🚗 Duty-free diesel"],
      "labels": {"style": {"color": "#00FF00", "fontSize": "30px", "fontWeight": "bold"}}  # Neon Green, Huge
   },
   "yAxis": {
      "title": {"text": "💧 MILLION LITERS 💧", 
                "style": {"color": "#FFA500", "fontSize": "40px", "fontWeight": "bold"}},  # Orange, Massive
      "labels": {"style": {"color": "#00FF00", "fontSize": "30px"}}  # Same Neon Green as X-Axis
   },
   "legend": {
      "itemStyle": {"color": "#FF69B4", "fontSize": "35px", "fontWeight": "bold"}  # Pink, Extra Large
   },
   "series": [
        {"type": "column", "name": "🟢 2020", "data": [59, 83]},
        {"type": "column", "name": "🔵 2021", "data": [24, 79]},
        {"type": "column", "name": "🟣 2022", "data": [58, 88]},
        {"type": "spline",
            "name": "⚡ AVERAGE",
            "data": [47, 83.33],
            "marker": {"lineWidth": 5, "fillColor": "yellow"}  # Thick yellow markers
        }
   ]
}

hct.streamlit_highcharts(chart_def, 640)  # 640 is the chart height

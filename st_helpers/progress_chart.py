import streamlit as st
import pandas as pd
import altair as alt

def return_chart(data, days, title):
    
    df = pd.DataFrame(data)

    # Ensure datetime consistency
    df['date'] = pd.to_datetime(df['date'])

    # Select past `n` days
    today = pd.Timestamp.today().normalize()  # Use normalized pandas Timestamp
    selected_days = pd.date_range(end=today, periods=days)

    # Create DataFrame with last 7 days
    selected_days_df = pd.DataFrame({'date': selected_days})

    # Merge and fill missing values
    df = pd.merge(selected_days_df, df, on='date', how='left').fillna({'practice_count': 0})
    df = df.rename(columns={'practice_count': 'Exercises', 'date': 'Date'})

    # Build chart using Altair
    chart = alt.Chart(df).mark_bar(
        cornerRadius=5,
        line=True,
        size=20
        ).encode(
        x=alt.X(
            'Date:T', 
            axis=alt.Axis(
                title='Date', 
                format='%b %d', 
                labelColor='white', 
                titleColor='white',
                tickCount=24,
                ),
            # scale=alt.Scale(domainMid=10, padding=10)
            ),
        y=alt.Y(
            'Exercises:Q', 
            axis=alt.Axis(
                title='Exercise Count', 
                labelColor='white', 
                titleColor='white',
                offset=20
                )
            ),
            color=alt.Color(
                'Exercises',
                scale=alt.Scale(scheme="purples"),
                legend=alt.Legend(
                    title="Exercises answered",
                    labelFontSize=14, 
                    titleFontSize=17, 
                    direction="horizontal", 
                    orient="none", 
                    gradientThickness=5,
                    legendX=-85,
                    legendY=-60,
                    labelOpacity=0.8,
                    titleAnchor="middle",
                    # titlePadding=20,
                    titleOrient="top",
                    titleBaseline="top"
                )
            )
    ).properties(
        title=alt.TitleParams(
            text=title,
            color='white',
            fontSize=25,
            anchor='end'
        ),
        width=alt.Step(40),
        background="#00000000",
        padding={"top": 30, "bottom": 5}
    ).configure_view(
        fill='transparent',  # Transparent background
        stroke="white"
    ).configure_axis(
        labelFont="Delius",
        labelFontSize=16,
        titleFont="Delius",
        titleFontSize=16,
        grid=True,
        gridColor='white',
        gridOpacity=0.2
    ).configure_title(
        font="Delius",
        color="white"
    ).resolve_scale(
        x='independent'
    )

    # Disable embed options bar    
    alt.renderers.set_embed_options(actions=False)

    # Show the chart
    st.altair_chart(chart, use_container_width=True)
        
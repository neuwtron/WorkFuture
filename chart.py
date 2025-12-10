import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("styles.css")


# ----------------------------
# CONNECT TO MYSQL DATABASE
# ----------------------------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",   # change this
        database="workfuture"
    )

# ----------------------------
# LOAD DATA FROM MYSQL
# ----------------------------
@st.cache_data
def load_data():
    db = get_db_connection()
    query = """
SELECT dates, platform, sentiment_score, topic
FROM scrape_results
WHERE sentiment_score IS NOT NULL AND topic IS NOT NULL
ORDER BY dates ASC

    """
    df = pd.read_sql(query, db)
    db.close()
    return df

# ----------------------------
# STREAMLIT APP STARTS HERE
# ----------------------------
st.title("Sentiment Analysis Dashboard")

st.write("""
This dashboard sorts and visualizes sentiment analysis results from various platforms over time. The graph below represents 
the sentiement scores from social media and news sources, showing how public opinion evolves on different topics depending on
the platform. Sentiment is described as "a view of or attitude toward a situation or event; an opinion." A score of -0.5 and below indicates
negative sentiment, while a score above 0.5 indicates positive sentiment with the midrange being classified as neutral sentiment.
""")

df = load_data()


# -----------------------------------
# 📈 SENTIMENT OVER TIME (BY PLATFORM)
# -----------------------------------

st.write("## Sentiment Score Over Time by Platform")

fig_time = px.line(
    df,
    x="dates",
    y="sentiment_score",
    color="platform",  # 👈 separates each line by platform
    color_discrete_sequence=[
        "#1f77b4",  # Twitter blue
        "#ff0e0e",  # Reddit orange
        "#0E0D0D",  # News Gray
    ],
    title="Sentiment Trend Over Time by Platform",
    markers=True

)

fig_time.update_layout(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font_color="#1b5e20",
    xaxis=dict(color="#1b5e20"),
    yaxis=dict(color="#1b5e20"),
    legend=dict(font=dict(color="#1b5e20")),
    hoverlabel=dict(
        bgcolor="#ffffff",
        bordercolor="#1b5e20",
        font=dict(color="#1b5e20")
    )
)



st.plotly_chart(fig_time, use_container_width=True)


# -----------------------------------
# 🟦 COMBINED AVERAGE SENTIMENT BY PLATFORM AND TOPIC
# -----------------------------------
st.write("## Average Sentiment by Platform and Topic (Jobs vs Living)")

st.write("""
This graph shows the average sentiment towards the topics of "Jobs" and "Living" in Chicago across different platforms. 
A score above a 0.5 is considered feeling positive sentiment, while below 0.5 indicates feeling negative sentiment.
""")

# Filter out rows where topic is NULL or not in your chosen categories
df_filtered = df[df["topic"].isin(["Jobs", "Living"])]

# Group by both platform and topic
df_combined = df_filtered.groupby(["platform", "topic"])["sentiment_score"].mean().reset_index()

fig_combined = px.bar(
    df_combined,
    x="platform",
    y="sentiment_score",
    color="topic",               # separate bars by topic
    barmode="group",             # side-by-side bars
    title="Average Sentiment Score by Platform and Topic",
    color_discrete_map={         # Set your colors
        "Jobs": "#345840",       # Grey
        "Living": "#0E0D0D"      # Red
    }
)


fig_combined.update_layout(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font_color="#1b5e20",
    xaxis=dict(color="#1b5e20"),
    yaxis=dict(color="#1b5e20"),
    legend=dict(font=dict(color="#1b5e20")),
    hoverlabel=dict(
        bgcolor="#ffffff",
        bordercolor="#1b5e20",
        font=dict(color="#1b5e20")
    )
)


st.plotly_chart(fig_combined, use_container_width=True)

st.success("Dashboard Loaded Successfully 🚀")

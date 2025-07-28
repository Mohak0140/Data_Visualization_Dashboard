import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CSV Data Visualizer", layout="wide")
st.title("📊 Interactive CSV Data Visualizer")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df, use_container_width=True)

    st.sidebar.header("Visualization Settings")
    chart_type = st.sidebar.selectbox("Select chart type", ["Scatter", "Line", "Bar", "Histogram", "Box"])
    x_axis = st.sidebar.selectbox("X-axis", df.columns)
    y_axis = st.sidebar.selectbox("Y-axis", df.columns)
    color = st.sidebar.selectbox("Color (optional)", [None] + list(df.columns))

    fig = None
    if chart_type == "Scatter":
        fig = px.scatter(df, x=x_axis, y=y_axis, color=color if color != None else None)
    elif chart_type == "Line":
        fig = px.line(df, x=x_axis, y=y_axis, color=color if color != None else None)
    elif chart_type == "Bar":
        fig = px.bar(df, x=x_axis, y=y_axis, color=color if color != None else None)
    elif chart_type == "Histogram":
        fig = px.histogram(df, x=x_axis, color=color if color != None else None)
    elif chart_type == "Box":
        fig = px.box(df, x=x_axis, y=y_axis, color=color if color != None else None)

    if fig:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Explore Data")
    st.dataframe(df.describe(include='all').T, use_container_width=True)
else:
    st.info("Please upload a CSV file to get started.")
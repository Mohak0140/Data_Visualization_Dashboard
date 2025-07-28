import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import sys
import os
from pathlib import Path

def setup_environment():
    """Setup virtual environment and install dependencies if needed"""
    venv_path = Path("venv")
    requirements_file = Path("requirements.txt")
    
    # Check if virtual environment exists
    if not venv_path.exists():
        st.error("Virtual environment not found. Please create it first with: python3 -m venv venv")
        st.stop()
    
    # Check if running in virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        st.warning("⚠️ Not running in virtual environment. Please activate venv first.")
    
    # Check if dependencies are installed
    try:
        import streamlit
        import pandas
        import plotly
    except ImportError as e:
        st.error(f"Missing dependency: {e}. Please install requirements.txt")
        st.stop()

def display_app_info():
    """Display application information and status"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔧 Application Info")
    st.sidebar.info(f"""
    **Status**: ✅ Running
    **Port**: 8501
    **Mode**: Streamlit Integrated
    **Python**: {sys.version.split()[0]}
    **Working Dir**: {os.getcwd()}
    """)

def main():
    """Main Streamlit application"""
    # Setup environment check
    setup_environment()
    
    # Configure Streamlit page
    st.set_page_config(
        page_title="CSV Data Visualizer", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Main title
    st.title("📊 Interactive CSV Data Visualizer")
    st.markdown("Upload a CSV file and create interactive visualizations")
    
    # Display app info in sidebar
    display_app_info()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload your CSV file", 
        type=["csv"],
        help="Select a CSV file to analyze and visualize"
    )

    if uploaded_file is not None:
        try:
            # Read CSV data
            df = pd.read_csv(uploaded_file)
            
            # Display success message
            st.success(f"✅ File uploaded successfully! Shape: {df.shape[0]} rows × {df.shape[1]} columns")
            
            # Data preview section
            st.subheader("📋 Data Preview")
            
            # Show basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Display dataframe
            st.dataframe(df, use_container_width=True, height=300)

            # Visualization controls in sidebar
            st.sidebar.header("📊 Visualization Settings")
            
            # Chart type selection
            chart_type = st.sidebar.selectbox(
                "Select chart type", 
                ["Scatter", "Line", "Bar", "Histogram", "Box"],
                help="Choose the type of visualization to create"
            )
            
            # Column selection
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            all_columns = df.columns.tolist()
            
            x_axis = st.sidebar.selectbox("X-axis", all_columns)
            
            if chart_type in ["Scatter", "Line", "Bar", "Box"]:
                y_axis = st.sidebar.selectbox("Y-axis", all_columns)
            else:
                y_axis = None
            
            color = st.sidebar.selectbox(
                "Color (optional)", 
                [None] + all_columns,
                help="Select a column to color-code the visualization"
            )
            
            # Chart title
            chart_title = st.sidebar.text_input(
                "Chart Title", 
                value=f"{chart_type} Chart",
                help="Enter a custom title for your chart"
            )

            # Create visualization
            fig = None
            try:
                if chart_type == "Scatter":
                    if y_axis:
                        fig = px.scatter(df, x=x_axis, y=y_axis, color=color, title=chart_title)
                elif chart_type == "Line":
                    if y_axis:
                        fig = px.line(df, x=x_axis, y=y_axis, color=color, title=chart_title)
                elif chart_type == "Bar":
                    if y_axis:
                        fig = px.bar(df, x=x_axis, y=y_axis, color=color, title=chart_title)
                elif chart_type == "Histogram":
                    fig = px.histogram(df, x=x_axis, color=color, title=chart_title)
                elif chart_type == "Box":
                    if y_axis:
                        fig = px.box(df, x=x_axis, y=y_axis, color=color, title=chart_title)
                    else:
                        fig = px.box(df, y=x_axis, color=color, title=chart_title)

                if fig:
                    st.subheader("📈 Visualization")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Please select appropriate columns for the chosen chart type.")
                    
            except Exception as e:
                st.error(f"Error creating visualization: {str(e)}")

            # Data exploration section
            st.markdown("---")
            st.subheader("🔍 Data Exploration")
            
            # Statistical summary
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Descriptive Statistics**")
                if numeric_columns:
                    st.dataframe(df[numeric_columns].describe(), use_container_width=True)
                else:
                    st.info("No numeric columns found for statistical analysis.")
            
            with col2:
                st.write("**Data Types & Missing Values**")
                info_df = pd.DataFrame({
                    'Data Type': df.dtypes.astype(str),
                    'Missing Values': df.isnull().sum(),
                    'Missing %': (df.isnull().sum() / len(df) * 100).round(2)
                })
                st.dataframe(info_df, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            st.info("Please ensure you've uploaded a valid CSV file.")
    else:
        # Welcome message when no file is uploaded
        st.info("👆 Please upload a CSV file to get started.")
        
        # Show example of what can be done
        st.subheader("✨ What you can do:")
        st.markdown("""
        - 📤 **Upload CSV files** up to 200MB
        - 📊 **Create interactive charts** (Scatter, Line, Bar, Histogram, Box plots)
        - 🎨 **Customize visualizations** with different colors and axes
        - 📈 **Explore data statistics** and missing values
        - 🔍 **Preview your data** in an interactive table
        """)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            Built with ❤️ using Streamlit • 
            <a href='https://github.com' target='_blank'>View Source</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
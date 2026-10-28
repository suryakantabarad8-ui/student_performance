
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Student Dashboard", layout="wide")

st.title("🎓 Student Performance Dashboard")
st.success("The Streamlit app is running!")

st.write("Checking dataset...")

file_path = Path(__file__).parent / "student-mat.csv"

if file_path.exists():
    try:
        df = pd.read_csv(file_path, sep=";")

        if len(df.columns) == 1:
            df = pd.read_csv(file_path, sep=None, engine="python")

        st.success("CSV file loaded successfully!")
        st.write("Dataset shape:", df.shape)
        st.dataframe(df.head(10), use_container_width=True)

        if "G3" in df.columns:
            st.metric("Average Final Grade", round(df["G3"].mean(), 2))

    except Exception as e:
        st.error(f"CSV loading error: {e}")
else:
    st.error("student-mat.csv was not found in the GitHub repository.")
    st.write("Files available in the app folder:")
    st.write([p.name for p in Path(__file__).parent.iterdir()])


import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Student Performance Dashboard",
    page_icon="🎓",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>
.stApp { background-color: #f5f7fb; }
h1, h2, h3 { color: #183153; }
div[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
</style>
""", unsafe_allow_html=True)

# ---------- LOAD CSV ----------
@st.cache_data
def load_data():
    path = Path(__file__).parent / "student-mat.csv"

    if not path.exists():
        return None

    df = pd.read_csv(path, sep=";")

    # Support comma-separated CSV files too
    if len(df.columns) == 1:
        df = pd.read_csv(path, sep=None, engine="python")

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the CSV file: {e}")
    st.stop()

if df is None:
    st.error("student-mat.csv is missing from the repository.")
    st.stop()

required = ["G1", "G2", "G3"]
if not all(c in df.columns for c in required):
    st.error("The CSV must contain G1, G2 and G3 grade columns.")
    st.stop()

# ---------- HEADER ----------
st.title("🎓 Student Performance Dashboard")
st.write(
    "Explore academic results, study habits and student attendance."
)

# ---------- SIDEBAR FILTERS ----------
st.sidebar.header("Dashboard Filters")
data = df.copy()

if "school" in data.columns:
    choices = sorted(data["school"].dropna().unique())
    selected = st.sidebar.multiselect(
        "School", choices, default=choices
    )
    data = data[data["school"].isin(selected)]

if "sex" in data.columns:
    choices = sorted(data["sex"].dropna().unique())
    selected = st.sidebar.multiselect(
        "Gender", choices, default=choices
    )
    data = data[data["sex"].isin(selected)]

if "age" in data.columns and not data.empty:
    low, high = int(data["age"].min()), int(data["age"].max())
    ages = st.sidebar.slider(
        "Age range", low, high, (low, high)
    )
    data = data[data["age"].between(*ages)]

if data.empty:
    st.warning("No students match the selected filters.")
    st.stop()

# ---------- SUMMARY CARDS ----------
total = len(data)
average = data["G3"].mean()
pass_rate = (data["G3"] >= 10).mean() * 100
absences = data["absences"].mean() if "absences" in data else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("👨‍🎓 Students", total)
c2.metric("📊 Average Final Grade", f"{average:.2f}/20")
c3.metric("✅ Pass Rate", f"{pass_rate:.1f}%")
c4.metric("📅 Average Absences", f"{absences:.1f}")

st.divider()

# ---------- GRAPH 1: GRADE DISTRIBUTION ----------
st.subheader("1. Final Grade Distribution")

fig1 = px.histogram(
    data, x="G3", nbins=21,
    color_discrete_sequence=["#6366f1"],
    title="How are final grades distributed?",
    labels={"G3": "Final Grade", "count": "Number of Students"}
)
fig1.update_layout(template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

# ---------- GRAPH 2: GRADES BY PERIOD ----------
st.subheader("2. Grade Comparison Across Periods")

grade_summary = pd.DataFrame({
    "Period": ["First Period (G1)", "Second Period (G2)", "Final (G3)"],
    "Average Grade": [
        data["G1"].mean(),
        data["G2"].mean(),
        data["G3"].mean()
    ]
})

fig2 = px.bar(
    grade_summary,
    x="Period",
    y="Average Grade",
    color="Period",
    text_auto=".2f",
    title="Average grades across three assessment periods",
    color_discrete_sequence=["#60a5fa", "#818cf8", "#34d399"]
)
fig2.update_layout(template="plotly_white", showlegend=False,
                   yaxis_range=[0, 20])
st.plotly_chart(fig2, use_container_width=True)

# ---------- GRAPH 3: STUDY TIME ----------
if "studytime" in data.columns:
    st.subheader("3. Study Time vs Academic Performance")

    study = data.groupby("studytime", as_index=False).agg(
        Average_Grade=("G3", "mean"),
        Students=("G3", "size")
    )

    fig3 = px.bar(
        study,
        x="studytime",
        y="Average_Grade",
        color="Average_Grade",
        text="Students",
        color_continuous_scale="Viridis",
        title="Study-time category vs average final grade",
        labels={
            "studytime": "Study Time Category",
            "Average_Grade": "Average Final Grade",
            "Students": "Student Count"
        }
    )
    fig3.update_layout(template="plotly_white",
                       yaxis_range=[0, 20])
    st.plotly_chart(fig3, use_container_width=True)

# ---------- GRAPH 4: ABSENCES ----------
if "absences" in data.columns:
    st.subheader("4. Absences vs Final Grade")

    fig4 = px.scatter(
        data,
        x="absences",
        y="G3",
        color="sex" if "sex" in data.columns else None,
        hover_data=["G1", "G2"],
        title="Does attendance relate to academic results?",
        labels={
            "absences": "Number of Absences",
            "G3": "Final Grade"
        },
        opacity=0.75
    )
    fig4.update_layout(template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)

# ---------- GRAPH 5: GENDER COMPARISON ----------
if "sex" in data.columns:
    st.subheader("5. Average Grade by Gender")

    gender = data.groupby("sex", as_index=False).agg(
        Average_Grade=("G3", "mean"),
        Students=("G3", "size")
    )

    fig5 = px.bar(
        gender,
        x="sex",
        y="Average_Grade",
        color="sex",
        text_auto=".2f",
        title="Average final grade by gender",
        labels={
            "sex": "Gender",
            "Average_Grade": "Average Final Grade"
        }
    )
    fig5.update_layout(template="plotly_white",
                       showlegend=False, yaxis_range=[0, 20])
    st.plotly_chart(fig5, use_container_width=True)

# ---------- GRAPH 6: PREVIOUS FAILURES ----------
if "failures" in data.columns:
    st.subheader("6. Previous Failures vs Final Grade")

    failures = data.groupby("failures", as_index=False).agg(
        Average_Grade=("G3", "mean"),
        Students=("G3", "size")
    )

    fig6 = px.bar(
        failures,
        x="failures",
        y="Average_Grade",
        color="Average_Grade",
        text="Students",
        color_continuous_scale="RdYlGn",
        title="Previous class failures vs average final grade",
        labels={
            "failures": "Number of Previous Failures",
            "Average_Grade": "Average Final Grade",
            "Students": "Student Count"
        }
    )
    fig6.update_layout(template="plotly_white",
                       yaxis_range=[0, 20])
    st.plotly_chart(fig6, use_container_width=True)

# ---------- DATA TABLE ----------
st.divider()
st.subheader("📋 Student Records")

with st.expander("View dataset"):
    st.dataframe(data, use_container_width=True)

st.download_button(
    "Download Filtered Data as CSV",
    data=data.to_csv(index=False).encode("utf-8"),
    file_name="student_data_filtered.csv",
    mime="text/csv"
)

st.caption("Student Performance Dashboard | Python • Streamlit • Plotly")

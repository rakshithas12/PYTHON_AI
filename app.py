"""Browser dashboard for the Student Performance Analytics System."""

from pathlib import Path

import pandas as pd
import streamlit as st

from student_performance.analysis import (
    SUBJECT_COLUMNS,
    analyze_students,
    load_students,
    process_students,
)

DATASET_PATH = Path(__file__).resolve().parent / "data" / "students.csv"


@st.cache_data(show_spinner="Loading and validating the sample dataset...")
def get_processed_students(dataset_path: str, modified_at: float) -> pd.DataFrame:
    """Cache the processed data and reload when the CSV file changes."""
    del modified_at  # Included in the cache key to invalidate after CSV edits.
    return process_students(load_students(dataset_path))


def main() -> None:
    st.set_page_config(
        page_title="Student Performance Analytics",
        page_icon="📊",
        layout="wide",
    )
    st.title("Student Performance Analytics")
    st.caption(
        "Explore marks, grades, attendance, pass rates, subject averages, and top performers."
    )
    st.info(
        "This public demo uses fictional sample records only. Do not enter or upload "
        "real student personal information."
    )

    try:
        modified_at = DATASET_PATH.stat().st_mtime
        students = get_processed_students(str(DATASET_PATH), modified_at)
    except (FileNotFoundError, ValueError, OSError) as error:
        st.error(f"Unable to load the dataset: {error}")
        st.stop()

    st.sidebar.header("Filters")
    department_options = ["All departments", *sorted(students["department"].unique())]
    selected_department = st.sidebar.selectbox("Department", department_options)
    selected_result = st.sidebar.selectbox("Result", ["All", "Pass", "Fail"])
    top_count = st.sidebar.slider("Number of top performers", min_value=1, max_value=10, value=5)

    filtered = students.copy()
    if selected_department != "All departments":
        filtered = filtered[filtered["department"] == selected_department]
    if selected_result != "All":
        filtered = filtered[filtered["result"] == selected_result]

    if filtered.empty:
        st.warning("No students match the selected filters. Choose different filters.")
        st.stop()

    summary = analyze_students(filtered, top_n=min(top_count, len(filtered)))

    metric_columns = st.columns(4)
    metric_columns[0].metric("Students", summary["student_count"])
    metric_columns[1].metric("Class average", f"{summary['overall_class_average']:.2f}%")
    metric_columns[2].metric(
        "Pass rate", f"{summary['pass_percentage']:.1f}%",
        help=f"{summary['passed_count']} passed · {summary['failed_count']} failed",
    )
    metric_columns[3].metric("Average attendance", f"{summary['average_attendance']:.2f}%")

    best = summary["highest_performer"]
    lowest = summary["lowest_performer"]
    st.write(
        f"**Highest average:** {best['name']} ({best['student_id']}) — "
        f"{best['average_marks']:.2f}% ({best['grade']})"
    )
    st.write(
        f"**Lowest average:** {lowest['name']} ({lowest['student_id']}) — "
        f"{lowest['average_marks']:.2f}% ({lowest['grade']})"
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Subject averages")
        subject_chart = summary["subject_averages"].set_index("subject")
        st.bar_chart(subject_chart[["average_marks"]])
    with right:
        st.subheader("Grade distribution")
        grade_order = ["A+", "A", "B", "C", "D", "F"]
        grade_counts = (
            filtered["grade"].value_counts().reindex(grade_order, fill_value=0)
        )
        st.bar_chart(grade_counts.rename("students"))

    st.subheader("Top performers")
    top_table = summary["top_performers"][
        ["student_id", "name", "department", "total_marks", "average_marks", "grade"]
    ].copy()
    st.dataframe(top_table, hide_index=True, use_container_width=True)

    st.subheader("Student results")
    visible_columns = [
        "student_id", "name", "department", *SUBJECT_COLUMNS,
        "total_marks", "average_marks", "grade", "result", "attendance_pct",
    ]
    st.dataframe(filtered[visible_columns], hide_index=True, use_container_width=True)
    st.download_button(
        "Download filtered results as CSV",
        data=filtered[visible_columns].to_csv(index=False).encode("utf-8"),
        file_name="student_performance_results.csv",
        mime="text/csv",
    )

    with st.expander("About the grading rules"):
        st.markdown(
            "Grades use the average of four subject marks: A+ (90+), A (80–89.99), "
            "B (70–79.99), C (60–69.99), D (50–59.99), and F (below 50). A student "
            "passes only if every subject mark is at least 40 and attendance is at least 75%."
        )


if __name__ == "__main__":
    main()

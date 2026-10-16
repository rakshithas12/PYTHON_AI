"""Validated data loading and student performance calculations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

SUBJECT_COLUMNS = ("python", "data_analysis", "mathematics", "ai_fundamentals")
REQUIRED_COLUMNS = (
    "student_id",
    "name",
    "department",
    *SUBJECT_COLUMNS,
    "attendance_pct",
)


def load_students(csv_path: str | Path) -> pd.DataFrame:
    """Load and validate the CSV dataset before analysis."""
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"Student dataset not found: {path}")

    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("Dataset must contain at least one student record")

    frame = frame.copy()
    for column in ("student_id", "name", "department"):
        if frame[column].isna().any():
            raise ValueError(f"Column '{column}' cannot contain empty values")
        frame[column] = frame[column].astype(str).str.strip()
        if (frame[column] == "").any():
            raise ValueError(f"Column '{column}' cannot contain blank values")

    if frame["student_id"].duplicated().any():
        duplicates = frame.loc[frame["student_id"].duplicated(), "student_id"].tolist()
        raise ValueError(f"Student IDs must be unique; duplicates: {duplicates}")

    numeric_columns = [*SUBJECT_COLUMNS, "attendance_pct"]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        if frame[column].isna().any():
            raise ValueError(f"Column '{column}' must contain valid numeric values")

    for subject in SUBJECT_COLUMNS:
        if not frame[subject].between(0, 100).all():
            raise ValueError(f"Marks in '{subject}' must be between 0 and 100")
    if not frame["attendance_pct"].between(0, 100).all():
        raise ValueError("Attendance percentages must be between 0 and 100")

    return frame


def assign_grade(average_marks: float) -> str:
    """Return a grade using the documented percentage thresholds."""
    if average_marks >= 90:
        return "A+"
    if average_marks >= 80:
        return "A"
    if average_marks >= 70:
        return "B"
    if average_marks >= 60:
        return "C"
    if average_marks >= 50:
        return "D"
    return "F"


def process_students(frame: pd.DataFrame) -> pd.DataFrame:
    """Add totals, averages, grades, and pass/fail results to student rows.

    A student passes when every subject mark is at least 40 and attendance is
    at least 75 percent. The grade itself is based on the average marks.
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {', '.join(missing)}")
    if frame.empty:
        raise ValueError("Cannot process an empty student dataset")

    result = frame.copy()
    totals: list[float] = []
    averages: list[float] = []
    grades: list[str] = []
    statuses: list[str] = []

    # A loop makes the per-student calculation and pass rule easy to follow.
    for _, student in result.iterrows():
        marks = np.asarray([student[subject] for subject in SUBJECT_COLUMNS], dtype=float)
        total = float(np.sum(marks))
        average = float(np.mean(marks))
        passed = bool(np.all(marks >= 40) and student["attendance_pct"] >= 75)

        totals.append(total)
        averages.append(average)
        grades.append(assign_grade(average))
        statuses.append("Pass" if passed else "Fail")

    result["total_marks"] = totals
    result["average_marks"] = averages
    result["grade"] = grades
    result["result"] = statuses
    return result


def analyze_students(processed: pd.DataFrame, top_n: int = 5) -> dict[str, Any]:
    """Summarize class performance, subject averages, and top performers."""
    if processed.empty:
        raise ValueError("Cannot analyze an empty student dataset")
    if top_n < 1:
        raise ValueError("top_n must be at least 1")

    averages = processed["average_marks"].to_numpy(dtype=float)
    best_index = processed["average_marks"].idxmax()
    lowest_index = processed["average_marks"].idxmin()

    # Use NumPy for subject-level means and return them in a readable table.
    subject_averages = {
        subject: float(np.mean(processed[subject].to_numpy(dtype=float)))
        for subject in SUBJECT_COLUMNS
    }
    subject_summary = (
        pd.DataFrame(
            [{"subject": subject, "average_marks": average}
             for subject, average in subject_averages.items()]
        )
        .sort_values("average_marks", ascending=False)
        .reset_index(drop=True)
    )

    ranked = processed.sort_values(
        ["average_marks", "student_id"], ascending=[False, True]
    ).head(top_n)
    passed_count = int((processed["result"] == "Pass").sum())

    return {
        "student_count": int(len(processed)),
        "overall_class_average": float(np.mean(averages)),
        "highest_performer": processed.loc[best_index],
        "lowest_performer": processed.loc[lowest_index],
        "subject_averages": subject_summary,
        "top_performers": ranked,
        "passed_count": passed_count,
        "failed_count": int(len(processed) - passed_count),
        "pass_percentage": float(passed_count / len(processed) * 100),
        "average_attendance": float(
            np.mean(processed["attendance_pct"].to_numpy(dtype=float))
        ),
    }


def format_report(processed: pd.DataFrame, summary: dict[str, Any]) -> str:
    """Format the analysis as a concise terminal report."""
    best = summary["highest_performer"]
    lowest = summary["lowest_performer"]
    visible_columns = [
        "student_id", "name", "department", "total_marks", "average_marks",
        "grade", "result", "attendance_pct",
    ]
    table = processed[visible_columns].copy()
    table["average_marks"] = table["average_marks"].map(lambda value: f"{value:.2f}")
    table["total_marks"] = table["total_marks"].map(lambda value: f"{value:.0f}")

    lines = [
        "STUDENT PERFORMANCE ANALYTICS",
        "=" * 34,
        f"Dataset records: {summary['student_count']}",
        f"Overall class average: {summary['overall_class_average']:.2f}%",
        f"Pass / fail: {summary['passed_count']} / {summary['failed_count']} "
        f"({summary['pass_percentage']:.1f}% pass)",
        f"Average attendance: {summary['average_attendance']:.2f}%",
        f"Highest performer: {best['name']} ({best['student_id']}) "
        f"- {best['average_marks']:.2f}% ({best['grade']})",
        f"Lowest performer: {lowest['name']} ({lowest['student_id']}) "
        f"- {lowest['average_marks']:.2f}% ({lowest['grade']})",
        "",
        "SUBJECT AVERAGES",
        summary["subject_averages"].to_string(index=False, formatters={
            "average_marks": lambda value: f"{value:.2f}%"
        }),
        "",
        "TOP PERFORMERS",
        summary["top_performers"][
            ["student_id", "name", "average_marks", "grade"]
        ].to_string(
            index=False,
            formatters={"average_marks": lambda value: f"{value:.2f}%"},
        ),
        "",
        "ALL STUDENTS",
        table.to_string(index=False),
    ]
    return "\n".join(lines)

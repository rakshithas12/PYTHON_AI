from pathlib import Path

import pandas as pd
import pytest

from student_performance.analysis import (
    SUBJECT_COLUMNS,
    analyze_students,
    assign_grade,
    load_students,
    process_students,
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
SAMPLE_DATA = PROJECT_DIR / "data" / "students.csv"


def test_sample_dataset_has_twenty_fictional_records():
    students = load_students(SAMPLE_DATA)
    assert len(students) == 20
    assert students["student_id"].is_unique


@pytest.mark.parametrize(
    ("average", "expected"),
    [(95, "A+"), (90, "A+"), (89.99, "A"), (80, "A"),
     (79.99, "B"), (70, "B"), (60, "C"), (50, "D"), (49.99, "F")],
)
def test_grade_thresholds(average, expected):
    assert assign_grade(average) == expected


def test_processing_calculates_totals_averages_grades_and_pass_status():
    processed = process_students(load_students(SAMPLE_DATA))
    aarav = processed.loc[processed["student_id"] == "EWB001"].iloc[0]
    assert aarav["total_marks"] == 359
    assert aarav["average_marks"] == pytest.approx(89.75)
    assert aarav["grade"] == "A"
    assert aarav["result"] == "Pass"

    # Rohan fails because one subject mark is below 40, even with attendance >= 75.
    rohan = processed.loc[processed["student_id"] == "EWB009"].iloc[0]
    assert rohan["result"] == "Fail"

    # Aditya has passing subject marks but fails the 75% attendance requirement.
    aditya = processed.loc[processed["student_id"] == "EWB015"].iloc[0]
    assert aditya["result"] == "Fail"


def test_summary_has_subject_means_pass_counts_and_top_students():
    processed = process_students(load_students(SAMPLE_DATA))
    summary = analyze_students(processed, top_n=3)
    assert summary["student_count"] == 20
    assert summary["highest_performer"]["student_id"] == "EWB014"
    assert summary["lowest_performer"]["student_id"] == "EWB019"
    assert summary["passed_count"] + summary["failed_count"] == 20
    assert len(summary["top_performers"]) == 3
    assert set(summary["subject_averages"]["subject"]) == set(SUBJECT_COLUMNS)
    assert summary["overall_class_average"] == pytest.approx(
        processed["average_marks"].mean()
    )


def test_rejects_duplicate_student_ids(tmp_path):
    students = pd.read_csv(SAMPLE_DATA)
    students.loc[1, "student_id"] = students.loc[0, "student_id"]
    path = tmp_path / "duplicates.csv"
    students.to_csv(path, index=False)
    with pytest.raises(ValueError, match="unique"):
        load_students(path)


def test_rejects_marks_outside_valid_range(tmp_path):
    students = pd.read_csv(SAMPLE_DATA)
    students.loc[0, "python"] = 101
    path = tmp_path / "invalid_marks.csv"
    students.to_csv(path, index=False)
    with pytest.raises(ValueError, match="between 0 and 100"):
        load_students(path)


def test_rejects_missing_required_column(tmp_path):
    students = pd.read_csv(SAMPLE_DATA).drop(columns=["department"])
    path = tmp_path / "missing_column.csv"
    students.to_csv(path, index=False)
    with pytest.raises(ValueError, match="department"):
        load_students(path)

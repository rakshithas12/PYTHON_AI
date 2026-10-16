"""Command-line entry point for Student Performance Analytics System."""

from __future__ import annotations

import argparse
from pathlib import Path

from student_performance.analysis import (
    analyze_students,
    format_report,
    load_students,
    process_students,
)

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = PROJECT_DIR / "data" / "students.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze student marks and attendance from a CSV file."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"CSV dataset path (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="number of top performers to display (default: 5)",
    )
    parser.add_argument(
        "--export",
        type=Path,
        help="optional path to export the processed student results as CSV",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        students = load_students(args.data)
        processed = process_students(students)
        summary = analyze_students(processed, top_n=args.top)
        print(format_report(processed, summary))
        if args.export:
            args.export.parent.mkdir(parents=True, exist_ok=True)
            processed.to_csv(args.export, index=False)
            print(f"\nProcessed results exported to: {args.export}")
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Student Performance Analytics System

A Python command-line data analysis project for the EWB Python with AI assignment. It reads a CSV dataset with Pandas, uses NumPy for numerical calculations, and reports student totals, averages, grades, pass/fail status, class statistics, subject averages, and top performers.

The included dataset contains 20 **fictional sample records**. Do not replace it with real student information in a public repository.

## Features

- Loads student records into a Pandas DataFrame and validates required columns, unique IDs, numeric values, and mark/attendance ranges.
- Calculates each student's total and average marks using NumPy.
- Assigns a grade using the thresholds below.
- Identifies pass/fail students using a stated rule.
- Reports highest and lowest performers, overall class average, pass/fail counts, average attendance, subject averages, and top performers.
- Can export processed student results to a CSV file.
- Includes a Streamlit dashboard for browser-based evaluation.
- Includes automated tests and a GitHub Actions workflow.

## Grading and pass rules

| Average marks | Grade |
|---:|:---|
| 90–100 | A+ |
| 80–89.99 | A |
| 70–79.99 | B |
| 60–69.99 | C |
| 50–59.99 | D |
| Below 50 | F |

A student **passes** when every subject mark is at least 40 **and** attendance is at least 75%. Grades are calculated from the average marks independently of pass/fail status, so a student can have a grade and still fail the attendance condition.

## Individual assignment reminder

The assignment asks for individual work and says not to submit a copied complete project as your own. Use this implementation as a working reference: understand the functions and calculations, follow your trainer's guidance on AI assistance, and personalize the documentation with your own explanation and learning before submitting.

## Prerequisites

- Python 3.10 or newer
- `pip`
- A terminal (PowerShell, Command Prompt, macOS Terminal, or Linux shell)

## Install and run

From the project folder:

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

If PowerShell blocks virtual-environment activation, run the program using `\.venv\Scripts\python.exe main.py` without activating it.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

The default dataset path is `data/students.csv`; it is resolved relative to `main.py`, so the command works from any current directory.

## Run the browser dashboard locally

The dashboard is an optional presentation layer around the same analysis functions. It does not replace the command-line project used to demonstrate Python, Pandas, NumPy, functions, and loops.

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`). The dashboard supports department and pass/fail filters, subject and grade charts, top performers, a results table, and CSV download.

## Deploy a live demo to Render

The assignment requires a GitHub repository and Google Form submission; it does not require web hosting. If your evaluator specifically wants a live URL, this project includes a Streamlit dashboard and `render.yaml` for a **Free** Render web service.

1. Push the complete project to the `PYTHON_AI` GitHub repository.
2. In Render, choose **New → Blueprint** and connect `rakshithas12/PYTHON_AI` on branch `main`.
3. Review the Blueprint and choose the **Free** plan if Render asks for a plan. Do not select a paid plan or add payment details.
4. Wait for the deployment status to show **Live**, then open the `onrender.com` URL and test the dashboard.

Render Free services sleep after 15 minutes without traffic and can take about a minute to wake. The dashboard reads the bundled fictional CSV and does not save user edits, so it does not need persistent storage. Free hosting does not guarantee always-on availability.

## Examples

Run analysis on the included sample data:

```bash
python main.py
```

Show the top 10 performers:

```bash
python main.py --top 10
```

Analyze another CSV with the same required columns:

```bash
python main.py --data path/to/students.csv
```

Export the calculated totals, averages, grades, and results:

```bash
python main.py --export output/processed_results.csv
```

The export is generated output and is excluded from Git by `.gitignore`.

## Dataset format

`data/students.csv` uses these columns:

| Column | Meaning |
|---|---|
| `student_id` | Unique student identifier |
| `name` | Student name (fictional in the supplied sample) |
| `department` | Department or program |
| `python` | Python subject mark, 0–100 |
| `data_analysis` | Data Analysis subject mark, 0–100 |
| `mathematics` | Mathematics subject mark, 0–100 |
| `ai_fundamentals` | AI Fundamentals subject mark, 0–100 |
| `attendance_pct` | Attendance percentage, 0–100 |

## Test

Install the development dependencies and run the tests:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The tests cover the sample data, grade boundaries, pass/fail logic, summary calculations, and validation errors.

## Project structure

```text
student-performance-analytics/
├── .github/workflows/tests.yml
├── .python-version
├── app.py
├── data/students.csv
├── docs/PROJECT_DOCUMENTATION.md
├── render.yaml
├── student_performance/
│   ├── __init__.py
│   └── analysis.py
├── tests/test_analysis.py
├── .gitignore
├── main.py
├── requirements.txt
└── requirements-dev.txt
```

## GitHub submission checklist

1. Create a public GitHub repository with a clear name such as `student-performance-analytics` (or follow your trainer's visibility instructions).
2. Copy the project files into the repository folder.
3. Run the application and tests locally.
4. Commit and push the project, including the dataset, README, and documentation.
5. Open the repository in a browser and confirm the files are visible.
6. Add the repository link to the EWB Google Form and complete the trainer's documentation/submission steps.

The assignment deadline shown in the supplied PDF is **15 October 2026**. Check with your trainer if you need guidance about submission after that date.

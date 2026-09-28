# CodeAssess — Coding Problem Designer & Test Case Generator

A portfolio project designed around coding-assessment content workflows.

## Features

- Dashboard with problem/test-case statistics
- Create, edit, view and delete coding problems
- Store:
  - Problem statement
  - Input/output format
  - Constraints
  - Examples
  - Explanation
  - Topic
  - Difficulty
  - Tags
  - Time and memory limits
  - C++ and Python reference solutions
  - Complexity
- Search and filter the problem bank
- Generate array-based test cases:
  - Random
  - Minimum
  - Maximum
  - Sorted
  - Reverse Sorted
  - All Same
- Automatically calculate expected output for the included maximum-array demo format
- Save generated tests in bulk
- Add custom test cases
- Export a complete problem + test cases as JSON
- SQLite database, so no separate DB installation is required

## Requirements

- Python 3.10+ recommended

## Windows setup

```powershell
cd codeassess_problem_designer

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

python app.py
```

Open:

http://127.0.0.1:5000

## macOS / Linux

```bash
cd codeassess_problem_designer

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python app.py
```

Then open http://127.0.0.1:5000

## Important note about the first version

The built-in automatic expected-output generator is intentionally implemented for the demo
"Maximum Element in an Array" input convention. The project is structured so that a future
version can plug in per-problem validators/reference executors for arbitrary problem formats.

## Suggested next upgrades

1. Add C++ reference-solution execution.
2. Add Python reference-solution execution.
3. Add randomized stress testing: brute-force vs optimized solution.
4. Add more generators for strings, matrices, graphs and trees.
5. Add user authentication and roles (Admin/Reviewer).
6. Add assessment builder.
7. Add SQL Question Bank as a second module.

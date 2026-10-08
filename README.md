# CodeSentinel

An online judge platform built with Django: solve problems in the browser, get verdicts from a sandboxed judge, and compete in contests.

## Overview

CodeSentinel lets users register, browse programming problems, write solutions in an in-browser Monaco editor, and receive automatic verdicts. Problems, test cases, and contests are managed through the Django admin.

The judge engine is modular: each supported language has its own executor, and submissions run with per-testcase time limits in temporary directories that are cleaned up afterwards. It uses `subprocess.run()` with argument lists and never `exec()`.

This is designed for a college-project or demo environment. A public judge would additionally need container-level isolation (see Future Improvements).

## Features

- User registration and login
- Problem management: statement, sample I/O, difficulty, time limit, points, and hidden or visible test cases
- Submissions in Python, C, C++, and Java
- Verdicts: Accepted, Wrong Answer, Compilation Error, Runtime Error, Time Limit Exceeded
- Timed contests with start time, duration, and registration
- Per-user submission history

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Django (5.2+) |
| Database | MySQL via PyMySQL (SQLite option for local checks) |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5, Monaco Editor |
| Judge | Python `subprocess`-based executors for Python, C, C++, Java |

## Setup

Requires Python 3, a MySQL server, and compilers/runtimes for the languages you want to judge (GCC/G++, JDK).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

Create the database:

```sql
CREATE DATABASE codesentinel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set your MySQL credentials in `.env` (set `USE_SQLITE=1` to try it without MySQL), then:

```powershell
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/.

## Usage

1. Register an account, or sign in as the superuser you created.
2. Open `/admin/` to add problems and test cases (`seed_demo_data` adds sample ones).
3. Pick a problem, write a solution in the editor, choose a language, and submit.
4. View verdicts in your submission history; join contests from the Contests page.

## Project Structure

```
accounts/      user registration, login
problems/      problems, test cases, seed command
submissions/   submission model and views
contests/      contests and registration
judge/         judge service, comparison, validation, cleanup
  executors/   python, c, cpp, java executors
templates/     Django templates
static/        CSS and JavaScript
codesentinel/  project settings and URLs
```

## Future Improvements

- Run submissions inside containers with restricted users, resource limits, and no network access
- Automated tests for the judge engine and contest flow

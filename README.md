# CodeSentinel

CodeSentinel is a full-stack Django online judge platform with a premium coding-platform UI, modular judge engine, user accounts, problem management, and submission history.

## Tech Stack

- Frontend: HTML, CSS, JavaScript, Bootstrap 5, Monaco Editor
- Backend: Django
- Database: MySQL
- Supported languages: Python, C, C++, Java

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
```

Create a MySQL database:

```sql
CREATE DATABASE codesentinel_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Update `.env` with your MySQL username and password, then run:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo_data
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Judge Notes

The judge uses `subprocess.run()` with argument lists, timeouts, temporary directories, and cleanup. It never uses Python `exec()`. This is suitable for a college project/demo environment. A production public judge should additionally isolate executions with containers, restricted users, cgroups/job objects, network blocking, and filesystem sandboxing.

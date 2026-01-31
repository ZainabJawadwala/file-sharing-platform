Project: File Sharing Platform

Quick setup (Windows):

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Ensure PostgreSQL is running and `DATABASE_URL` in `database.py` is correct.

4. Run the app:

```powershell
uvicorn main:app --reload
```

Notes:
- If you prefer SQLite for quick testing, change `DATABASE_URL` in `database.py` to `sqlite:///./files.db` and ensure `engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})` for SQLite.
- To install packages system-wide, run the same `pip install -r requirements.txt` without the venv step.

Run the quick auth test and write output to `final` file

PowerShell commands (run from the project folder):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install passlib[bcrypt] python-jose boto3
python run_test.py
```

After running, open the `final` file in your editor to view the output. If you cannot install packages, `final` will contain an error message explaining what's missing.
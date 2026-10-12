# Simple Expense Tracker

A responsive Flask web app for recording personal expenses, saving them to CSV, filtering by month, and viewing total and category-wise spending.

## Features

- Add expenses with date, category, description, and amount.
- Validates dates, categories, descriptions, and positive amounts.
- Saves records in `data/expenses.csv`.
- Shows total spending, record count, and category-wise totals/percentages.
- Filters the dashboard by month.
- Deletes individual records and exports the CSV file.
- Includes a health-check endpoint for deployment monitoring.
- Responsive layout for desktop and mobile.

## Technology stack

- Python 3
- Flask
- CSV file storage (Python `csv` module)
- HTML and CSS
- Gunicorn
- Render deployment configuration (`render.yaml`)

## Run locally on Windows PowerShell

Install Python 3.11+ and Git first. Open PowerShell in the extracted project folder.

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser. If PowerShell blocks activation, run this once in the current PowerShell window and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

To stop the server, press `Ctrl+C`. The data is stored in `data/expenses.csv`. Back up this file if you need to preserve local records.

## Deploy to Render

1. Create a public GitHub repository and push this project.
2. In Render, choose **New + → Blueprint** and connect the repository, or choose **New + → Web Service**.
3. If using a Blueprint, Render reads `render.yaml`. If creating a Web Service manually, use:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Health check path: `/health`
4. Deploy and wait for the build to finish. Open the `onrender.com` URL and test adding, deleting, filtering, and exporting records.

### Important: persistence on Render

The CSV file is persistent across app restarts only when the underlying filesystem persists. Render free web services use an ephemeral filesystem, so local CSV changes may be lost on redeploy/restart. For a durable production deployment, attach a Render persistent disk and set `DATA_DIR` to its mount path (for example `/var/data`), if your plan supports persistent disks, or migrate storage to a managed database. Do not assume a free instance permanently stores expense data.

## Push to GitHub from PowerShell

Create an empty repository on GitHub first (do not initialize it with a README, licence, or `.gitignore`, because these files already exist locally). Then run from the project folder:

```powershell
git init
git add .
git commit -m "Build simple expense tracker"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/simple-expense-tracker.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. If Git says the remote already exists, use `git remote set-url origin https://github.com/YOUR-USERNAME/simple-expense-tracker.git`.

## Suggested GitHub repository details

**Repository name:** `simple-expense-tracker`

**Description:** `A responsive Python Flask expense tracker with CSV persistence, monthly filtering, category-wise spending summaries, validation, and CSV export. Deployable on Render.`

**Topics:** `python`, `flask`, `expense-tracker`, `csv`, `web-app`, `render`

## Suggested submission checklist

- [ ] Test adding a valid expense and confirm it appears.
- [ ] Try an invalid/zero/negative amount and confirm validation.
- [ ] Filter by month and clear the filter.
- [ ] Delete an expense and export CSV.
- [ ] Confirm `/health` returns `{"status":"ok"}`.
- [ ] Add deployment URL and GitHub repository URL to the internship portal.
- [ ] Ensure `README.md` describes setup, deployment, and storage limitations.
- [ ] Include the PDF report in the repository or submission package if required.
- [ ] Share a LinkedIn post about the completed project if required.

## Project structure

```text
simple-expense-tracker/
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
├── data/
│   └── .gitkeep
├── static/
│   └── style.css
├── templates/
│   └── index.html
└── report/
    └── Simple_Expense_Tracker_Report.pdf
```

## Interview questions

**How are expense records stored?**  
Each record is stored as a row in a CSV file with an ID, date, category, description, and amount. The CSV format is easy to inspect and export.

**Why persist application data?**  
Persistence keeps records available between requests and normal process restarts. In cloud deployments, the storage medium must also survive redeploys; an ephemeral filesystem is not sufficient for durable records.

**How would monthly filtering work?**  
The selected `YYYY-MM` value is validated and compared with the beginning of each ISO-formatted expense date. Only matching rows are included in the dashboard summary.

## Limitations and future improvements

- CSV storage is suitable for a small learning project, but concurrent writes and large datasets are better handled by a database.
- Add a persistent disk or a managed database for durable cloud storage.
- Future improvements could include authentication, budgets, charts, recurring expenses, and SQLite/PostgreSQL support.

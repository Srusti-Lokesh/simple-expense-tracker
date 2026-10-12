import csv
import io
import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_file, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-production")

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
DATA_FILE = DATA_DIR / "expenses.csv"
FIELDS = ["id", "date", "category", "description", "amount"]


def ensure_storage():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()


def read_expenses():
    ensure_storage()
    with DATA_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    expenses = []
    for row in rows:
        try:
            amount = float(row.get("amount", 0))
            datetime.strptime(row.get("date", ""), "%Y-%m-%d")
            if amount <= 0:
                continue
            expenses.append({
                "id": row.get("id", ""),
                "date": row.get("date", ""),
                "category": row.get("category", "Other"),
                "description": row.get("description", ""),
                "amount": amount,
            })
        except (ValueError, TypeError):
            continue
    return sorted(expenses, key=lambda item: (item["date"], item["id"]), reverse=True)


def write_expenses(expenses):
    ensure_storage()
    temp_file = DATA_FILE.with_suffix(".tmp")
    with temp_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        for expense in expenses:
            writer.writerow({key: expense[key] for key in FIELDS})
    temp_file.replace(DATA_FILE)


def get_filtered_expenses(month=""):
    expenses = read_expenses()
    if month:
        try:
            datetime.strptime(month, "%Y-%m")
            expenses = [item for item in expenses if item["date"].startswith(month)]
        except ValueError:
            month = ""
    return expenses, month


def make_summary(expenses):
    total = round(sum(item["amount"] for item in expenses), 2)
    categories = {}
    for item in expenses:
        categories[item["category"]] = categories.get(item["category"], 0) + item["amount"]
    category_summary = sorted(
        [{"name": name, "total": round(amount, 2)} for name, amount in categories.items()],
        key=lambda item: item["total"],
        reverse=True,
    )
    return total, category_summary


@app.get("/")
def index():
    month = request.args.get("month", "").strip()
    expenses, month = get_filtered_expenses(month)
    total, category_summary = make_summary(expenses)
    all_expenses = read_expenses()
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        category_summary=category_summary,
        count=len(expenses),
        month=month,
        today=date.today().isoformat(),
        all_count=len(all_expenses),
    )


@app.post("/add")
def add_expense():
    expense_date = request.form.get("date", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    amount_text = request.form.get("amount", "").strip()

    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        flash("Please enter a valid expense date.", "error")
        return redirect(url_for("index"))

    allowed_categories = {"Food", "Transport", "Housing", "Utilities", "Shopping", "Health", "Entertainment", "Education", "Travel", "Other"}
    if category not in allowed_categories:
        flash("Please select a valid category.", "error")
        return redirect(url_for("index"))
    if not description or len(description) > 120:
        flash("Description is required and must be 120 characters or fewer.", "error")
        return redirect(url_for("index"))

    try:
        amount_decimal = Decimal(amount_text)
        if not amount_decimal.is_finite() or amount_decimal <= 0 or amount_decimal > Decimal("999999999"):
            raise InvalidOperation
        amount = str(amount_decimal.quantize(Decimal("0.01")))
    except (InvalidOperation, ValueError):
        flash("Amount must be a positive number with at most two decimal places.", "error")
        return redirect(url_for("index"))

    expenses = read_expenses()
    new_id = str(max([int(item["id"]) for item in expenses if str(item["id"]).isdigit()] + [0]) + 1)
    expenses.append({
        "id": new_id,
        "date": expense_date,
        "category": category,
        "description": description,
        "amount": amount,
    })
    write_expenses(expenses)
    flash("Expense added successfully.", "success")
    return redirect(url_for("index"))


@app.post("/delete/<expense_id>")
def delete_expense(expense_id):
    expenses = read_expenses()
    updated = [item for item in expenses if str(item["id"]) != str(expense_id)]
    if len(updated) == len(expenses):
        flash("Expense was not found.", "error")
    else:
        write_expenses(updated)
        flash("Expense deleted.", "success")
    return redirect(url_for("index"))


@app.get("/export")
def export_csv():
    ensure_storage()
    return send_file(DATA_FILE, as_attachment=True, download_name="expenses.csv", mimetype="text/csv")


@app.get("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    ensure_storage()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)

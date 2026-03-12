# BudgetApp

BudgetApp is a Django 5 project that lets each user record their salary and expenses, then instantly see 50/30/20 allocations with detailed needs/wants breakdowns. Authentication is built in, budgets are private per user, and the UI is Bootstrap-based with a sidebar layout and Chart.js visual.

## Features
- User registration, login, and logout (Django auth)
- Private budgets per user
- Budget model with salary, housing, food, transport, other expenses
- Automatic calculations:
  - Total expenses, remaining balance
  - 50/30/20 buckets (Savings/Needs/Wants)
  - Needs breakdown (Rent, Fare, Utilities, Debt, Groceries, Personal care, Gas)
  - Wants breakdown (Eating Out, Entertainment, New Clothing)
- Dashboard with:
  - Input form + savings goal
  - Summary tiles and stacked 50/30/20 bar
  - Doughnut chart (Chart.js) for allocations
  - Needs/Wants breakdown lists and stacked bar chart for custom categories
  - Savings goal progress, recent history, monthly trends line chart
- Historical budgets (each save is a record) + history page
- Custom needs/wants categories per budget
- Exports: CSV and PDF (PDF via reportlab)
- Profile page (email, currency, default savings goal)
- Alerts when expenses exceed salary or category totals exceed 100%
- Responsive Bootstrap UI, sidebar navigation, custom CSS/JS

## Stack
- Python 3.11+ (tested with 3.11/3.12/3.14)
- Django 5.2.x
- SQLite (default; swapable)
- Bootstrap 5.3, Chart.js

## Setup
From the project root (`C:\Users\User\Desktop\BudgetApp`):
```bash
python -m venv .venv
.\\.venv\\Scripts\\activate   # Windows
pip install django
python manage.py migrate
python manage.py runserver
```

## Usage
1) Register a user (`/budgets/register/`) or via top-right links.
2) Log in (`/budgets/login/`).
3) Go to Dashboard (`/budgets/`) to enter salary and expenses, save, and view allocations.

## Project Structure
- `manage.py` — Django entrypoint
- `BudgetApp/` — project settings and URLs
- `budgets/` — app with models, forms, views, URLs, migrations
- `templates/` — base layout, dashboard, auth pages
- `static/` — CSS and JS (Chart.js integration)

## Notes
- Sidebar navigation highlights current page.
- Chart data is passed as JSON to avoid template JS injection issues.
- Default secret key is for development; change `SECRET_KEY` and set `DEBUG = False` for production.
- For production: configure allowed hosts, static files (`collectstatic`), and a real database.

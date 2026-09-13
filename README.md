# SplitCyber - Group Expense Splitter

A full-featured group expense-splitting backend and dashboard application built using **FastAPI** and **SQLAlchemy** with **MySQL** support (and seamless SQLite fallback).

## Features

- **User Management**: Create and track users with avatars and unique email verification.
- **Group Management**: Organize users into groups (e.g. Trips, Roommates, Projects) with dedicated member tracking.
- **Flexible Expense Splitting**:
  - `EQUAL`: Split evenly among all or selected members with penny rounding adjustment.
  - `EXACT`: Specify exact amounts for each member.
  - `PERCENTAGE`: Specify percentage share per member with 100% total validation.
- **Balance Calculation & Debt Simplification**:
  - Computes net balance for every group member (`paid - share + settlements`).
  - Implements the **Greedy Min-Cash-Flow Algorithm** to calculate the minimal set of transactions needed to settle all debts.
- **Settlement Tracking**: Record direct repayments between members to reduce outstanding balances.
- **Interactive Web Dashboard**: Built-in modern glassmorphism frontend dashboard to manage groups, add expenses, and view debts in real time.
- **Interactive API Documentation**: Swagger UI at `/api/docs` and ReDoc at `/api/redoc`.

---

## Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **ORM & DB**: SQLAlchemy with MySQL (`pymysql`) + SQLite auto-fallback
- **Validation**: Pydantic v2
- **Testing**: Python `unittest` + `TestClient` (HTTPX)
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (no external build step required)

---

## Project Structure

```
trial/
├── backend/
│   └── app/
│       ├── config.py             # App and DB settings
│       ├── database.py           # SQLAlchemy engine & session maker
│       ├── models.py             # SQLAlchemy ORM models
│       ├── schemas.py            # Pydantic request & response schemas
│       ├── main.py               # FastAPI app entry point & route mounting
│       ├── routers/
│       │   ├── users.py          # User management endpoints
│       │   ├── groups.py         # Group and membership endpoints
│       │   ├── expenses.py       # Expense creation and split calculations
│       │   ├── balances.py       # Balance summary and debt calculation
│       │   └── settlements.py    # Direct debt settlement endpoints
│       └── services/
│           └── balance.py        # Min-Cash-Flow debt simplification logic
├── frontend/
│   ├── index.html                # Modern single-page dashboard UI
│   ├── css/                      # Custom styling & glassmorphism design
│   └── js/                       # Client-side API integration & DOM logic
├── tests/
│   └── test_api.py               # Integration test suite
├── run.py                        # Single-command server starter
├── seed.py                       # Demo data population script
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Database (Optional)
By default, the app will try connecting to MySQL at `localhost:3306` with user `root` and database `expense_db`. If MySQL is not running or credentials differ, it **automatically falls back to local SQLite** (`expense_db.db`) without any manual intervention.

To configure MySQL credentials, set environment variables:
```bash
export MYSQL_USER="your_user"
export MYSQL_PASSWORD="your_password"
export MYSQL_HOST="localhost"
export MYSQL_PORT="3306"
export MYSQL_DB="expense_db"
```

### 3. Run the Server
```bash
python run.py
```
- **Web Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Interactive API Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

### 4. Seed Demo Data (Optional)
In a separate terminal while the server is running:
```bash
python seed.py
```

### 5. Run Tests
```bash
python -m unittest tests/test_api.py
```

---

## API Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check endpoint |
| `POST` | `/api/users` | Create user |
| `GET` | `/api/users` | List all users |
| `POST` | `/api/groups` | Create new group |
| `GET` | `/api/groups` | List all groups |
| `POST` | `/api/groups/{id}/members` | Add member to group |
| `POST` | `/api/groups/{id}/expenses` | Create expense (`EQUAL`, `EXACT`, `PERCENTAGE`) |
| `GET` | `/api/groups/{id}/expenses` | List all group expenses |
| `GET` | `/api/groups/{id}/balances` | Get member balances & simplified debt transactions |
| `POST` | `/api/groups/{id}/settlements` | Record debt settlement between 2 members |
| `GET` | `/api/groups/{id}/settlements` | List all settlements in group |

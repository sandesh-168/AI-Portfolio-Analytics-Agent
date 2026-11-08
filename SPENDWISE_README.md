# SpendWise — Full-Stack Personal Expense Tracker

SpendWise is a production-style, responsive personal finance and expense management web application designed for portfolio demonstration and university full-stack engineering requirements.

It features a modern **React (Vite) + Tailwind CSS** frontend communicating through REST APIs with an **Express.js (Node.js)** backend and a persistent **MySQL 8** database with connection pooling.

---

## 🌟 Key Features

* **Authentication & Session Management**
  * Registration with client and server input validation (Zod + React Hook Form).
  * Secure bcrypt password hashing.
  * JWT authentication delivered through secure, HTTP-only cookies.
  * Rate limiting on authentication endpoints to defend against brute force.
  * 1-Click Demo Login button for rapid testing and evaluation.

* **Personalized Dashboard**
  * Dynamic user greeting and date display.
  * Real-time financial calculations (Overall Lifetime Balance, Period Income, Period Expenses, and Savings Rate percentage).
  * Interactive **Income vs Expenses** Bar Chart (Recharts) with monthly historical breakdown.
  * **Expense Breakdown** Doughnut/Pie Chart showing category share.
  * Recent transactions table with quick edit modal access.
  * Active monthly budgets overview with color-coded utilization progress bars (Normal, Warning, Exceeded).
  * Real financial insights calculated from actual spending habits.

* **Transaction Management**
  * Full CRUD operations (Add, Edit, Delete with modal confirmations).
  * Scoped to authenticated user ID with complete data isolation.
  * Exact `DECIMAL(12,2)` precision math.
  * Real-time search by title and notes.
  * Filter by transaction type (Income / Expense).
  * Filter by category and date range.
  * Multi-column sorting (Date, Amount, Title; Ascending / Descending).
  * Pagination with custom page navigation.
  * Instant CSV export with server-side generation.

* **Monthly Budget Tracking**
  * Category-based monthly spending limits.
  * Real-time calculation of spent amount, remaining budget, and percentage utilization.
  * Exceeded status highlight with negative remaining balance.
  * Unique constraint enforcement (`user_id`, `category`, `budget_month`) to prevent duplicates.

* **Financial Reports & Analytics**
  * Filter presets: *This Month, Last Month, Last 3 Months, Last 6 Months, This Year, Custom Date Range*.
  * KPI summary cards: Total Inflow, Total Outflow, Net Savings, Lifetime Balance.
  * Inflow vs Outflow monthly trends chart.
  * Category breakdown proportional pie chart.
  * Identification of highest-spending category and largest single purchase.
  * Export filtered report data to CSV.

* **Savings Goals**
  * Create goals with target amount and target date (e.g. *Emergency Fund, Apple MacBook Pro, Vacation*).
  * Track completion percentage and remaining amount to target.
  * Deposit or withdraw funds with honest manual record tracking.

* **Recurring Transactions Engine**
  * Schedule recurring incomes (salary, retainers) and expenses (rent, subscriptions, utilities).
  * Frequencies: Weekly, Monthly, Yearly.
  * Pause and resume rules.
  * Idempotency guarantee via `recurring_occurrences` table and MySQL transactions so duplicate transactions are never inserted.
  * Manual **"Generate Due"** action button for seamless local development and testing.

* **Settings & Preferences**
  * Profile management: edit name and view email.
  * Display currency selector: **INR (₹ - Default), USD ($), EUR (€), GBP (£)** using locale formatting (`en-IN`, `en-US`, `de-DE`, `en-GB`).
  * Theme toggle: Light Mode and Dark Mode.
  * Security: change password with current password verification.
  * Account Deletion: cascade deletion of all user records from MySQL with confirmation modal.

---

## 🏗️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, Vite 6, Tailwind CSS 3, React Router DOM 6, Recharts 2, Lucide React, React Hook Form, Zod |
| **Backend** | Node.js, Express.js 4, mysql2 (Connection Pooling), JSON Web Tokens (JWT), bcryptjs, Helmet, CORS, Cookie-Parser, Express-Rate-Limit, Zod |
| **Database** | MySQL 8.0+ (`spendwise_db`) with Foreign Keys, Unique Constraints, and Indexes |
| **Testing** | Jest, Supertest (22 integration tests passing) |

---

## 📁 Project Folder Structure

```
spendwise/
├── backend/
│   ├── database/
│   │   ├── schema.sql           # MySQL database schema (tables, keys, indexes)
│   │   └── seed.sql             # Realistic sample financial seed data
│   ├── src/
│   │   ├── config/
│   │   │   ├── database.js      # mysql2 connection pool and query helpers
│   │   │   ├── initDb.js        # Schema initialization script
│   │   │   └── seedDb.js        # Seed execution runner
│   │   ├── controllers/
│   │   │   ├── authController.js
│   │   │   ├── userController.js
│   │   │   ├── transactionController.js
│   │   │   ├── budgetController.js
│   │   │   ├── dashboardController.js
│   │   │   ├── reportController.js
│   │   │   ├── goalController.js
│   │   │   └── recurringController.js
│   │   ├── middleware/
│   │   │   ├── authMiddleware.js # Cookie and Bearer token JWT verification
│   │   │   ├── errorHandler.js   # Centralized error and validation handler
│   │   │   └── rateLimiter.js    # Express rate limiters
│   │   ├── routes/
│   │   │   ├── authRoutes.js
│   │   │   ├── userRoutes.js
│   │   │   ├── transactionRoutes.js
│   │   │   ├── budgetRoutes.js
│   │   │   ├── dashboardRoutes.js
│   │   │   ├── reportRoutes.js
│   │   │   ├── goalRoutes.js
│   │   │   ├── recurringRoutes.js
│   │   │   └── index.js
│   │   ├── validators/          # Zod schema validators
│   │   ├── utils/               # Response formatting helpers
│   │   ├── app.js               # Express application configuration
│   │   └── server.js            # Server entry point
│   ├── tests/
│   │   └── api.test.js          # Full Jest + Supertest integration suite
│   ├── .env.example
│   └── package.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/          # Button, Input, Select, Card, Modal, Badge, etc.
│   │   │   ├── layout/          # Navbar, Sidebar, DashboardLayout
│   │   │   ├── dashboard/       # SummaryCard, BarChart, PieChart, Insights
│   │   │   ├── transactions/    # TransactionModal, filters
│   │   │   ├── budgets/         # BudgetCard, BudgetModal
│   │   │   ├── goals/           # GoalCard, GoalModal, ContributeModal
│   │   │   └── recurring/       # RecurringModal
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   ├── CurrencyContext.jsx
│   │   │   ├── ToastContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   ├── pages/               # All 12 application pages
│   │   ├── services/            # api.js reusable HTTP client
│   │   ├── utils/               # Formatters and category constants
│   │   ├── App.jsx              # Router and Protected Route guards
│   │   ├── main.jsx
│   │   └── index.css
│   ├── .env.example
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
├── package.json                 # Root script runner
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Configuration

### Backend Configuration (`backend/.env`)

```ini
PORT=5000
NODE_ENV=development
FRONTEND_URL=http://localhost:5173

# MySQL Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=spendwise_db

# JWT Secret
JWT_SECRET=spendwise_super_secure_jwt_secret_key_college_project_2026_x8934
JWT_EXPIRES_IN=1d
```

### Frontend Configuration (`frontend/.env`)

```ini
VITE_API_URL=http://localhost:5000/api
```

---

## 🚀 Step-by-Step Local Setup

### Prerequisites

1. **Node.js** (v18 or higher recommended; verified on Node.js v26)
2. **MySQL Server 8.0+** running locally on port 3306.

---

### Step 1: Install Dependencies

From the root project directory:

```bash
# Install backend and frontend dependencies
npm run setup
```

Or install separately:

```bash
cd backend && npm install
cd ../frontend && npm install
```

---

### Step 2: Initialize Database and Seed Sample Data

1. Initialize the schema and tables in MySQL:
   ```bash
   npm run db:init
   ```
2. (Optional but recommended) Seed realistic transactions, budgets, goals, and demo user:
   ```bash
   npm run db:seed
   ```

> **Demo User Account Credentials:**
> * **Email:** `demo@spendwise.com`
> * **Password:** `Password123!`

---

### Step 3: Run the Application (Two Terminals)

#### Terminal 1 — Start the Backend Server:

```bash
cd backend
npm run dev
```
* The API will start on: `http://localhost:5000/api`
* Health check: `http://localhost:5000/api/health`

#### Terminal 2 — Start the Frontend Application:

```bash
cd frontend
npm run dev
```
* Open your browser at: `http://localhost:5173`

---

## 🧪 Running Automated Tests

SpendWise includes an automated Jest integration test suite in `backend/tests/api.test.js` validating:
* User registration and duplicate email rejection (409).
* Password verification and bad password rejection (401).
* Unauthorized access prevention (401).
* Transaction CRUD, negative amount validation, and query filters.
* User data isolation (User B cannot access, modify, or delete User A records).
* Monthly budgets and duplicate month-category prevention.
* Real-time dashboard calculation accuracy.
* Savings goals contributions and withdrawals.

Run the tests with:

```bash
npm run test:backend
```

Result:
```
PASS tests/api.test.js
  SpendWise API Integration Test Suite
    ✓ GET /api/health should return 200 OK
    ✓ 1. User registration with valid data
    ✓ 2. Duplicate email registration should fail with 409 Conflict
    ✓ 3. Register User B for isolation testing
    ✓ 4. Login with valid credentials
    ✓ 5. Login with invalid credentials should return 401
    ✓ 6. Unauthorized access without token should return 401
    ✓ 7. Access profile with valid token
    ✓ 8. Reject invalid transaction amounts (zero or negative)
    ✓ 9. Create a valid transaction for User A
    ✓ 10. Create an income transaction for User A
    ✓ 11. List transactions for User A
    ✓ 12. Update a transaction
    ✓ 13. Preventing User B from accessing or editing User A transaction (Data Isolation)
    ✓ 14. Create a budget for User A
    ✓ 15. Reject duplicate budgets for same user, category, and month
    ✓ 16. List budgets and calculate spending utilization from real transactions
    ✓ 17. Dashboard summary returns correct overall balance and period metrics
    ✓ 18. Create savings goal with target and initial saved amount
    ✓ 19. Deposit money toward savings goal and verify percentage
    ✓ 20. Withdraw money from savings goal
    ✓ 21. Delete transaction for User A

Test Suites: 1 passed, 1 total
Tests:       22 passed, 22 total
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check endpoint |
| `POST` | `/api/auth/register` | Register new user account |
| `POST` | `/api/auth/login` | Log in and receive HTTP-only auth cookie |
| `POST` | `/api/auth/logout` | Clear auth cookie |
| `GET` | `/api/auth/me` | Retrieve current authenticated user profile |
| `POST` | `/api/auth/change-password` | Update password with current password verification |
| `GET` | `/api/users/me` | Fetch user settings |
| `PATCH` | `/api/users/me` | Update name and preferred currency |
| `DELETE` | `/api/users/me` | Delete account and cascade delete all user records |
| `GET` | `/api/transactions` | List transactions with filters, search, sort, pagination |
| `GET` | `/api/transactions/:id` | Get single transaction |
| `POST` | `/api/transactions` | Create new transaction |
| `PATCH` | `/api/transactions/:id` | Update transaction |
| `DELETE` | `/api/transactions/:id` | Delete transaction |
| `GET` | `/api/transactions/export` | Download filtered transactions as CSV |
| `GET` | `/api/budgets` | List budgets with real spending utilization |
| `POST` | `/api/budgets` | Set category monthly budget |
| `PATCH` | `/api/budgets/:id` | Update budget limit |
| `DELETE` | `/api/budgets/:id` | Delete budget |
| `GET` | `/api/dashboard/summary` | Overall balance, period income, expenses, savings rate |
| `GET` | `/api/dashboard/income-expenses` | Monthly historical income vs expense comparison |
| `GET` | `/api/dashboard/expense-breakdown` | Category distribution for doughnut chart |
| `GET` | `/api/dashboard/recent-transactions` | Latest 7 transactions |
| `GET` | `/api/dashboard/budget-overview` | Current month budget progress bars |
| `GET` | `/api/dashboard/insights` | Real insights derived from transaction records |
| `GET` | `/api/reports/summary` | Period report summary metrics |
| `GET` | `/api/reports/monthly-trends` | Inflow/outflow monthly trend series |
| `GET` | `/api/reports/category-breakdown` | Category breakdown for report range |
| `GET` | `/api/goals` | List all savings goals |
| `POST` | `/api/goals` | Create new savings goal |
| `PATCH` | `/api/goals/:id` | Update savings goal |
| `POST` | `/api/goals/:id/contribute` | Deposit or withdraw savings contribution |
| `DELETE` | `/api/goals/:id` | Delete savings goal |
| `GET` | `/api/recurring` | List all recurring transaction rules |
| `POST` | `/api/recurring` | Create recurring rule (weekly/monthly/yearly) |
| `PATCH` | `/api/recurring/:id` | Update recurring rule |
| `POST` | `/api/recurring/:id/pause` | Pause rule |
| `POST` | `/api/recurring/:id/resume` | Resume rule |
| `DELETE` | `/api/recurring/:id` | Delete rule |
| `POST` | `/api/recurring/generate-due` | Idempotently generate pending recurring transactions |

---

## 🔒 Security Practices

* **Passwords:** Hashed with `bcryptjs` using a cost factor of 10. Passwords are never logged or returned in API responses.
* **Tokens:** Signed JWTs stored in `HTTP-only`, `SameSite=Lax` cookies, shielding against XSS token harvesting.
* **Data Isolation:** All database queries require authentication and are scoped by `user_id = ?`. Users cannot read or manipulate another user's financial records.
* **SQL Injection Prevention:** All SQL queries strictly use parameterized queries (`mysql2/promise`). User inputs are never concatenated directly into queries.
* **Rate Limiting:** Protects `/api/auth/register` and `/api/auth/login` from brute force credential attacks.
* **Security Headers:** HTTP headers configured using `helmet`.
* **CORS:** Controlled origin policy configured for frontend domains.

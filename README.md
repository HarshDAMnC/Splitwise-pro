# Splitwise Optimization Engine

A professional, full-stack expense sharing application engineered specifically to minimize cash flow transactions using advanced graph algorithms. Features a highly normalized database schema, a decoupled Python REST API backend, and a dynamic frontend UI that perfectly matches modern minimalist aesthetics.

## 🚀 Core Features

- **Greedy Graph Simplification**: Employs an $O(V \log V)$ Max-Heap algorithm to instantly calculate the absolute minimum number of cash transactions needed to settle all cyclical debts within a group.
- **Strictly Normalized Database**: Integrates directly with **Supabase (PostgreSQL)** across 10 meticulously isolated schemas separating `expenses`, `payers`, `splits`, and cached global `balances`. 
- **Omni-platform Accessibility**: Seamlessly alter and mutate database states dynamically via Python interactive terminal CLIs, raw standalone scripts, or visually via the native web application.

---

## 🛠️ Tech Stack

- **Backend Architecture:** Python, Flask REST API
- **Data Layer:** Supabase (PostgreSQL), `supabase-py` SDK
- **Algorithm Foundation:** Python `heapq` module
- **Frontend Layer:** Vanilla JavaScript (ES6+), Vanilla CSS3, HTML5

---

## 📐 The 10-Table Architecture

To achieve absolute mathematical precision without relying on NoSQL document nesting arrays, the core relies on strict Relational Logic:
1. `users`: Global platform identifiers
2. `groups`: Organizational scopes
3. `group_members`: Join table mapping
4. `expenses`: Mathematical cost definitions
5. `expense_payers`: Tracking exact physical capital handed to merchants
6. `expense_splits`: Tracking theoretical debt allocation
7. `categories`: Enum tagging
8. `user_balances_cache`: High-speed integer tracking for $O(1)$ algorithmic lookups
9. `transactions`: Permanent cached output of the minimized graph
10. `settlements`: Ledger tracking actual physical cash payoffs

---

## 💻 Installation & Setup

### 1. Configure the Environment
Clone the repository and ensure you are using Python 3.10+.
```bash
pip install -r backend/requirements.txt
```

### 2. Initialize the Database
1. Launch a new [Supabase](https://supabase.com/) project.
2. Navigate to the internal **SQL Editor** tab.
3. Copy the entire contents of `backend/schema.sql` and run it to instantly deploy all 10 tables and Foreign Key limits.
4. Rename `backend/.env.example` to `backend/.env` and inject your unique Project URL and Anon API key.

### 3. Launch the Stack
Start the Python Flask Core matching `app.py`:
```bash
python backend/app.py
```
*(The server will securely boot on `http://localhost:5000`)*

Next, simply open `frontend/index.html` seamlessly inside any modern browser to immediately interact with the stack.

---

## 🧪 Developer CLI Tools

You are not restricted to the interactive website interface. The system accommodates developers via built-in terminal pipelines:

- **Interactive Manual Logging**: `python backend/cli/add_data.py` (Execute a wizard that guides you iteratively through logging entities)
- **Hardcoded Automation**: `python backend/cli/custom_script.py` (Edit Python directly to inject massive expenses via arrays and loops)
- **System Stress Test**: `python backend/cli/seed_db.py` (A one-click execution that spawns highly complex web structures of debt automatically to test the algorithmic load)

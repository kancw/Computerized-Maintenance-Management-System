# Computerized Maintenance Management System (CMMS)

A command-line SQLite application for managing campus maintenance operations.

## What It Does

**Data Management (Add / Delete / Update / View)**
- **Employees** — store executives, managers, and workers with contact info; enforce a supervision hierarchy (executives → managers → workers); cap at 1,000 employees
- **Activities** — track maintenance jobs (cleaning, repair, renovation, weather-related, maintenance) with location, dates, status (scheduled / in-progress / completed), and an assigned manager
- **Assignments** — link employees to activities with start/due dates
- **Buildings & Rooms** — manage up to 99 buildings; rooms are typed (classroom, office, laboratory, conference, storage, restroom) with encoded floor/room IDs
- **Outdoor Areas** — track named areas by type (square, gate, path, parking lot, garden, sports field)
- **External Companies & Contracts** — record contracted companies, their specialization, and which activity each contract covers
- **Chemicals & Usage** — catalogue chemicals by hazard level (0–4) and log quantities used per activity

**Other Features**
- **Run SQL** — execute arbitrary SQL queries directly against the database
- **Generate Reports** — produce summaries of maintenance activity data
- **Restart Database** — triple-authentication (passphrase → DBA password → confirmation) wipes and recreates the database, then reloads sample data

## Structure

```
src/
  app.py          # Interactive CLI (main entry point)
  database.py     # Schema creation and DB connection
  insert_data.py  # Sample/seed data
  cmms.db         # SQLite database file (auto-generated)
tests/
  test_app.py     # 32 unit tests covering all CRUD operations
  conftest.py     # Pytest path configuration
```

## Running

```powershell
# Activate the virtual environment first
.venv\Scripts\Activate.ps1
python src/app.py
```

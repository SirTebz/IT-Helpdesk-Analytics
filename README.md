# IT Helpdesk Analytics Dashboard

Turn helpdesk ticket data into actionable operational insights. This is a complete, reproducible Junior Data Analyst portfolio project built around a realistic synthetic service-desk dataset (10,000 tickets across 25 months).

## Features

- Streamlit multi-page dashboard: overview, tickets, trends, SLA, technician, department, category, customer satisfaction, data quality, explorer, and reporting.
- Global date, department, category, priority, status, and technician filters.
- Validated synthetic data pipeline, with duplicate, required-field, categorical, and date-sequence checks.
- Reusable KPI calculations, evidence-led insights, CSV exports, Power BI-ready extract, Excel workbook, SQL Server schema and analytical SQL.
- SQLite development database created automatically; SQL Server connection is configurable using environment variables.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app/main.py
```

The first run generates `data/raw/tickets.csv`, cleans it into `data/processed/tickets_cleaned.csv`, creates `data/processed/sample_analysis.xlsx`, and loads the SQLite development database. Start fresh by deleting those generated data files.

## SQL Server setup

Copy `.env.example` to `.env`, set `DB_DIALECT=mssql`, populate SQL Server credentials, then run `database/schema.sql` in SQL Server. The Python configuration uses SQLAlchemy with PyODBC and never stores credentials in source control. SQLite remains the default local development option.

## Tests

```powershell
pytest -q
```

## Architecture

`app/data.py` handles generation, validation and cleaning; `app/analytics.py` provides reusable KPIs and segment metrics; `app/main.py` is the Streamlit interface. SQL Server schema is in `database/`, business queries are in `sql/`, automated tests are in `tests/`, analysis is in `analysis/`, and supporting documentation is in `docs/`.

## KPIs

Total/open/resolved tickets, resolution rate, mean and median resolution hours, SLA compliance and breach rate, first response hours, customer satisfaction, and reopened-ticket rate. See [analytics documentation](docs/analytics.md).

## Limitations and next steps

The generated records are intentionally realistic but synthetic, so they should not be used for operational decisions. Production deployment would add scheduled ingestion, role-based access, source-system identifiers, and a migration-based database loader.

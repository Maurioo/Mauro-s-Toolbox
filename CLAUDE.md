# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Mauro's Toolbox** is a multi-component analytics platform combining:
- **NBA Analytics Dashboard** — CSV-driven stats and ML predictions (scikit-learn RandomForestRegressor)
- **CRM Tools Suite** — Request Builder (multi-step form wizard) and Document Classification

## Commands

### Python Backend (Flask, port 5000)
```bash
pip install -r backend/requirements.txt
cd backend && python app.py
# or with auto-install:
python backend/start_app.py
```

### Node.js Backend (Express, port 8000)
```bash
cd backend && npm install && npm start
```

### React Frontend (port 3000, proxies to Flask at 5000)
```bash
cd react-app && npm install && npm start
npm run build        # production build
```

### Tests
```bash
# Python
pytest tests/

# React (Jest + React Testing Library)
cd react-app && npm test
cd react-app && npm test -- --testNamePattern="<test-name>"
```

### Linting
```bash
cd react-app && npx eslint src/
```

## Architecture

The project has **two parallel frontend implementations** (vanilla HTML and React) and **two backend options** (Flask primary, Express secondary).

```
public/          # Standalone vanilla HTML pages (no build needed, open directly)
react-app/src/   # React alternative frontend
backend/app.py   # Primary API (Flask, CSV-based data loading + ML)
backend/server.js # Secondary API (Express, SQL Server integration)
data/            # CSV files (gitignored) — primary data source
etl/             # ETL pipeline scripts
tests/           # pytest test suite
```

### Backend API (`backend/app.py`)
- Flask with CORS enabled
- Loads NBA data from CSV files via pandas at startup
- Uses **query templates** (not raw SQL) for standardized data access
- ML models loaded from `nba_pts_predictor.pkl` / `nba_model_features.pkl` (generated, not committed)
- Health check: `GET /api/health`

### Request Builder (`public/request-builder.html`)
- OOP architecture: abstract `BlockBase` class with `render()`, `validate()`, `getValue()`, `isFilled()`
- 9 concrete block types: `TextInput`, `TextArea`, `Dropdown`, `MultiSelect`, `Date`, `Number`, `ImpactUrgency`, `Scope`, `SelectionDefinition`
- Configuration-driven via `ConfigRepository.getRequestTypes()` — add new request types there
- Audit logs persisted to `localStorage`; form state is in-memory only

### React Frontend (`react-app/src/`)
- Key components: `NBADashboard`, `StatFilters`, `PlayerStatsChart`
- Uses `recharts` for charts, `styled-components` for styling, `framer-motion` for animations
- Proxies API calls to Flask backend (configured in `react-app/package.json`)

### Database
- **Default**: CSV files via pandas (no DB needed)
- **Optional SQL Server**: `localhost\MOCKCRM`, database `nba`, user `nbaUser` (connection in `backend/server.js`)
- **Optional PostgreSQL**: `docker-compose up` (port 3000)

## Key Notes

- The `data/` directory (CSV files) is gitignored — the app will fail to load data if CSVs are missing
- Pre-trained ML model `.pkl` files are also gitignored; run the training pipeline to regenerate them
- The vanilla HTML pages in `public/` are self-contained and work without any backend except `analytics-dashboard.html`, which requires the Flask server
- The project documentation (README.md) is written in Dutch

# Mauro's Toolbox

Een modern analytics en utilities platform met HTML/JavaScript frontend, Python Flask backend en dynamische visualisaties. Zero-database design met focus op CRM-systeem gerelateerde tools.

---

## Projectoverzicht

Dit project bevat twee hoofdcomponenten:

### 1. **NBA Analytics Dashboard**
- Interactief dashboard voor NBA-statistieken en game analysis voor het 2024-2025 seizoen, WIP etl job dat live game data aanvult.
- Volledig gebaseerd op CSV-data (`nba_2025_players.csv`, `nba_2025_teams.csv`, `nba_gamelogs_2025.csv`)
- Real-time filtering, charting en data visualization
- Machine Learning predictions voor game outcomes
- Backend: Flask API op `localhost:5000`

### 2. **CRM Tools Suite**
- **Request Builder**: Configureerbare formulieren voor gestructureerde bedrijfsverzoeken
  - Multi-step wizard (select type → fill form → review → submit)
  - 9 modulaire form blocks (TextInput, Dropdown, MultiSelect, DatePicker, ImpactUrgency, Scope, SelectionDefinition, etc.)
  - Real-time validatie & error handling
  - Audit logging via localStorage
  
- **Document Classification**: AI-powered document categorization tool
- **CRM Menu**: Centraal menu voor alle CRM tools

---

## Snel Starten

### Minimale setup (alleen frontend)
```powershell
# Open de projectmap
cd "c:\Users\mauro\OneDrive\0.1 Programming\Mauro-s-Toolbox"

# Open in browser
start public/index.html                    # Homepagina
```

### Volledige setup (frontend + backend)
```powershell
# 1. Installeer Python dependencies
pip install -r backend/requirements.txt

# 2. Start Flask backend (in afzonderlijke terminal)
cd backend
python app.py
# Backend draait op http://localhost:5000

# 3. Open frontend in browser
cd ..
start public/index.html
```

---

## Vereisten

### Minimaal (alleen frontend tools)
- **Modern web browser** (Chrome, Edge, Firefox)
- Windows / macOS / Linux

### Met backend (analytics dashboard)
- **Python 3.8+** (check: `python --version`)
- **pip** (check: `pip --version`)
- **CSV data files** in `data/` map:
  - `nba_2025_players.csv`
  - `nba_2025_teams.csv`
  - `nba_gamelogs_2025.csv`

---

## Project Structuur

```
Mauro-s-Toolbox/
├── public/                          # Frontend HTML/JS pages
│   ├── index.html                   # Homepage with navigation
│   ├── analytics-dashboard.html      # NBA Analytics Dashboard
│   ├── crm-menu.html                # CRM Tools Menu
│   ├── request-builder.html          # Request Builder (Form wizard)
│   ├── document-classificatie.html   # Document Classification Tool
│   ├── dashboardNBA.html             # NBA Game Query (legacy)
│   └── ...other utilities
│
├── backend/                         # Python Flask API
│   ├── app.py                       # Main Flask application
│   ├── requirements.txt              # Python dependencies
│   └── ...other backend modules
│
├── data/                            # CSV data sources
│   ├── nba_2025_players.csv
│   ├── nba_2025_teams.csv
│   └── ...other datasets
│
├── notebooks/                       # Jupyter notebooks (analysis)
├── etl/                             # ETL pipeline scripts
└── README.md                        # This file
```

---

## Frontend Pages Guide

### `index.html` - Homepage
**Direct access**: Double-click `public/index.html` in File Explorer
- Central navigation hub
- Quick links to all tools
- Modern dark theme with gradient background

### `analytics-dashboard.html` - NBA Analytics
**Requires**: Running Flask backend (`python app.py`)
- Filter data by player, team, date range
- Interactive charts (charts.js)
- Real-time statistics
- ML predictions for game outcomes
- Query builder interface

**Commands**:
```powershell
cd backend
python app.py
# Then open: public/analytics-dashboard.html
```

### `crm-menu.html` - CRM Tools Hub
**Direct access**: No backend required
- Menu for all CRM tools
- Available now: Document Classification, Request Builder
- Card-based interface with status badges

### `request-builder.html` - Dynamic Form Wizard
**Direct access**: No backend required

**Features**:
- Multi-step form wizard (4 steps)
- 3 pre-configured request types:
  1. Ad-hoc Mailing Selection
  2. Portfolio Configuration Change
  3. Bulk RM/Banker Reassignment
  
- Real-time validation
- JSON payload generation
- Audit log viewer (localStorage)
- Non-exportable internal data display

**Code Architecture**:
```javascript
// Data Access Layer
ConfigRepository          
├── getRequestTypes()     // Return all form configs
├── getRequestTypeById()  // Get single config
├── getAuditLogs()        // Read from localStorage
└── saveAuditLog()        // Persist submissions

// Block Base Class (Abstract)
BlockBase                 
├── render()              // Create DOM elements
├── validate()            // Validation logic
├── getValue()            // Return form value
└── isFilled()            // Required field check

// Concrete Block Implementations
├── TextInputBlock
├── TextAreaBlock
├── DropdownBlock
├── MultiSelectBlock
├── DateBlock
├── NumberBlock
├── ImpactUrgencyBlock    // Calculates derived priority
├── ScopeBlock            // Environment + explanation
└── SelectionDefinitionBlock  // 3 modes: IDs, portfolios, rules
```

---

## Installation & Setup

### Step 1: Clone Repository
```powershell
git clone https://github.com/Maurioo/Mauro-s-Toolbox.git
cd Mauro-s-Toolbox
code .  # Open in VSCode
```

### Step 2: Install Backend Dependencies (optional)
```powershell
pip install -r backend/requirements.txt
```

### Step 3: Verify CSV Files
Check that these exist in `data/` folder:
- ✅ `nba_2025_players.csv`
- ✅ `nba_2025_teams.csv`
- ✅ `nba_gamelogs_2025.csv`

### Step 4: Start Services

**Option A: Frontend Only (recommended for testing)**
```powershell
# Just open any HTML file in browser
start public/index.html
```

**Option B: Frontend + Backend (analytics dashboard)**
```powershell
# Terminal 1: Start Flask API
cd backend
python app.py
# Runs on http://localhost:5000

# Terminal 2 or File Explorer: Open frontend
start public/index.html
```

---

## Direct Commands

| Command | Purpose | Environment |
|---------|---------|-------------|
| `start public/index.html` | Open homepage | Frontend only |
| `start public/request-builder.html` | Open request builder | Frontend only |
| `start public/crm-menu.html` | Open CRM menu | Frontend only |
| `pip install -r backend/requirements.txt` | Install Python deps | Backend setup |
| `cd backend && python app.py` | Start Flask API | Backend (localhost:5000) |
| `git push origin main` | Push to GitHub | Git |
| `git status` | Check uncommitted changes | Git |

---

## Form Block Configuration

Each request type is defined as JSON config. Example:

```javascript
{
  id: 'portfolio-config',
  name: 'Portfolio Configuration Change',
  version: '1.0.0',
  description: 'Request changes to portfolio settings',
  blocks: [
    {
      id: 'portfolioId',
      blockType: 'NumberBlock',
      label: 'Portfolio ID',
      required: true,
      validation: { min: 1 },
      hint: 'Numeric portfolio identifier'
    },
    {
      id: 'changeType',
      blockType: 'DropdownBlock',
      label: 'Type of Change',
      required: true,
      options: ['Threshold Update', 'Fee Adjustment', 'Risk Parameters']
    },
    // ... more blocks
  ]
}
```

---

## Extending the Project

### Adding a New Request Type Config

Edit `public/request-builder.html`, find section `ConfigRepository.getRequestTypes()`:

```javascript
{
  id: 'my-request-type',
  name: 'My Request Type',
  version: '1.0.0',
  description: 'Description for users',
  blocks: [
    { id: 'field1', blockType: 'TextInputBlock', label: 'Field 1', required: true },
    { id: 'field2', blockType: 'DropdownBlock', label: 'Field 2', options: ['A', 'B', 'C'] },
    { id: 'field3', blockType: 'ImpactUrgencyBlock', label: 'Priority', required: true }
  ]
}
```

The dropdown in step 1 will auto-populate with your new type.

### Adding a New Form Block Type

1. Create new class extending `BlockBase` in `public/request-builder.html`
2. Implement required methods:
   - `render(container)` — Create DOM elements
   - `validate()` — Return true/false
   - `getValue()` — Return form value
   - `isFilled()` — Check if required field has value

3. Add to `blockMap` in `buildForm()` function:
```javascript
const blockMap = {
  'CustomBlock': () => new CustomBlock(blockConfig),
  // ... other blocks
};
```

4. Use in form config:
```javascript
{ id: 'custom', blockType: 'CustomBlock', label: 'My Custom Field', required: true }
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **CSV files not found** | Ensure files in `data/` folder, check .gitignore not excluding them |
| **Backend not responding** | Check if `python app.py` running, check terminal for errors |
| **CORS errors on requests** | Ensure backend URL matches in frontend fetch calls |
| **localhost:5000 connection refused** | Flask API not started - run `cd backend && python app.py` |
| **Form validation not working** | Open browser console (F12) for JavaScript errors |
| **Audit log not persisting** | Check browser localStorage enabled (DevTools > Application > Storage) |
| **Forms not rendering** | Check block type names match exactly in blockMap |
| **Windows firewall prompt** | Click "Allow" to give Python network access |

---

## Technologies Used

| Layer | Technology |
|-------|-----------|
| **Frontend** | HTML5, Vanilla JavaScript (ES6+), CSS3 |
| **Backend** | Python 3.8+, Flask |
| **Data** | CSV files, pandas processing |
| **Visualization** | Charts.js, custom SVG |
| **Storage** | Browser localStorage (audit logs) |
| **Build** | No build step required (standalone HTML) |

---

## Validation System

All form blocks validate on three triggers:

1. **On Input** — Real-time feedback as user types
2. **On Blur** — When user leaves field (final check)
3. **On Submit** — Before proceeding to review step

Error messages show:
- Required field violations
- Format/regex mismatches
- Length constraints (min/max)
- Custom validation rules
- Numeric range violations

---

## Security Considerations

This is a **proof-of-concept** for internal use. For production deployment:

- ✅ **Server-side validation** required (never trust client)
- ✅ **Authentication & authorization** needed
- ✅ **Entitlement checks** on data access
- ✅ **Audit logging** at database level
- ✅ **HTTPS enforcement** (no localhost in production)
- ✅ **SQL injection prevention** (parameterized queries)
- ✅ **CSRF protection** on forms
- ✅ **Rate limiting** on API endpoints

**Note**: The "non-exportable" UI (watermarks, read-only CSS) is UX friction only, not true security. Real data protection must happen server-side.

---

## Support & Contribution

- **Issues**: Open an issue on [GitHub](https://github.com/Maurioo/Mauro-s-Toolbox/issues)
- **Questions**: Contact Mauro
- **Pull Requests**: Welcome! Follow Git workflow

---

## License & Attribution

Side project for testing data pipelines, ETL processes, and modern web tooling.
Focus on clean architecture, reusable components, and user experience.

---

**Last Updated**: February 2026  
**Version**: 2.0.0  
**Status**: Active Development

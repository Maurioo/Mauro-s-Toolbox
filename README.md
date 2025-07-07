# Mauro's NBA Toolbox

## Projectoverzicht
Dit project is een modern NBA-analytics dashboard dat volledig draait op CSV-data, met flexibele ML/AI-functionaliteit, dynamische visualisaties en een prettige gebruikerservaring. Zowel de backend (Flask) als de frontend (HTML/JS) zijn geoptimaliseerd voor gebruik zonder SQL-database.

---

## Setup & Installatie

### 1. Vereisten
- **Python 3.8+** (aanbevolen: 3.10 of hoger)
- **pip** (Python package manager)
- **Node.js + npm** (voor frontend development, optioneel)
- **De data-bestanden in de map `data/`**

### 2. Dependencies installeren
Open een terminal in de projectmap en voer uit:

```bash
# Backend Python dependencies
pip install -r backend/requirements.txt

# (Optioneel) Frontend dependencies voor development
cd react-app
npm install
cd ..
```

### 3. Data-bestanden
Zorg dat de volgende bestanden aanwezig zijn in de `data/` map:
- `PlayerStats2025_Cleaned.csv`
- `PlayerStats2025_Cumulative.csv`

### 4. Backend starten

```bash
cd backend
python app.py
```
De backend draait nu op [http://localhost:5000](http://localhost:5000)

### 5. Frontend openen
Open `public/analytics-dashboard.html` direct in je browser (dubbelklik of via contextmenu).

**Let op:** De frontend verwacht dat de backend draait op `localhost:5000`.

---

## Extra: Setup script (Windows)
Gebruik het volgende batch-script om alles in één keer te installeren en te starten:

Plaats dit in een bestand `setup_and_run.bat` in de hoofdmap:

```bat
@echo off
cd backend
pip install -r requirements.txt
start python app.py
cd ..
start public/analytics-dashboard.html
```

Dubbelklik op `setup_and_run.bat` om backend en dashboard te starten.

---

## Problemen oplossen
- Controleer of alle dependencies zijn geïnstalleerd.
- Controleer of de CSV-bestanden in de juiste map staan.
- Bij firewall-meldingen: geef Python toegang tot localhost.
- Voor ML/AI-functionaliteit: geen extra model-bestanden nodig, alles draait op pandas/numpy.

---

## Vragen of feedback?
Neem contact op met Mauro of open een issue op GitHub.

## Snel starten in Visual Studio Code op een andere laptop

1. **Open de projectmap in VSCode**
   - Start Visual Studio Code
   - Kies `Bestand > Map openen...` en selecteer de hoofdmap van het project (waar `README.md` en de mappen `backend/`, `public/`, etc. staan)

2. **Open een nieuwe terminal in VSCode**
   - Ga naar `Beeld > Terminal` of druk op <kbd>Ctrl</kbd>+<kbd>`</kbd> (backtick)
   - Controleer dat je in de hoofdmap van het project zit (zie pad boven de terminal)

3. **Installeer Python dependencies**
   - Typ:
     ```bash
     pip install -r backend/requirements.txt
     ```
   - Wacht tot alle packages zijn geïnstalleerd

4. **Controleer of de data-bestanden aanwezig zijn**
   - Controleer of in de map `data/` de bestanden `PlayerStats2025_Cleaned.csv` en `PlayerStats2025_Cumulative.csv` staan

5. **Start de backend (Flask API)**
   - Typ:
     ```bash
     cd backend
     python app.py
     ```
   - De backend draait nu op [http://localhost:5000](http://localhost:5000)

6. **Open het dashboard in je browser**
   - Ga in de Verkenner naar de map `public/`
   - Dubbelklik op `analytics-dashboard.html` om het dashboard te openen
   - (Of open `index.html` voor het startscherm)

7. **(Optioneel) Frontend development**
   - Voor React-ontwikkeling: open een extra terminal en voer uit:
     ```bash
     cd react-app
     npm install
     npm start
     ```
   - De React-app draait dan op [http://localhost:3000](http://localhost:3000)

**Let op:**
- Zorg dat je Python en pip geïnstalleerd hebt (check met `python --version` en `pip --version`)
- Bij eerste keer opstarten kan Windows een firewallmelding geven; sta toegang toe voor Python
- Werkt alles lokaal, geen internet of cloud nodig

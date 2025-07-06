# NBA Dashboard - React + Flask + SQL Server
- "Public -> 'analytics-dashboard.html'"
Een moderne NBA dashboard applicatie met React frontend, Flask backend API en SQL Server database. 
Met Data d.m.v. playwright webscraping basketball-reference (generate -> getNBAGames.py).

## 🏗️ Architectuur

- **Frontend**: React met Recharts voor visualisaties
- **Backend**: Flask API met SQL Server connectie
- **Database**: SQL Server met NBA speler wedstrijdstatistieken

## 🚀 Setup

### 1. Backend Setup (Flask)

```bash
cd backend
pip install flask flask-cors pyodbc pandas
python app.py
```

De Flask API draait op `http://localhost:5000`

### 2. Frontend Setup (React)

```bash
cd frontend
npm install
npm start
```

De React app draait op `http://localhost:3000`

### 3. Database Setup

Zorg dat je SQL Server draait met:
- Instance: MOCKCRM
- Database: nba
- User: nbaUser
- Poort: 50810

## 📊 Features

- **Real-time data**: Data uit SQL Server database, met Webscraping Script (PlayWright, generate -> getNBAGames)
- **Interactieve grafieken**: Bar charts, line charts met Recharts, React
- **Overzicht Totalen en Gemiddelde per Speler** Query op Database met FlashAPI
- **Responsive design**: Werkt op alle apparaten
- **Animaties**: Smooth transitions met Framer Motion

## 🔧 API Endpoints

- `GET /api/health` - Health check
- `GET /api/nba/top-players` - Top 10 spelers op punten
- `GET /api/nba/player-stats/<stat_type>` - Spelers op specifieke stat
- `GET /api/nba/team-stats` - Team statistieken
- `GET /api/nba/player-details/<player_name>` - Speler details

## 🎨 Styling

- Styled Components voor CSS-in-JS
- Glassmorphism effecten
- Responsive grid layout

## 📁 Project Structuur

```
├── backend/
│   ├── app.py              # Flask API
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── App.js         # Main app
│   │   └── index.js       # Entry point
│   └── package.json       # Node dependencies
└── README.md
```

## 🛠️ Development

### Backend Development
```bash
cd backend
python app.py
```

### Frontend Development
```bash
cd frontend
npm start
```

### Database Queries
Test je database connectie:
```sql
SELECT TOP 10 * FROM dbo.nbaPlayerTotals ORDER BY PTS DESC
```

## 🚀 Deployment

1. Build React app: `npm run build`
2. Deploy Flask API naar je server
3. Configureer database connectie
4. Set environment variables

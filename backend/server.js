//CRM functionaliteit: opslaan gebruikers in de database
// deze code is een eenvoudige Express.js server die gebruikersgegevens opslaat in een SQL Server database

const express = require("express");
const path = require("path");
const sql = require("mssql");
const cron = require("node-cron");
const { scrapeAndStore } = require("./scraper");
const cors = require('cors');

const app = express();
const port = 8000;

// Aanbevolen configuratie voor named instance 'MOCKCRM' op localhost:;
const config = {
  user: 'nbaUser',
  password: 'test123',
  server: 'localhost',
  port: 50810, // bijvoorbeeld 49172
  database: 'nba',
  options: {
    trustServerCertificate: true,
    enableArithAbort: true
  }
};

app.use(express.static(path.join(__dirname, "../public")));
app.use(express.json()); // om JSON binnenkomend te kunnen lezen
app.use(cors());

app.post("/api/users", (req, res) => {
  console.log("Ontvangen:", req.body);
  res.json({ message: "Gebruiker opgeslagen!", data: req.body });
});

// GET algemene statistieken (meest recente datum)
app.get("/api/nba/stats", async (req, res) => {
  try {
    const pool = await sql.connect(config);
    const result = await pool.request()
      .query(`
        SELECT Label, Value
        FROM dbo.NBA_Dashboard
        WHERE StatDate = (SELECT MAX(StatDate) FROM dbo.NBA_Dashboard)
      `);
    res.json(result.recordset);
    pool.close();
  } catch (err) {
    console.error("❌ /api/nba/stats error:", err);
    return res.status(500).json({ error: err.message });
  }
});

// GET top-spelers trends
app.get("/api/nba/trends", async (req, res) => {
  try {
    const pool = await sql.connect(config);
    const result = await pool.request()
      .query(`
        SELECT PlayerName AS name, StatValue AS value
        FROM dbo.NBA_Trends
        WHERE StatDate = (SELECT MAX(StatDate) FROM dbo.NBA_Trends)
      `);
    res.json(result.recordset);
    pool.close();
  } catch (err) {
    console.error("❌ /api/nba/trends error:", err);
    return res.status(500).json({ error: err.message });
  }
});

app.get('/api/nbaPlayerTotals', async (req, res) => {
  try {
    await sql.connect(config);
    const result = await sql.query('SELECT * FROM dbo.nbaPlayerTotals');
    res.json(result.recordset);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/nbaPlayerTotals/top10/:stat', async (req, res) => {
  const stat = req.params.stat;
  // Mapping van stat naar kolomnaam in de database
  const statMap = {
    PPG: 'PTS',
    RPG: 'TRB',
    APG: 'AST',
    TP: 'PTS',
    TR: 'TRB',
    TA: 'AST',
    MPG: 'MP'
  };
  const col = statMap[stat] || 'PTS';
  try {
    await sql.connect(config);
    const result = await sql.query(`
      SELECT TOP 10 * FROM dbo.nbaPlayerTotals
      ORDER BY [${col}] DESC
    `);
    res.json(result.recordset);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.listen(port, () => {
  console.log(`API draait op http://localhost:${port}`);
});
//CRM functionaliteit: opslaan gebruikers in de database
// deze code is een eenvoudige Express.js server die gebruikersgegevens opslaat in een SQL Server database

const express = require("express");
const path = require("path");
const sql = require("mssql");
const cron = require("node-cron");
const { scrapeAndStore } = require("./scraper");

const app = express();
const port = 8000;

// Aanbevolen configuratie voor named instance 'MOCKCRM' op localhost:
const config = {
  server: "localhost",
  database: "nba",
  user: "nbaUser",           // je nieuw aangemaakte SQL-login
  password: "test123",
  options: {
    instanceName: "MOCKCRM",  // je named instance
    trustServerCertificate: true
  },
  // evt.: verhoog timeout
  connectionTimeout: 30000,
  requestTimeout: 30000
};


app.use(express.static(path.join(__dirname, "../public")));
app.use(express.json()); // om JSON binnenkomend te kunnen lezen

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

app.listen(port, () => {
  console.log(`API draait op http://localhost:${port}`);
});

// scraper functionaliteit: dagelijkse NBA-scrape en opslaan in SQL Server
// deze code gebruikt node-cron om elke dag om 06:00 een NBA-scrape uit te voeren en de resultaten op te slaan in een SQL Server database

// Plan: elke dag om 06:00 (aanpasbaar)
cron.schedule("0 6 * * *", () => {
  console.log("Start dagelijkse NBA-scrape…");
  scrapeAndStore().catch(console.error);
});

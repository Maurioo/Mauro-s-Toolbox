// scraper.js
const axios     = require("axios");
const cheerio   = require("cheerio");
// const sql       = require("mssql");
// const config    = {
//   user: 'PNC\\mauro',
//   password: '',
//   server: 'localhost\\MOCKCRM', // of jouw instantie
//   database: 'nba',
//   options: { trustServerCertificate: true }
// };

async function scrapeAndStore() {
  // 1) Scrape basketball-reference (voorbeeld: league totals)
  const url = "https://www.basketball-reference.com/leagues/NBA_2025_totals.html";
  const { data: html } = await axios.get(url);
  const $ = cheerio.load(html);

  const statDate = new Date().toISOString().slice(0,10); // 'YYYY-MM-DD'

  // 2) Parse enkele key-stats (pas selectors aan naar gewenste rijen)
  const stats = [
    { label: "Aantal spelers", selector: "#totals_stats .poptip" /* voorbeeld */ },
    // Voeg hier meer toe...
  ].map(s => ({
    label: s.label,
    value: parseFloat($(s.selector).first().text()) || 0
  }));

  // 3) Parse top-spelers (bijv. eerste 4 rijen)
  const trends = [];
  $("#totals_stats tbody tr").slice(0,4).each((i, row) => {
    const cells = $(row).find("td");
    const name  = $(cells[1]).text().trim();
    const pts   = $(cells[26]).text().trim(); // PTS-kolom index
    trends.push({ name, value: pts + " PTS" });
  });

  // 4) Opslaan in SQL Server
//   let pool = await sql.connect(config);

//   // General stats
//   for (let s of stats) {
//     await pool.request()
//       .input("d", sql.Date, statDate)
//       .input("lab", sql.NVarChar(100), s.label)
//       .input("val", sql.Float, s.value)
//       .query(`
//         MERGE dbo.NBA_Dashboard AS target
//         USING (SELECT @d AS StatDate, @lab AS Label) AS src
//         ON target.StatDate = src.StatDate AND target.Label = src.Label
//         WHEN MATCHED THEN
//           UPDATE SET Value = @val
//         WHEN NOT MATCHED THEN
//           INSERT (StatDate, Label, Value) VALUES (@d, @lab, @val);
//       `);
//   }

  // Trends
  for (let t of trends) {
    await pool.request()
      .input("d", sql.Date, statDate)
      .input("nm", sql.NVarChar(100), t.name)
      .input("val", sql.NVarChar(100), t.value)
      .query(`
        MERGE dbo.NBA_Trends AS tgt
        USING (SELECT @d AS StatDate, @nm AS PlayerName) AS src
        ON tgt.StatDate = src.StatDate AND tgt.PlayerName = src.PlayerName
        WHEN MATCHED THEN
          UPDATE SET StatValue = @val
        WHEN NOT MATCHED THEN
          INSERT (StatDate, PlayerName, StatValue) VALUES (@d, @nm, @val);
      `);
  }

  console.log(`[${statDate}] Scrape en opslag voltooid.`);
  pool.close();
}

module.exports = { scrapeAndStore };

from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import pandas as pd
from datetime import datetime
import os
import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

app = Flask(__name__, static_folder='../public', static_url_path='')
CORS(app)

# Laad ML-model en feature volgorde bij startup
try:
       MODEL = joblib.load('nba_pts_predictor.pkl')
       MODEL_FEATURES = joblib.load('nba_model_features.pkl')
except FileNotFoundError:
       MODEL = None
       MODEL_FEATURES = None
       print("⚠️  ML-model niet gevonden, ML-functionaliteit is uitgeschakeld.")

# SQL Server configuratie - gebruik dezelfde instellingen als server.js
DB_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    #'port': 50810,
    'database': 'nba',
    'uid': 'nbaUser',
    'pwd': 'test123',
    'trusted_connection': 'no',
    'trust_server_certificate': 'yes',
    'enable_arith_abort': 'yes'
}

def get_db_connection():
    """Maak verbinding met SQL Server database"""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER=localhost\\MOCKCRM;"
        f"DATABASE=nba;"
        f"UID=nbaUser;"
        f"PWD=test123;"
        f"TrustServerCertificate=yes;"
        f"Encrypt=no;"
    )
    return pyodbc.connect(conn_str)

@app.route("/api/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# === DYNAMISCHE QUERY ENDPOINTS ===

@app.route("/api/query", methods=['POST'])
def execute_query():
    """Voer een custom SQL query uit"""
    try:
        data = request.get_json()
        query = data.get('query')
        params = data.get('params', [])
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        
        return jsonify({
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "row_count": len(df)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/query-templates")
def get_query_templates():
    """Haal beschikbare query templates op"""
    templates = {
        # Letterlijk alle totalen en gemiddelde in een platte tabel
        "Overview Major Stat Categories Totals And Averages": {
            "name": "Overview Major Stat Categories Totals and Averages",
            "description": "Points, Rebounds, Assists, Steals, Blocks, Personal Fouls, Turnovers, Games Played",
            "query": """
                select
                player_name,
                sum(pc.PTS) as [Total Points],
                sum(pc.TRB) as [Total Rebounds],
                sum(pc.AST) as [Total Assists],
                sum(pc.STL) as [Total Steals],
                sum(pc.BLK) as [Total Blocks],
                sum(pc.PF)  as [Total Personal Fouls],
                sum(pc.TOV) as [Total Turnovers],
                count(*)    as [Total Games],
                ROUND(AVG(pc.PTS), 2) as [Average Points],
                ROUND(AVG(pc.TRB), 2) as [Average Rebounds],
                ROUND(AVG(pc.AST), 2) as [Average Assists],
                ROUND(AVG(pc.STL), 2) as [Average Steals],
                ROUND(AVG(pc.BLK), 2) as [Average Blocks],
                ROUND(AVG(pc.PF), 2)  as [Average Personal Fouls],
                ROUND(AVG(pc.TOV), 2) as [Average Turnovers]
                from dbo.nbaPlayerStats_Cleaned pc
                group by player_name
                order by [Total Points] desc
            """
        },

        # Verfijning op spelers en uitblikwedstrijden, puur obv punten en efg% een performance score
        "top_performers": {
            "name": "Top Performances",
            "description": "Single Game Highlights",
            "query": """
                WITH Ranked AS (
                    SELECT 
                        [date], team, opp, result, fg, fga, [FG%], [3p], [3pa], [3p%], [2p], [2pa], [2P%], [efg%],
                        ft, fta, [ft%], trb, stl, blk, tov, pf, player_name, pts,
                        RANK() OVER (ORDER BY PTS DESC) AS RankPTS,
                        RANK() OVER (ORDER BY [eFG%] DESC) AS RankEFG,
                        COUNT(*) OVER () AS TotalPlayers
                    FROM dbo.nbaPlayerStats_Cleaned
                ),
                Scored AS (
                    SELECT *,
                        1.0 - CAST(RankPTS - 0.7 AS FLOAT) / (TotalPlayers - 1) AS ScorePTS,
                        1.0 - CAST(RankEFG - 1 AS FLOAT) / (TotalPlayers - 1) AS ScoreEFG
                    FROM Ranked
                ),
                FinalScore AS (
                    SELECT *,
                        (0.7 * ScorePTS + 0.3 * ScoreEFG) AS PerformanceScore
                    FROM Scored
                )
                SELECT 
                    f.[Date], f.Team, CONCAT(f.player_name, ' - ', nba.team_code) AS [Player Name - Team],
                    f.Opp, f.Result, f.FG, f.FGA, f.[FG%], f.[3P], f.[3PA], f.[3P%],
                    f.[2P], f.[2PA], f.[2P%], f.[EFG%], f.FT, f.FTA, f.[FT%],
                    f.TRB, f.STL, f.BLK, f.TOV, f.PF
                FROM FinalScore f
                INNER JOIN nba.dbo.nbaPlayerStats_Cleaned nba 
                    ON f.player_name = nba.player_name AND f.[date] = nba.[date]  -- toegevoegd om rijen correct te matchen
                ORDER BY f.PerformanceScore DESC, f.[Date], f.Team, [Player Name - Team];
            """
        },

        ## TODO nog te bedenken welke aanpak ik hiervoor wil gebruiken
        ##"player_performance": {
        ##    "name": "Speler Performance Analyse",
        ##    "description": "Analyseer speler statistieken per team",
        ##    "query": """
        ##        SELECT 
        ##            player_name,
        ##            team_code,
        ##            PTS,
        ##            TRB,
        ##            AST,
        ##            GS,
        ##            MP,
        ##            CAST(PTS AS FLOAT) / NULLIF(CAST(MP AS FLOAT), 0) as PTS_PER_MINUTE
        ##        FROM dbo.nbaPlayerTotals 
        ##        WHERE MP > 0
        ##        ORDER BY PTS DESC
        ##    """
        ##},
        ## TODO nog te bedenken welke aanpak ik hiervoor wil gebruiken

        ##"team_comparison": {
        ##    "name": "Team Vergelijking",
        ##    "description": "Vergelijk teams op basis van gemiddelde statistieken",
        ##    "query": """
        ##        SELECT 
        ##            team_code,
        ##            COUNT(*) as player_count,
        ##            AVG(CAST(PTS AS FLOAT)) as avg_points,
        ##            AVG(CAST(TRB AS FLOAT)) as avg_rebounds,
        ##            AVG(CAST(AST AS FLOAT)) as avg_assists,
        ##            AVG(CAST(MP AS FLOAT)) as avg_minutes
        ##        FROM dbo.nbaPlayerTotals 
        ##        GROUP BY team_code
        ##        ORDER BY avg_points DESC
        ##    """
        ##},
        
        ## TODO nog te bedenken welke aanpak ik hiervoor wil gebruiken
        ##"efficiency_analysis": {
        ##    "name": "Efficiëntie Analyse",
        ##    "description": "Spelers gerangschikt op efficiëntie (punten per minuut)",
        ##    "query": """
        ##        SELECT 
        ##            player_name,
        ##            team_code,
        ##            PTS,
        ##            MP,
        ##            CAST(PTS AS FLOAT) / NULLIF(CAST(MP AS FLOAT), 0) as efficiency,
        ##            GS
        ##        FROM dbo.nbaPlayerTotals 
        ##        WHERE MP > 0
        ##        ORDER BY efficiency DESC
        ##    """
        ##}
    }
    return jsonify(templates)

@app.route("/api/query-template/<template_name>")
def execute_query_template(template_name):
    """Voer een query template uit"""
    try:
        templates = {
            "Overview Major Stat Categories Totals And Averages": """
                select
                player_name,
                sum(pc.PTS) as [Total Points],
                sum(pc.TRB) as [Total Rebounds],
                sum(pc.AST) as [Total Assists],
                sum(pc.STL) as [Total Steals],
                sum(pc.BLK) as [Total Blocks],
                sum(pc.PF)  as [Total Personal Fouls],
                sum(pc.TOV) as [Total Turnovers],
                count(*)    as [Total Games],
                ROUND(AVG(pc.PTS), 2) as [Average Points],
                ROUND(AVG(pc.TRB), 2) as [Average Rebounds],
                ROUND(AVG(pc.AST), 2) as [Average Assists],
                ROUND(AVG(pc.STL), 2) as [Average Steals],
                ROUND(AVG(pc.BLK), 2) as [Average Blocks],
                ROUND(AVG(pc.PF), 2)  as [Average Personal Fouls],
                ROUND(AVG(pc.TOV), 2) as [Average Turnovers]
                from dbo.nbaPlayerStats_Cleaned pc
                group by player_name
                order by [Total Points] desc
            """,
            "top_performers": """
                WITH Ranked AS (
                    SELECT 
                        [date], team, opp, result, fg, fga, [FG%], [3p], [3pa], [3p%], [2p], [2pa], [2P%], [efg%],
                        ft, fta, [ft%], trb, stl, blk, tov, pf, player_name, pts,
                        RANK() OVER (ORDER BY PTS DESC) AS RankPTS,
                        RANK() OVER (ORDER BY [eFG%] DESC) AS RankEFG,
                        COUNT(*) OVER () AS TotalPlayers
                    FROM dbo.nbaPlayerStats_Cleaned
                ),
                Scored AS (
                    SELECT *,
                        1.0 - CAST(RankPTS - 0.7 AS FLOAT) / (TotalPlayers - 1) AS ScorePTS,
                        1.0 - CAST(RankEFG - 1 AS FLOAT) / (TotalPlayers - 1) AS ScoreEFG
                    FROM Ranked
                ),
                FinalScore AS (
                    SELECT *,
                        (0.7 * ScorePTS + 0.3 * ScoreEFG) AS PerformanceScore
                    FROM Scored
                )
                SELECT 
                    f.[Date], f.Team, CONCAT(f.player_name, ' - ', nba.team_code) AS [Player Name - Team],
                    f.Opp, f.Result, f.FG, f.FGA, f.[FG%], f.[3P], f.[3PA], f.[3P%],
                    f.[2P], f.[2PA], f.[2P%], f.[EFG%], f.FT, f.FTA, f.[FT%],
                    f.TRB, f.STL, f.BLK, f.TOV, f.PF
                FROM FinalScore f
                INNER JOIN nba.dbo.nbaPlayerStats_Cleaned nba 
                    ON f.player_name = nba.player_name AND f.[date] = nba.[date]  -- toegevoegd om rijen correct te matchen
                ORDER BY f.PerformanceScore DESC, f.[Date], f.Team, [Player Name - Team];
            """
            ##"top_performers": """
            ##    WITH Ranked AS (
            ##        SELECT 
            ##            [date], team, opp, result, fg, fga, [FG%], [3p], [3pa], [3p%], [2p], [2pa], [2P%], [efg%],
            ##            ft, fta, [ft%], trb, stl, blk, tov, pf, player_name, pts,
            ##            RANK() OVER (ORDER BY PTS DESC) AS RankPTS,
            ##            RANK() OVER (ORDER BY [eFG%] DESC) AS RankEFG,
            ##            COUNT(*) OVER () AS TotalPlayers
            ##        FROM dbo.nbaPlayerStats_Cleaned
            ##    ),
            ##    Scored AS (
            ##        SELECT *,
            ##            1.0 - CAST(RankPTS - 1 AS FLOAT) / (TotalPlayers - 1) AS ScorePTS,
            ##            1.0 - CAST(RankEFG - 1 AS FLOAT) / (TotalPlayers - 1) AS ScoreEFG
            ##        FROM Ranked
            ##    ),
            ##    FinalScore AS (
            ##        SELECT *,
            ##            (0.7 * ScorePTS + 0.3 * ScoreEFG) AS PerformanceScore
            ##        FROM Scored
            ##    )
            ##    SELECT 
            ##        f.[Date], f.Team, CONCAT(f.player_name, ' - ', nba.team_code) AS [Player Name - Team],
            ##        f.Opp, f.Result, f.FG, f.FGA, f.[FG%], f.[3P], f.[3PA], f.[3P%],
            ##        f.[2P], f.[2PA], f.[2P%], f.[EFG%], f.FT, f.FTA, f.[FT%],
            ##        f.TRB, f.STL, f.BLK, f.TOV, f.PF
            ##    FROM FinalScore f
            ##    INNER JOIN nba.dbo.nbaPlayerStats_Cleaned nba 
            ##        ON f.player_name = nba.player_name AND f.[date] = nba.[date]  -- toegevoegd om rijen correct te matchen
            ##    ORDER BY f.PerformanceScore DESC, f.[Date], f.Team, [Player Name - Team];
            ##""",
            ##"category_leaders": """
            ##    select
            ##    player_name,
            ##    sum(pc.PTS) as [Total Points],
            ##    sum(pc.TRB) as [Total Rebounds],
            ##    sum(pc.AST) as [Total Assists],
            ##    sum(pc.STL) as [Total Steals],
            ##    sum(pc.BLK) as [Total Blocks],
            ##    sum(pc.PF)  as [Total Personal Fouls],
            ##    sum(pc.TOV) as [Total Turnovers],
            ##    count(*)    as [Total Games],
            ##    ROUND(AVG(pc.PTS), 2) as [Average Points],
            ##    ROUND(AVG(pc.TRB), 2) as [Average Rebounds],
            ##    ROUND(AVG(pc.AST), 2) as [Average Assists],
            ##    ROUND(AVG(pc.STL), 2) as [Average Steals],
            ##    ROUND(AVG(pc.BLK), 2) as [Average Blocks],
            ##    ROUND(AVG(pc.PF), 2)  as [Average Personal Fouls],
            ##    ROUND(AVG(pc.TOV), 2) as [Average Turnovers]
            ##    from dbo.nbaPlayerStats_Cleaned pc
            ##    group by player_name
            ##    order by [Total Points] desc
            ##""",
            ##"efficiency_analysis": """
            ##    SELECT 
            ##        player_name,
            ##        team_code,
            ##        PTS,
            ##        MP,
            ##        CAST(PTS AS FLOAT) / NULLIF(CAST(MP AS FLOAT), 0) as efficiency,
            ##        GS
            ##    FROM dbo.nbaPlayerTotals 
            ##    WHERE MP > 0
            ##    ORDER BY efficiency DESC
            ##"""
        }
        
        if template_name not in templates:
            return jsonify({"error": "Template not found"}), 404
        
        conn = get_db_connection()
        df = pd.read_sql(templates[template_name], conn)
        conn.close()
        
        return jsonify({
            "success": True,
            "template": template_name,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "row_count": len(df)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === ML/AI VOORBEREIDING ENDPOINTS ===

@app.route("/api/ml/features")
def get_ml_features():
    """Haal features op voor machine learning"""
    try:
        conn = get_db_connection()
        query = """
            SELECT 
                player_name,
                team_code,
                PTS,
                TRB,
                AST,
                GS,
                CAST(PTS AS FLOAT) / NULLIF(CAST(MP AS FLOAT), 0) as PTS_PER_MINUTE,
                CAST(TRB AS FLOAT) / NULLIF(CAST(MP AS FLOAT), 0) as REB_PER_MINUTE,
                CAST(AST AS FLOAT) / NULLIF(CAST(MP AS FLOAT), 0) as AST_PER_MINUTE
            FROM dbo.nbaPlayerTotals 
            WHERE MP > 0
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        return jsonify({
            "success": True,
            "features": df.to_dict('records'),
            "feature_columns": ['PTS', 'TRB', 'AST', 'GS', 'PTS_PER_MINUTE', 'REB_PER_MINUTE', 'AST_PER_MINUTE']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ml/predict", methods=['POST'])
def ml_predict():
    """
    Verwacht JSON met 'player', 'team', 'opp'. Haalt rolling averages uit de database.
    """
    try:
        if MODEL is None or MODEL_FEATURES is None:
            return jsonify({"error": "ML-model niet beschikbaar"}), 503
        data = request.get_json()
        player = data['player']
        team = data['team']
        opp = data['opp']

        conn = get_db_connection()
        # Haal de laatste 5 wedstrijden van deze speler op
        query = """
            SELECT TOP 5 PTS, TRB, AST
            FROM dbo.nbaPlayerStats_Cleaned
            WHERE player_name = '?' AND team_code = '?'
            ORDER BY [Date] DESC
        """
        df = pd.read_sql(query, conn, params=[player, team])
        conn.close()

        if df.empty or len(df) < 1:
            return jsonify({"error": "Niet genoeg data voor deze speler/team"}), 400

        # Rolling averages
        features = {
            'PTS_avg5': df['PTS'].mean(),
            'TRB_avg5': df['TRB'].mean(),
            'AST_avg5': df['AST'].mean(),
            f'team_code_{team}': 1,
            f'Opp_{opp}': 1
        }
        # Vul ontbrekende features aan met 0
        for col in MODEL_FEATURES:
            if col not in features:
                features[col] = 0

        X_pred = pd.DataFrame([features], columns=MODEL_FEATURES).fillna(0)
        pred = MODEL.predict(X_pred)[0]
        return jsonify({"success": True, "predicted_pts": float(pred)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === BESTAANDE ENDPOINTS (behouden voor backward compatibility) ===

@app.route("/api/nba/top-players")
def get_top_players():
    """Haal top 10 spelers op basis van punten"""
    try:
        conn = get_db_connection()
        query = """
        SELECT TOP 10 
            player_name,
            team_code,
            PTS,
            TRB,
            AST,
            GS,
            MP
        FROM dbo.nbaPlayerTotals 
        ORDER BY PTS DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"Error in get_top_players: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/nba/player-stats/<stat_type>")
def get_player_stats_by_type(stat_type):
    """Haal top 10 spelers op basis van specifieke statistiek"""
    try:
        conn = get_db_connection()
        
        # Mapping van stat type naar database kolom
        stat_mapping = {
            'ppg': 'PTS',
            'rpg': 'TRB', 
            'apg': 'AST',
            'mpg': 'MP'
        }
        
        column = stat_mapping.get(stat_type.lower(), 'PTS')
        
        query = f"""
        SELECT TOP 10 
            player_name,
            team_code,
            PTS,
            TRB,
            AST,
            GS,
            MP
        FROM dbo.nbaPlayerTotals 
        ORDER BY [{column}] DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"Error in get_player_stats_by_type: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/nba/team-stats")
def get_team_stats():
    """Haal team statistieken op"""
    try:
        conn = get_db_connection()
        query = """
        SELECT 
            team_code,
            COUNT(*) as player_count,
            AVG(CAST(PTS AS FLOAT)) as avg_points,
            AVG(CAST(TRB AS FLOAT)) as avg_rebounds,
            AVG(CAST(AST AS FLOAT)) as avg_assists
        FROM dbo.nbaPlayerTotals 
        GROUP BY team_code
        ORDER BY avg_points DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return jsonify(df.to_dict('records'))
    except Exception as e:
        print(f"Error in get_team_stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/nba/player-details/<player_name>")
def get_player_details(player_name):
    """Haal gedetailleerde speler statistieken op"""
    try:
        conn = get_db_connection()
        query = """
        SELECT *
        FROM dbo.nbaPlayerTotals 
        WHERE player_name = ?
        """
        df = pd.read_sql(query, conn, params=[player_name])
        conn.close()
        
        if df.empty:
            return jsonify({"error": "Player not found"}), 404
            
        return jsonify(df.to_dict('records')[0])
    except Exception as e:
        print(f"Error in get_player_details: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/cumulative/points/top20')
def get_cumulative_points_top20():
    """Geeft voor de top 20 spelers (hoogste PPG) het cumulatieve puntenverloop per datum terug."""
    try:
        conn = get_db_connection()
        query = '''
        WITH Top20 AS (
            SELECT TOP 20 player_name, AVG(CAST(PTS AS FLOAT)) AS ppg
            FROM dbo.nbaPlayerStats_Cumulative
            GROUP BY player_name
            ORDER BY ppg DESC
        )
        SELECT c.Date, c.player_name, c.team_code,
               SUM(c.PTS) OVER (PARTITION BY c.player_name ORDER BY c.Date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_pts
        FROM dbo.nbaPlayerStats_Cumulative c
        INNER JOIN Top20 t ON c.player_name = t.player_name
        ORDER BY c.player_name, c.Date
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        # Zet datum om naar string voor JSON serialisatie
        df['Date'] = df['Date'].astype(str)
        return jsonify({
            "success": True,
            "data": df.to_dict('records'),
            "players": df['player_name'].unique().tolist(),
            "dates": sorted(df['Date'].unique().tolist())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cumulative/stat', methods=['POST'])
def get_cumulative_stat():
    """Geeft voor een lijst spelers en een stat het cumulatieve verloop per datum terug."""
    try:
        data = request.get_json()
        players = data.get('players', [])
        stat = data.get('stat', 'PTS')
        if not players or not stat:
            return jsonify({"error": "players en stat zijn verplicht"}), 400
        # Maak een string voor de IN-clause
        placeholders = ','.join(['?'] * len(players))
        query = f'''
        SELECT c.Date, c.player_name, c.team_code,
               c.[{stat}] AS cumulative_stat
        FROM dbo.nbaPlayerStats_Cumulative c
        WHERE c.player_name IN ({placeholders})
        ORDER BY c.player_name, c.Date
        '''
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=players)
        conn.close()
        df['Date'] = df['Date'].astype(str)
        return jsonify({
            "success": True,
            "data": df.to_dict('records'),
            "players": df['player_name'].unique().tolist(),
            "dates": sorted(df['Date'].unique().tolist()),
            "stat": stat
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/overview-totals')
def overview_totals():
    """Geeft per speler en team de totalen en correcte percentages terug."""
    try:
        conn = get_db_connection()
        query = '''
        SELECT
            player_name,
            SUM(PTS) AS [Total Points],
            SUM(AST) AS [Total Assists],
            SUM(TRB) AS [Total Rebounds],
            SUM(STL) AS [Total Steals],
            SUM(BLK) AS [Total Blocks],
            SUM(TOV) AS [Total Turnovers],
            SUM(PF)  AS [Total Personal Fouls],
            CASE WHEN SUM(FGA) > 0 THEN CAST(SUM(FG) AS FLOAT) / SUM(FGA) ELSE NULL END AS [FG%],
            SUM(FG)  AS [Total FG],
            SUM(FGA) AS [Total FGA],
            CASE WHEN SUM([3PA]) > 0 THEN CAST(SUM([3P]) AS FLOAT) / SUM([3PA]) ELSE NULL END AS [3P%],
            SUM([3P])  AS [Total 3P],
            SUM([3PA]) AS [Total 3PA],
            CASE WHEN SUM([2PA]) > 0 THEN CAST(SUM([2P]) AS FLOAT) / SUM([2PA]) ELSE NULL END AS [2P%],
            SUM([2P])  AS [Total 2P],
            SUM([2PA]) AS [Total 2PA],
            CASE WHEN SUM(FTA) > 0 THEN CAST(SUM(FT) AS FLOAT) / SUM(FTA) ELSE NULL END AS [FT%],
            SUM(FT)  AS [Total FT],
            SUM(FTA) AS [Total FTA],
            CASE WHEN SUM(FGA) > 0 THEN CAST((SUM(FG) + 0.5 * SUM([3P])) AS FLOAT) / SUM(FGA) ELSE NULL END AS [eFG%],
            SUM(ORB) AS [Total ORB],
            SUM(DRB) AS [Total DRB],
            team_code
        FROM [nba].[dbo].[nbaPlayerStats_Cleaned]
        GROUP BY player_name, team_code
        ORDER BY [Total Points] DESC
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        df = df.replace({np.nan: None})
        return jsonify({
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "row_count": len(df)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/overview-totals/sorted', methods=['POST'])
def overview_totals_with_sort():
    """Geeft per speler en team de totalen en correcte percentages terug met dynamische sortering."""
    try:
        data = request.get_json() or {}
        sort_column = data.get('sort_column', 'Total Points')
        sort_direction = data.get('sort_direction', 'DESC')
        
        # Debug logging
        print(f"DEBUG: Received sort_column: '{sort_column}', sort_direction: '{sort_direction}'")
        
        # Map frontend kolomnamen naar database kolomnamen
        column_mapping = {
            'Total Points': '[Total Points]',
            'Total Assists': '[Total Assists]',
            'Total Rebounds': '[Total Rebounds]',
            'Total Steals': '[Total Steals]',
            'Total Blocks': '[Total Blocks]',
            'Total Turnovers': '[Total Turnovers]',
            'Total Personal Fouls': '[Total Personal Fouls]',
            'Total FG': '[Total FG]',
            'Total FGA': '[Total FGA]',
            'Total 3P': '[Total 3P]',
            'Total 3PA': '[Total 3PA]',
            'Total 2P': '[Total 2P]',
            'Total 2PA': '[Total 2PA]',
            'Total FT': '[Total FT]',
            'Total FTA': '[Total FTA]',
            'Total ORB': '[Total ORB]',
            'Total DRB': '[Total DRB]',
            'player_name': 'player_name',
            'team_code': 'team_code'
        }
        
        # Bepaal de juiste ORDER BY clause
        if sort_column in column_mapping:
            order_by = f"ORDER BY {column_mapping[sort_column]} {sort_direction}"
            print(f"DEBUG: Using mapped column: {column_mapping[sort_column]}")
        else:
            order_by = "ORDER BY [Total Points] DESC"
            print(f"DEBUG: Column '{sort_column}' not found in mapping, using fallback")
        
        print(f"DEBUG: Final ORDER BY clause: {order_by}")
        
        conn = get_db_connection()
        query = f'''
        SELECT
            player_name,
            SUM(PTS) AS [Total Points],
            SUM(AST) AS [Total Assists],
            SUM(TRB) AS [Total Rebounds],
            SUM(STL) AS [Total Steals],
            SUM(BLK) AS [Total Blocks],
            SUM(TOV) AS [Total Turnovers],
            SUM(PF)  AS [Total Personal Fouls],
            CASE WHEN SUM(FGA) > 0 THEN CAST(SUM(FG) AS FLOAT) / SUM(FGA) ELSE NULL END AS [FG%],
            SUM(FG)  AS [Total FG],
            SUM(FGA) AS [Total FGA],
            CASE WHEN SUM([3PA]) > 0 THEN CAST(SUM([3P]) AS FLOAT) / SUM([3PA]) ELSE NULL END AS [3P%],
            SUM([3P])  AS [Total 3P],
            SUM([3PA]) AS [Total 3PA],
            CASE WHEN SUM([2PA]) > 0 THEN CAST(SUM([2P]) AS FLOAT) / SUM([2PA]) ELSE NULL END AS [2P%],
            SUM([2P])  AS [Total 2P],
            SUM([2PA]) AS [Total 2PA],
            CASE WHEN SUM(FTA) > 0 THEN CAST(SUM(FT) AS FLOAT) / SUM(FTA) ELSE NULL END AS [FT%],
            SUM(FT)  AS [Total FT],
            SUM(FTA) AS [Total FTA],
            CASE WHEN SUM(FGA) > 0 THEN CAST((SUM(FG) + 0.5 * SUM([3P])) AS FLOAT) / SUM(FGA) ELSE NULL END AS [eFG%],
            SUM(ORB) AS [Total ORB],
            SUM(DRB) AS [Total DRB],
            team_code
        FROM [nba].[dbo].[nbaPlayerStats_Cleaned]
        GROUP BY player_name, team_code
        {order_by}
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        df = df.replace({np.nan: None})
        return jsonify({
            "success": True,
            "data": df.to_dict('records'),
            "columns": df.columns.tolist(),
            "row_count": len(df),
            "sort_column": sort_column,
            "sort_direction": sort_direction
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cumulative/top10')
def get_cumulative_top10():
    """Cumulatieve punten per dag voor top 10 spelers (hardcoded lijst)"""
    try:
        # Haal de top 10 spelers op uit de database op basis van totale punten
        conn = get_db_connection()
        top10_query = """
            SELECT TOP 10 player_name
            FROM [nba].[dbo].[nbaPlayerStats_Cleaned]
            GROUP BY player_name
            ORDER BY SUM(PTS) DESC
        """
        top10_df = pd.read_sql(top10_query, conn)
        top10 = top10_df['player_name'].tolist()
        conn.close()
        placeholders = ','.join(['?'] * len(top10))
        query = f"""
            SELECT player_name, [Date], 
                PTS AS cumulative_pts
            FROM nba.dbo.nbaPlayerStats_Cumulative
            WHERE player_name IN ({placeholders})
            ORDER BY player_name, [Date]
        """
        conn = get_db_connection()
        df = pd.read_sql(query, conn, params=top10)
        conn.close()
        df['Date'] = df['Date'].astype(str)
        return jsonify({
            "success": True,
            "data": df.to_dict('records'),
            "players": df['player_name'].unique().tolist(),
            "dates": sorted(df['Date'].unique().tolist())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-performances-ml')
def top_performances_ml():
    """Geeft de top 50 beste individuele wedstrijden volgens een ML-performance score."""
    try:
        conn = get_db_connection()
        query = '''
        SELECT [Date], player_name, team_code, PTS, TRB, AST, STL, BLK, TOV, [FG%], [eFG%]
        FROM dbo.nbaPlayerStats_Cleaned
        WHERE player_name IS NOT NULL AND PTS IS NOT NULL
        '''
        df = pd.read_sql(query, conn)
        conn.close()
        # Drop rows met missende waarden
        df = df.dropna()
        # Features voor ML (MP uitgesloten vanwege datetime.time problemen)
        features = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'eFG%']
        # Handgemaakte score als target
        df['perf_score'] = (
            df['PTS'] +
            1.2 * df['AST'] +
            1.2 * df['TRB'] +
            1.5 * df['STL'] +
            1.5 * df['BLK'] -
            1.0 * df['TOV']
        ) * (df['eFG%'] + 0.5)
        X = df[features]
        y = df['perf_score']
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        pipeline.fit(X, y)
        df['ml_score'] = pipeline.predict(X)
        # Top 50 beste wedstrijden
        top_games = df.sort_values('ml_score', ascending=False).head(50)
        # Zet datum om naar string
        top_games['Date'] = top_games['Date'].astype(str)
        return jsonify({
            'success': True,
            'data': top_games.to_dict('records'),
            'columns': list(top_games.columns),
            'row_count': len(top_games)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

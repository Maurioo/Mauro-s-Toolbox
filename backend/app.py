from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import pandas as pd
from datetime import datetime
import os
import json
import joblib

app = Flask(__name__, static_folder='../public', static_url_path='')
CORS(app)

# Laad ML-model en feature volgorde bij startup
MODEL = joblib.load('nba_pts_predictor.pkl')
MODEL_FEATURES = joblib.load('nba_model_features.pkl')

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

if __name__ == "__main__":
    app.run(debug=True, port=5000)

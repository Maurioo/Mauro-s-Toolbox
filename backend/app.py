from flask import Flask, jsonify, request
from flask_cors import CORS
import pyodbc
import pandas as pd
from datetime import datetime
import os
import json
import joblib
import numpy as np
# import sklearn  # Dit is niet strikt nodig tenzij je direct sklearn.something gebruikt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# === CSV DATA LOADERS ===
CLEANED_CSV = os.path.join(os.path.dirname(__file__), '../data/PlayerStats2025_Cleaned.csv')
CUMULATIVE_CSV = os.path.join(os.path.dirname(__file__), '../data/PlayerStats2025_Cumulative.csv')

def load_cleaned_df():
    return pd.read_csv(CLEANED_CSV)

def load_cumulative_df():
    return pd.read_csv(CUMULATIVE_CSV)

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
#DB_CONFIG = {
#    'driver': 'ODBC Driver 17 for SQL Server',
#    'server': 'localhost',
#    #'port': 50810,
#    'database': 'nba',
#    'uid': 'nbaUser',
#    'pwd': 'test123',
#    'trusted_connection': 'no',
#    'trust_server_certificate': 'yes',
#    'enable_arith_abort': 'yes'
#}

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
    """Voer een custom SQL query uit (nu alleen pandas queries op CSV)"""
    try:
        data = request.get_json()
        query = data.get('query')
        # params = data.get('params', [])  # niet meer nodig
        if not query:
            return jsonify({"error": "Query is required"}), 400
        # Detecteer welke CSV gebruikt moet worden
        if 'nbaPlayerStats_Cleaned' in query:
            df = load_cleaned_df()
        elif 'nbaPlayerStats_Cumulative' in query:
            df = load_cumulative_df()
        else:
            return jsonify({"error": "Alleen queries op PlayerStats2025_Cleaned.csv en PlayerStats2025_Cumulative.csv worden ondersteund."}), 400
        # Evalueer de query als pandas expressie (beperkt, alleen SELECT ... FROM ... WHERE ... GROUP BY ... ORDER BY ...)
        # Simpele parser: alleen SELECT kolommen FROM ... WHERE ... GROUP BY ... ORDER BY ...
        # Voor nu: alleen enkele standaard queries ondersteunen
        # (Voor custom queries: geef een foutmelding terug)
        return jsonify({"error": "Custom SQL queries worden niet meer ondersteund. Gebruik de query templates."}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/query-templates")
def get_query_templates():
    """Haal beschikbare query templates op (nu alleen pandas)"""
    templates = {
        "Overview Major Stat Categories Totals And Averages": {
            "name": "Overview Major Stat Categories Totals and Averages",
            "description": "Points, Rebounds, Assists, Steals, Blocks, Personal Fouls, Turnovers, Games Played",
            "query": "overview_totals"
        },
        "top_performers": {
            "name": "Top Performances",
            "description": "Single Game Highlights",
            "query": "top_performers"
        }
    }
    return jsonify(templates)

@app.route("/api/query-template/<template_name>")
def execute_query_template(template_name):
    """Voer een query template uit (nu via pandas)"""
    try:
        if template_name == "Overview Major Stat Categories Totals And Averages":
            df = load_cleaned_df()
            agg = df.groupby('player_name').agg({
                'PTS': 'sum',
                'TRB': 'sum',
                'AST': 'sum',
                'STL': 'sum',
                'BLK': 'sum',
                'PF': 'sum',
                'TOV': 'sum',
                'PTS': ['mean'],
                'TRB': ['mean'],
                'AST': ['mean'],
                'STL': ['mean'],
                'BLK': ['mean'],
                'PF': ['mean'],
                'TOV': ['mean'],
                'player_name': 'count'
            })
            agg.columns = [
                'Total Points', 'Total Rebounds', 'Total Assists', 'Total Steals', 'Total Blocks',
                'Total Personal Fouls', 'Total Turnovers',
                'Average Points', 'Average Rebounds', 'Average Assists', 'Average Steals',
                'Average Blocks', 'Average Personal Fouls', 'Average Turnovers', 'Total Games'
            ]
            agg = agg.reset_index()
            agg = agg.sort_values('Total Points', ascending=False)
            return jsonify({
                "success": True,
                "template": template_name,
                "data": agg.to_dict('records'),
                "columns": agg.columns.tolist(),
                "row_count": len(agg)
            })
        elif template_name == "top_performers":
            df = load_cleaned_df()
            # Simuleer performance score: PTS + 0.7*AST + 0.7*TRB + 1.2*STL + 1.2*BLK - 0.7*TOV
            df = df.dropna(subset=['PTS', 'AST', 'TRB', 'STL', 'BLK', 'TOV'])
            df['PerformanceScore'] = (
                df['PTS'] + 0.7*df['AST'] + 0.7*df['TRB'] + 1.2*df['STL'] + 1.2*df['BLK'] - 0.7*df['TOV']
            )
            top = df.sort_values('PerformanceScore', ascending=False).head(50)
        return jsonify({
            "success": True,
            "template": template_name,
                "data": top.to_dict('records'),
                "columns": top.columns.tolist(),
                "row_count": len(top)
        })
        else:
            return jsonify({"error": "Template not found"}), 404
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

@app.route('/api/ml/predict-next-game')
def ml_predict_next_game():
    """Voorspel voor elke speler het aantal punten in de volgende wedstrijd (rolling average laatste 5 wedstrijden)."""
    try:
        df = load_cleaned_df()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by=['player_name', 'Date'])
        # Rolling average laatste 5 wedstrijden per speler
        df['rolling_avg_pts'] = df.groupby('player_name')['PTS'].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        # Pak de laatste wedstrijd per speler
        last_games = df.groupby('player_name').tail(1).copy()
        result = last_games[['player_name', 'team_code', 'Date', 'PTS', 'rolling_avg_pts']].copy()
        result = pd.DataFrame(result)
        result = result.rename(columns={'PTS': 'last_game_pts', 'rolling_avg_pts': 'predicted_next_pts'})
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        return jsonify({
            'success': True,
            'data': result.to_dict(orient='records'),
            'columns': list(result.columns),
            'row_count': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ml/hot-streaks')
def ml_hot_streaks():
    """Detecteer spelers die in hun laatste 5 wedstrijden >20% boven hun seizoensgemiddelde scoren."""
    try:
        df = load_cleaned_df()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by=['player_name', 'Date'])
        # Seizoensgemiddelde per speler als DataFrame
        season_avg = df.groupby('player_name')['PTS'].mean().to_frame('season_avg')
        # Rolling average laatste 5 wedstrijden
        df['rolling_avg_5'] = df.groupby('player_name')['PTS'].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        # Pak de laatste wedstrijd per speler
        last_games = df.groupby('player_name').tail(1).copy()
        last_games = last_games.merge(season_avg, left_on='player_name', right_index=True)
        last_games['hot_streak'] = last_games['rolling_avg_5'] > 1.2 * last_games['season_avg']
        hot = last_games[last_games['hot_streak']].copy()
        result = hot[['player_name', 'team_code', 'Date', 'rolling_avg_5', 'season_avg']].copy()
        result = pd.DataFrame(result)
        result = result.rename(columns={'rolling_avg_5': 'last5_avg_pts'})
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        return jsonify({
            'success': True,
            'data': result.to_dict(orient='records'),
            'columns': list(result.columns),
            'row_count': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ml/outliers')
def ml_outliers():
    """Geef wedstrijden terug waar een speler >2 standaarddeviaties boven zijn eigen gemiddelde scoorde (uitschieters)."""
    try:
        df = load_cleaned_df()
        # Gemiddelde en std per speler
        stats = df.groupby('player_name')['PTS'].agg(['mean', 'std']).reset_index()
        df = df.merge(stats, on='player_name', how='left')
        df['z_score'] = (df['PTS'] - df['mean']) / df['std']
        outliers = df[df['z_score'] > 2].copy()
        result = outliers[['Date', 'player_name', 'team_code', 'PTS', 'mean', 'std', 'z_score']].copy()
        result = pd.DataFrame(result)
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        return jsonify({
            'success': True,
            'data': result.to_dict(orient='records'),
            'columns': list(result.columns),
            'row_count': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ml/jeremy-lin-games')
def ml_jeremy_lin_games():
    """
    Vind wedstrijden waarin een speler veel beter presteerde dan zijn eigen gemiddelde, op basis van PTS, FG% en eFG%.
    Geeft de top 30 grootste uitschieters terug (Jeremy Lin Games).
    """
    try:
        df = load_cleaned_df()
        # Alleen wedstrijden met voldoende data
        df = df.dropna(subset=['PTS', 'FG%', 'eFG%'])
        # Seizoensgemiddelde en std per speler
        stats = df.groupby('player_name').agg({
            'PTS': ['mean', 'std'],
            'FG%': ['mean', 'std'],
            'eFG%': ['mean', 'std']
        })
        stats.columns = ['PTS_mean', 'PTS_std', 'FG%_mean', 'FG%_std', 'eFG%_mean', 'eFG%_std']
        df = df.merge(stats, left_on='player_name', right_index=True, how='left')
        # Z-scores per stat
        df['z_pts'] = (df['PTS'] - df['PTS_mean']) / df['PTS_std']
        df['z_fg'] = (df['FG%'] - df['FG%_mean']) / df['FG%_std']
        df['z_efg'] = (df['eFG%'] - df['eFG%_mean']) / df['eFG%_std']
        # Combineer tot één Jeremy Lin score (gewogen som, PTS zwaarst)
        df['jeremy_lin_score'] = df['z_pts'] * 1.5 + df['z_fg'] + df['z_efg']
        # Sorteer op score
        top = df.sort_values('jeremy_lin_score', ascending=False).head(30).copy()
        top['Date'] = pd.to_datetime(top['Date']).dt.strftime('%Y-%m-%d')
        # Kolommen voor tabel en grafiek
        if 'opp' in top.columns:
            result = top[['Date', 'player_name', 'team_code', 'opp', 'PTS', 'FG%', 'eFG%', 'jeremy_lin_score']].copy()
        else:
            result = top[['Date', 'player_name', 'team_code', 'PTS', 'FG%', 'eFG%', 'jeremy_lin_score']].copy()
            result['opp'] = None
            result = result[['Date', 'player_name', 'team_code', 'opp', 'PTS', 'FG%', 'eFG%', 'jeremy_lin_score']]
        result = result.rename(columns={'team_code': 'Team Code', 'jeremy_lin_score': 'JeremyLinScore', 'opp': 'OPP'})
        result['JeremyLinScore'] = result['JeremyLinScore'].round(2)
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        # Selecteer top 5 unieke spelers met hoogste JeremyLinScore
        top = df.sort_values('jeremy_lin_score', ascending=False)
        top_players = top['player_name'].unique()[:5]
        top = top[top['player_name'].isin(top_players)].copy()
        # Voor elke speler alleen de hoogste uitschieter
        top = top.sort_values('jeremy_lin_score', ascending=False).drop_duplicates('player_name')
        # Kolommen voor grouped bar chart
        result = top[['player_name', 'team_code', 'PTS', 'PTS_mean', 'FG%', 'FG%_mean', 'eFG%', 'eFG%_mean', 'jeremy_lin_score']].copy()
        result = result.rename(columns={
            'player_name': 'Player Name',
            'team_code': 'Team Code',
            'PTS': 'PTS (Game)',
            'PTS_mean': 'PTS (Season Avg)',
            'FG%': 'FG% (Game)',
            'FG%_mean': 'FG% (Season Avg)',
            'eFG%': 'eFG% (Game)',
            'eFG%_mean': 'eFG% (Season Avg)',
            'jeremy_lin_score': 'JeremyLinScore'
        })
        result['JeremyLinScore'] = result['JeremyLinScore'].round(2)
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        return jsonify({
            'success': True,
            'data': result.to_dict(orient='records'),
            'columns': list(result.columns),
            'row_count': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

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
    try:
        data = request.get_json()
        players = data.get('players', [])
        stat = data.get('stat', 'PTS')
        if not players or not stat:
            return jsonify({"error": "players en stat zijn verplicht"}), 400
        df = load_cleaned_df()
        df = df[df['player_name'].isin(players)]
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='player_name')
        df = df.sort_values(by='Date')
        df['cumulative_stat'] = df.groupby(['player_name', 'team_code'])[stat].cumsum()
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        result = df[['Date', 'player_name', 'team_code', 'cumulative_stat']].copy()
        result = pd.DataFrame(result)
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        return jsonify({
            "success": True,
            "data": result.to_dict(orient='records'),
            "players": result['player_name'].drop_duplicates().tolist(),
            "dates": sorted(result['Date'].drop_duplicates().tolist()),
            "stat": stat
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/overview-totals')
def overview_totals():
    try:
        df = load_cleaned_df()
        grouped = df.groupby(['player_name', 'team_code']).agg({
            'PTS': 'sum',
            'AST': 'sum',
            'TRB': 'sum',
            'STL': 'sum',
            'BLK': 'sum',
            'TOV': 'sum',
            'PF': 'sum',
            'FG': 'sum',
            'FGA': 'sum',
            '3P': 'sum',
            '3PA': 'sum',
            '2P': 'sum',
            '2PA': 'sum',
            'FT': 'sum',
            'FTA': 'sum',
            'ORB': 'sum',
            'DRB': 'sum'
        }).reset_index()
        grouped['FG%'] = grouped.apply(lambda r: r['FG']/r['FGA'] if r['FGA'] > 0 else None, axis=1)
        grouped['3P%'] = grouped.apply(lambda r: r['3P']/r['3PA'] if r['3PA'] > 0 else None, axis=1)
        grouped['2P%'] = grouped.apply(lambda r: r['2P']/r['2PA'] if r['2PA'] > 0 else None, axis=1)
        grouped['FT%'] = grouped.apply(lambda r: r['FT']/r['FTA'] if r['FTA'] > 0 else None, axis=1)
        grouped['eFG%'] = grouped.apply(lambda r: (r['FG'] + 0.5*r['3P'])/r['FGA'] if r['FGA'] > 0 else None, axis=1)
        grouped = grouped.sort_values(by='PTS', ascending=False)
        grouped = grouped.replace({np.nan: None})
        columns = [
            'player_name',
            'Total Points', 'Total Assists', 'Total Rebounds', 'Total Steals', 'Total Blocks',
            'Total Turnovers', 'Total Personal Fouls',
            'FG%', 'Total FG', 'Total FGA', '3P%', 'Total 3P', 'Total 3PA',
            '2P%', 'Total 2P', 'Total 2PA', 'FT%', 'Total FT', 'Total FTA', 'eFG%',
            'Total ORB', 'Total DRB', 'team_code'
        ]
        grouped = grouped.rename(columns={
            'PTS': 'Total Points',
            'AST': 'Total Assists',
            'TRB': 'Total Rebounds',
            'STL': 'Total Steals',
            'BLK': 'Total Blocks',
            'TOV': 'Total Turnovers',
            'PF': 'Total Personal Fouls',
            'FG': 'Total FG',
            'FGA': 'Total FGA',
            '3P': 'Total 3P',
            '3PA': 'Total 3PA',
            '2P': 'Total 2P',
            '2PA': 'Total 2PA',
            'FT': 'Total FT',
            'FTA': 'Total FTA',
            'ORB': 'Total ORB',
            'DRB': 'Total DRB'
        })
        grouped = grouped[columns]
        return jsonify({
            "success": True,
            "data": grouped.to_dict(orient='records'),
            "columns": columns,
            "row_count": len(grouped)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/overview-totals/sorted', methods=['POST'])
def overview_totals_with_sort():
    try:
        data = request.get_json() or {}
        sort_column = data.get('sort_column', 'Total Points')
        sort_direction = data.get('sort_direction', 'DESC')
        df = load_cleaned_df()
        grouped = df.groupby(['player_name', 'team_code']).agg({
            'PTS': 'sum',
            'AST': 'sum',
            'TRB': 'sum',
            'STL': 'sum',
            'BLK': 'sum',
            'TOV': 'sum',
            'PF': 'sum',
            'FG': 'sum',
            'FGA': 'sum',
            '3P': 'sum',
            '3PA': 'sum',
            '2P': 'sum',
            '2PA': 'sum',
            'FT': 'sum',
            'FTA': 'sum',
            'ORB': 'sum',
            'DRB': 'sum'
        }).reset_index()
        grouped['FG%'] = grouped.apply(lambda r: r['FG']/r['FGA'] if r['FGA'] > 0 else None, axis=1)
        grouped['3P%'] = grouped.apply(lambda r: r['3P']/r['3PA'] if r['3PA'] > 0 else None, axis=1)
        grouped['2P%'] = grouped.apply(lambda r: r['2P']/r['2PA'] if r['2PA'] > 0 else None, axis=1)
        grouped['FT%'] = grouped.apply(lambda r: r['FT']/r['FTA'] if r['FTA'] > 0 else None, axis=1)
        grouped['eFG%'] = grouped.apply(lambda r: (r['FG'] + 0.5*r['3P'])/r['FGA'] if r['FGA'] > 0 else None, axis=1)
        grouped = grouped.rename(columns={
            'PTS': 'Total Points',
            'AST': 'Total Assists',
            'TRB': 'Total Rebounds',
            'STL': 'Total Steals',
            'BLK': 'Total Blocks',
            'TOV': 'Total Turnovers',
            'PF': 'Total Personal Fouls',
            'FG': 'Total FG',
            'FGA': 'Total FGA',
            '3P': 'Total 3P',
            '3PA': 'Total 3PA',
            '2P': 'Total 2P',
            '2PA': 'Total 2PA',
            'FT': 'Total FT',
            'FTA': 'Total FTA',
            'ORB': 'Total ORB',
            'DRB': 'Total DRB'
        })
        columns = [
            'player_name',
            'Total Points', 'Total Assists', 'Total Rebounds', 'Total Steals', 'Total Blocks',
            'Total Turnovers', 'Total Personal Fouls',
            'FG%', 'Total FG', 'Total FGA', '3P%', 'Total 3P', 'Total 3PA',
            '2P%', 'Total 2P', 'Total 2PA', 'FT%', 'Total FT', 'Total FTA', 'eFG%',
            'Total ORB', 'Total DRB', 'team_code'
        ]
        grouped = grouped[columns]
        grouped = grouped.replace({np.nan: None})
        grouped = grouped.sort_values(by=sort_column, ascending=(sort_direction == 'asc'))
        return jsonify({
            "success": True,
            "data": grouped.to_dict(orient='records'),
            "columns": columns,
            "row_count": len(grouped),
            "sort_column": sort_column,
            "sort_direction": sort_direction
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cumulative/top10')
def get_cumulative_top10():
    try:
        df = load_cleaned_df()
        df['Date'] = pd.to_datetime(df['Date'])
        top10 = df.groupby('player_name')['PTS'].sum().sort_values(ascending=False).head(10).index.tolist()
        df_top = df[df['player_name'].isin(top10)]
        df_top = df_top.sort_values(by='player_name')
        df_top = df_top.sort_values(by='Date')
        df_top['cumulative_pts'] = df_top.groupby(['player_name', 'team_code'])['PTS'].cumsum()
        df_top['Date'] = df_top['Date'].dt.strftime('%Y-%m-%d')
        result = df_top[['Date', 'player_name', 'team_code', 'cumulative_pts']].copy()
        result = pd.DataFrame(result)
        return jsonify({
            "success": True,
            "data": result.rename(columns={'cumulative_pts': 'cumulative_stat'}).to_dict(orient='records'),
            "players": result['player_name'].drop_duplicates().tolist(),
            "dates": sorted(result['Date'].drop_duplicates().tolist())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-performances-ml')
def top_performances_ml():
    try:
        df = load_cleaned_df()
        df = df.dropna(subset=['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'eFG%'])
        features = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', 'eFG%']
        df['perf_score'] = (
            df['PTS'] +
            1.2 * df['AST'] +
            1.2 * df['TRB'] +
            1.5 * df['STL'] +
            1.5 * df['BLK'] -
            1.0 * df['TOV']
        ) * (df['eFG%'] + 0.5)
        top_games = df.sort_values(by='perf_score', ascending=False).head(50).copy()
        top_games['Date'] = pd.to_datetime(top_games['Date']).dt.strftime('%Y-%m-%d')
        result = top_games.copy()
        result = pd.DataFrame(result)
        result = result.replace({np.nan: None, np.inf: None, -np.inf: None})
        # Zet kolomvolgorde netjes
        desired_order = [
            'Date', 'player_name', 'team_code', 'perf_score', 'PTS', 'TRB', 'AST', 'BLK', 'STL', 'TOV', 'PF',
            'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', '2P', '2PA', '2P%', 'FT', 'FTA', 'FT%', 'eFG%'
        ]
        cols = [col for col in desired_order if col in result.columns]
        result = result[cols + [c for c in result.columns if c not in cols]]
        # Verwijder ongewenste kolommen
        result = result.drop(columns=['Rk', 'Gcar', 'Gtm', 'Unnamed_5', 'GS', 'MP', 'ORB', 'DRB', 'GmSc', 'PlusMinus', 'player_id'], errors='ignore')
        return jsonify({
            'success': True,
            'data': result.to_dict(orient='records'),
            'columns': list(result.columns),
            'row_count': len(result)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/predict/next10games')
def predict_next10games():
    """Voorspel voor elke speler de stats voor de komende 10 wedstrijden van het volgende seizoen (AI/ML-style)."""
    try:
        df = load_cleaned_df()
        stats = ['PTS', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'FG%', '3P%', 'FT%']
        players = df['player_name'].unique()
        predictions = []
        for player in players:
            player_df = df[df['player_name'] == player]
            team = player_df['team_code'].iloc[-1] if not player_df.empty else None
            pred_rows = []
            for i in range(1, 11):
                pred = {'player_name': player, 'team_code': team, 'game': i}
                for stat in stats:
                    mean = player_df[stat].mean()
                    std = player_df[stat].std() if player_df[stat].std() > 0 else 1
                    # Simuleer AI: random normaal rond mean, min 0
                    value = np.random.normal(mean, std)
                    if stat.endswith('%'):
                        value = max(0, min(1, value))
                    else:
                        value = max(0, value)
                    pred[stat] = round(float(value), 2)
                pred_rows.append(pred)
            predictions.append({'player_name': player, 'team_code': team, 'predictions': pred_rows})
        return jsonify({
            'success': True,
            'players': players.tolist(),
            'data': predictions,
            'columns': ['player_name', 'team_code', 'game'] + stats,
            'row_count': len(predictions)
        })
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

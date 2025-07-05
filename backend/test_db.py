import pyodbc
import pandas as pd

# SQL Server configuratie - gebruik dezelfde instellingen als server.js
DB_CONFIG = {
    'driver': 'ODBC Driver 17 for SQL Server',
    'server': 'localhost',
    'port': 50810,
    'database': 'nba',
    'uid': 'nbaUser',
    'pwd': 'test123',
    'trusted_connection': 'no',
    'trust_server_certificate': 'yes',
    'enable_arith_abort': 'yes'
}

def test_connection():
    try:
        # Probeer eerst met poort
        conn_str = (
            f"DRIVER={{{DB_CONFIG['driver']}}};"
            f"SERVER={DB_CONFIG['server']};"
            f"PORT={DB_CONFIG['port']};"
            f"DATABASE={DB_CONFIG['database']};"
            f"UID={DB_CONFIG['uid']};"
            f"PWD={DB_CONFIG['pwd']};"
            f"TrustServerCertificate={DB_CONFIG['trust_server_certificate']};"
            f"Encrypt=no;"
        )
        print("Trying connection with port:", conn_str)
        
        conn = pyodbc.connect(conn_str)
        print("✅ Database connection successful with port!")
        
        # Test query
        query = "SELECT TOP 5 * FROM dbo.nbaPlayerTotals"
        df = pd.read_sql(query, conn)
        print("✅ Query successful!")
        print("Data shape:", df.shape)
        print("Columns:", df.columns.tolist())
        print("First row:", df.iloc[0].to_dict())
        
        conn.close()
        return True
        
    except Exception as e:
        print("❌ Connection with port failed:", str(e))
        
        # Probeer zonder poort (named instance)
        try:
            conn_str = (
                f"DRIVER={{{DB_CONFIG['driver']}}};"
                f"SERVER={DB_CONFIG['server']}\\MOCKCRM;"
                f"DATABASE={DB_CONFIG['database']};"
                f"UID={DB_CONFIG['uid']};"
                f"PWD={DB_CONFIG['pwd']};"
                f"TrustServerCertificate={DB_CONFIG['trust_server_certificate']};"
                f"Encrypt=no;"
            )
            print("Trying connection with named instance:", conn_str)
            
            conn = pyodbc.connect(conn_str)
            print("✅ Database connection successful with named instance!")
            
            # Test query
            query = "SELECT TOP 5 * FROM dbo.nbaPlayerTotals"
            df = pd.read_sql(query, conn)
            print("✅ Query successful!")
            print("Data shape:", df.shape)
            print("Columns:", df.columns.tolist())
            print("First row:", df.iloc[0].to_dict())
            
            conn.close()
            return True
            
        except Exception as e2:
            print("❌ Connection with named instance also failed:", str(e2))
            return False

if __name__ == "__main__":
    test_connection() 
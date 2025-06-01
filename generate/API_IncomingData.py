import requests
import pyodbc

# API ophalen
response = requests.get("https://api.mockaroo.com/api/generate.json?key=eb339fd0&schema=API_IncomingData&count=100")
if response.status_code != 200:
    raise Exception(f"Fout bij ophalen API: {response.status_code}")

data = response.json()

# Verbinding met SQL Server 2022
conn = pyodbc.connect(
    "Driver={SQL Server};"
    "Server=localhost\\MOCKCRM;"
    "Database=CRM_Demo;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

# Itereer over response en insert in tabel ApiCustomers
for klant in data:
    klant_id = klant["customerId"]
    naam = klant["firstName"]
    email = klant["lastName"]
    stad = klant["email"]	

    cursor.execute("""
        INSERT INTO dbo.ApiCustomers (id, name, email, city)
        VALUES (?, ?, ?, ?)
    """, klant_id, naam, email, stad)

conn.commit()
conn.close()

print(f"{response.text}")
print("✔️ API-data succesvol geladen in SQL Server.")

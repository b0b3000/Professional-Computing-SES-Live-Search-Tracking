import pyodbc

# Define connection parameters
server = 'cits3200server.database.windows.net'
database = 'cits3200DB'
username = 'cits3200group4'
password = 'meshtastic2024!' #CHANGE THIS SO IT IS STORED IN KEY VAULT AS SOON AS JIM GIVES ME ACCESS

connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

try:
    with pyodbc.connect(connection_string, timeout=5) as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE employees (id INT PRIMARY KEY,name VARCHAR(100),age INT);")
        print("Connection successful!")

except Exception as e:
    print(f"Error: {e}")

import json
import pyodbc
import get_key

TIMEOUT = 30

def get_database_url():
    
    '''
        NOTE: For local testing using the Azure database, you will need to install the required ODBC Driver (As below)
        This will not be an issue when we are hosting on Azure as Azure already comeS with default drivers to use.    
    '''
    
    server = 'cits3200server.database.windows.net'
    database = 'cits3200DB'
    username = 'cits3200group4'
    password = get_key.get_db_password()
    connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    return connection_string


# Function to connect to database
def connect_database():
    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()
            print("Connection successful!")
            return cursor

    except Exception as e:
        print(f"Error: {e}")
        return

def upload_search_data(session):
    
    base_stations = session["gps_data"].keys()
    
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()
            
            for base_station in base_stations:
                
                session_id = session["session_id"]
                start_time = session["start_time"]
                end_time = session["end_time"]
                #gpx_data = session["gpx_data"] Temporary
                gps_JSON = session["gps_data"][base_station]
                gpx_data = session["gpx_data"][base_station]
                search_date = session["search_date"]
                
                # Decode gps_JSON from bytes, then convert to JSON string. Ensures legal storage in Database
                decoded_data = gps_JSON.decode('utf-8').replace("'", '"')
                gps_JSON_string = json.dumps(json.loads(decoded_data)) 
                
                
                query = """
                    INSERT INTO search_history (session_id, base_station, start_time, end_time, gpx_data, search_date, gps_JSON) 
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """
                
                cursor.execute(query, (session_id, base_station, start_time, end_time, gpx_data, search_date, gps_JSON_string))
                conn.commit()
            
            print("Upload successful")

    except Exception as e:
        print(f"Error: {e}")
        return
    
# This is called when we render our page
def get_unique_base_stations():
    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

            # Query to fetch unique base station names from the database
            query = "SELECT DISTINCT base_station FROM search_history"
            cursor.execute(query)
            
            # Fetch all the unique base stations
            base_stations = [row[0] for row in cursor.fetchall()]

        return base_stations

    except Exception as e:
        print(f"Error in get_unique_base_stations: {e}")
        return []

def get_historical_searches(start_date=None, end_date=None, base_stations=None):
    
    '''
    Called when a user wants to select a historical search. It queries the database with the filters
    start_date, end_date and base_stations, and returns a list of tuples of the columns that were retrieved from the database
    '''
    
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()


        # SQL query to filter searches based on date or base station
        query = "SELECT session_id, base_station, start_time, end_time, gpx_data, gps_JSON FROM search_history WHERE 1=1"
        
        # Add conditions for date filtering
        params = []
        if start_date:
            query += " AND search_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND search_date <= ?"
            params.append(end_date)
        
        # Add condition for filtering multiple base stations
        if base_stations:
            placeholders = ','.join('?' for _ in base_stations)
            query += f" AND base_station IN ({placeholders})"
            params.extend(base_stations)
    
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
    
    except Exception as e:
        print(" ----- ERROR IN get_historical_searches ----\n")
        print(f"Error: {e}")
        return

    return results

# Temporary function for testing purposes
def create_colums_in_table(col_name, data_type):
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()
            
            
            print("Here", flush=True)
            # Testing, Creating another column in table
            alter_table_query = f"""ALTER TABLE search_history ADD '{col_name}' '{data_type}';"""
            cursor.execute(alter_table_query)
            conn.commit()

    except Exception as e:
        
        print(f"Error: {e}")
        return
    
#Testing purposes (Uncomment if needed to test)
#if __name__ == "__main__":
#    
#    connect_database()
"""Functions that the web application uses to interact with the Azure database."""

import json
import pyodbc
import get_key

TIMEOUT = 30


def get_database_url():
    """Fetches the database connection URL from static variables set in this function.

    Returns:
        string (str): Azure database connection string.
    """
    
    server = "cits3200server.database.windows.net"
    database = "cits3200DB"
    username = "cits3200group4"
    password = get_key.get_db_password()
    connection_string = f"DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    return connection_string


def connect_database():
    """Connects to the database using the pyodbc driver."""
    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()
            print("Connection to database successful.")
            return cursor

    except Exception as e:
        print(f"An error occured when connecting to the database: {e}")


def upload_search_data(active_search, incomplete=False):
    """Uploads search data to database upon pressing of the 'End Search' button.
    
    Arguments:
    active_search -- A dictionary of start_time, session_id, and all currently selected blob's data.
    incomplete -- ?
    """
    
    base_stations = active_search["gps_data"].keys()

    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

            for base_station in base_stations:
                session_id = active_search["session_id"]
                start_time = active_search["start_time"]
                gps_JSON = active_search["gps_data"][base_station]

                if incomplete:
                    end_time = None
                    gpx_data = None
                    search_date = None

                else:
                    end_time = active_search["end_time"]
                    gpx_data = active_search["gpx_data"][base_station]
                    search_date = active_search["search_date"]
                
                if (type(gps_JSON) == bytes):
                    gps_JSON = gps_JSON.decode("utf-8")
                decoded_data = gps_JSON.replace("'", '"')
                gps_JSON_string = json.dumps(json.loads(decoded_data))    # Conversion to JSON string ensures legal storage in the database.

                query = """
                    INSERT INTO search_history (session_id, base_station, start_time, end_time, gpx_data, search_date, gps_JSON) 
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """
                
                cursor.execute(query, (session_id, base_station, start_time, end_time, gpx_data, search_date, gps_JSON_string))
                conn.commit()
            
            print("Upload successful")

    except Exception as e:
        print(f"An error occured when uploading search data to the database: {e}")
    

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


def get_live_searches(session_id, base_stations):
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

        json_data = {}
        for base_station in base_stations:
            # SQL query to filter searches based on session_id and base station
            query = "SELECT gps_JSON FROM search_history WHERE session_id = CAST(? AS VARCHAR) AND base_station = CAST(? AS VARCHAR)"

            cursor.execute(query, (session_id, base_station))
            json_data[base_station] = cursor.fetchall()[0].gps_JSON
        
        conn.close()
    
    except Exception as e:
        print(" ----- ERROR IN get_live_searches ----\n")
        print(f"Error: {e}")
        return

    return json_data


def get_historical_searches(start_date=None, end_date=None, base_stations=None):
    
    """
    Called when a user wants to select a historical search. It queries the database with the filters
    start_date, end_date and base_stations, and returns a list of tuples of the columns that were retrieved from the database
    """
    
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()


        # SQL query to filter searches based on date or base station
        query = "SELECT session_id, base_station, start_time, end_time, search_date, gps_JSON, gpx_data FROM search_history WHERE 1=1"
        
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
            placeholders = ",".join("?" for _ in base_stations)
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


def get_all_searches():
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

        query = "SELECT session_id, base_station, start_time, end_time, search_date, gps_JSON FROM search_history"
        
        cursor.execute(query)
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
            alter_table_query = f"""ALTER TABLE search_history ADD "{col_name}" "{data_type}";"""
            cursor.execute(alter_table_query)
            conn.commit()

    except Exception as e:
        
        print(f"Error: {e}")
        return
    

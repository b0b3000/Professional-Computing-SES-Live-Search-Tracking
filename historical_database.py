"""This module contains functions that the web app uses to interact with the Azure database."""

import json
import pyodbc
import get_key
import datetime

TIMEOUT = 30
SERVER = 'cits3200server.database.windows.net' # MODIFY THIS WHEN CREATING A NEW SQL DB SERVER
DATABASE = 'cits3200DB' # MODIFY THIS WHEN CREATING A NEW SQL DB
USERNAME = 'cits3200group4' 
PASSWORD = get_key.get_db_password()
DRIVER_VERSION = "ODBC Driver 18 for SQL Server"


def get_database_url():
    """Fetches the database connection URL from static variables set in this function.

    Returns:
        string (str): Azure database connection string.
    """
    server = "cits3200server.database.windows.net"
    database = "cits3200DB"
    username = "cits3200group4"
    password = get_key.get_db_password()
    connection_string = f'DRIVER={DRIVER_VERSION};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'

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
        return None


def upload_search_data(active_search, incomplete=False):
    """Uploads search data to database upon pressing of the 'Fetch Latest Data' or 'End Search' buttons.

    Args:
        active_search (dict): A dictionary of start_time, session_id, and all currently selected blob's data.
        incomplete (bool): If the function is called when end_time, gpx_data, search_date are unavailable.
    """
    base_stations = active_search["gps_data"].keys()

    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

            for base_station in base_stations:
                session_id = active_search["session_id"]
                start_time = active_search["start_time"]
                gps_json = active_search["gps_data"][base_station]

                if incomplete:
                    end_time = None
                    gpx_data = None
                    search_date = None

                else:
                    end_time = active_search["end_time"]
                    gpx_data = active_search["gpx_data"][base_station]
                    search_date = active_search["search_date"]

                # Converts data to JSON string to ensure legal storage in the database.
                if (type(gps_json) == bytes):
                    gps_json = gps_json.decode("utf-8")
                decoded_data = gps_json.replace("'", '"')
                gps_json_string = json.dumps(json.loads(decoded_data))

                # Check if the record already exists
                check_query = """
                    SELECT COUNT(*)
                    FROM search_history
                    WHERE session_id = ? AND base_station = ?
                """
                cursor.execute(check_query, (session_id, base_station))
                exists = cursor.fetchone()[0]

                if exists > 0:
                # Update the existing row
                    update_query = """
                        UPDATE search_history
                        SET start_time = ?, end_time = ?, gpx_data = ?, search_date = ?, gps_JSON = ?
                        WHERE session_id = ? AND base_station = ?
                    """
                    cursor.execute(update_query, (start_time, end_time, gpx_data, search_date, gps_json_string, session_id, base_station))
                else:
                    query = """
                        INSERT INTO search_history (session_id, base_station, start_time, end_time, gpx_data, search_date, gps_JSON)
                        VALUES (?, ?, ?, ?, ?, ?, ?);
                    """
                    cursor.execute(query, (session_id, base_station, start_time, end_time,
                                       gpx_data, search_date, gps_json_string))
                conn.commit()

            print("Upload to database successful.")

    except Exception as e:
        print(f"An error occured when uploading search data to the database: {e}")
        

def get_unique_base_stations():
    """Finds all unique base stations present in the database.

    This is called when the main page is initially loaded.

    Returns:
        list: All unique base stations in database, or an empty list if an error occured.
    """
    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT base_station FROM search_history"
            cursor.execute(query)
            base_stations = [row[0] for row in cursor.fetchall()]

        return base_stations

    except Exception as e:
        print(" ----- ERROR IN get_unqiue_base_stations ----\n")
        print(f"Error: {e}")
        return []


def get_live_searches(session_id, base_stations):
    """Fetches selected searches from the database

    Called when rendering the historical map and when ending a search.

    Args:
        session_id (str): The current Flask session ID.
        base_stations (list): A list of selected base stations.

    Returns:
        dict: JSON data for the selected base stations, pulled from the database.
    """
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
        print(f"An error occured when getting live searches: {e}")
        return {}

    return json_data


def get_historical_searches(start_date=None, end_date=None, base_stations=None):
    """Retrieves historical searches from the database to display on the historical search page.

    Args:
        start_date (str, optional): The start date of the filter.
        end_date (str, optional): The end date of the filter.
        base_stations (list, optional): A list of the selected base stations to filter.

    Returns:
        list: Base stations between the start and end dates, as rows from the database.
    """

    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

        query = "SELECT session_id, base_station, start_time, end_time, search_date, gps_JSON, gpx_data FROM search_history WHERE 1=1"

        params = []
        if start_date:
            query += " AND search_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND search_date <= ?"
            params.append(end_date)

        if base_stations:    # Condition for multiple base stations.
            placeholders = ",".join("?" for _ in base_stations)
            query += f" AND base_station IN ({placeholders})"
            params.extend(base_stations)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

    except Exception as e:
        print(f"An error occured when getting selected historical searches: {e}")
        return None

    return results


def get_all_searches():
    """The same as the above function, but fetches all searches instead."""
    try:

        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

        query = "SELECT session_id, base_station, start_time, end_time, search_date, gps_JSON FROM search_history"

        cursor.execute(query)
        results = cursor.fetchall()

        conn.close()

    except Exception as e:
        print(f"An error occured when getting all historical searches: {e}")
        return None

    return results
  
def get_pings_after_time(session_id, base_station, filter_time):
    """
    Retrieve pings from the database for a specific base station and session after a given time.
    Returns empty list if we encounter errors or if we simply have no pings.
    """
    try:
        with pyodbc.connect(get_database_url(), timeout=TIMEOUT) as conn:
            cursor = conn.cursor()

            # select pings after a specific time for a given session and base station
            query = """
            SELECT gps_JSON 
            FROM search_history 
            WHERE session_id = ? AND base_station = ?
            """
            print(query, session_id, base_station)
            cursor.execute(query, (session_id, base_station))
            result = cursor.fetchone()
            if result:
                gps_data = result[0]
                print(gps_data[-1])
                decoded_data = json.loads(gps_data) if isinstance(gps_data, str) else gps_data
                filter_time = filter_time.strftime("%Y-%m-%dT%H:%M:%S")
                filter_time = datetime.datetime.strptime(filter_time, '%Y-%m-%dT%H:%M:%S')
                broken_out = False
                print(decoded_data[-1])
                for i, ping in enumerate(decoded_data):
                    ping_time = datetime.datetime.strptime(list(ping.values())[0]['time'], '%Y-%m-%dT%H:%M:%S')

                    #print(ping_time)
                    #print(filter_time)
                    #print(type(ping_time))
                    #print(type(filter_time))
                    if ping_time > filter_time:
                        print("REACHED CURRENT POINT")
                        decoded_data = decoded_data[i:]
                        broken_out = True
                        break
                if not broken_out:
                    decoded_data = []
                    
                return decoded_data
            else:
                return []
    except Exception as e:
        print(f"Error in get_pings_after_time: {e}")
        return []
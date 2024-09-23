''' 

    This program creates the table needed to store historical data. 
    Rather than creating a schema through the Azure portal, we are creating one using this program and then connecting and filling in to an exisiting database
    This requires a url to be formed using the Azure database connection details. 
    These variables will either need to be configured on the Azure server or we can do it using a .env file that is loaded in our __init__.py file before we create the app
     
    
    For example this could look like:
    ---------------------------------
    from dotenv import load_dotenv
    import os
    load_dotenv()  # Load environment variables from .env file

    Afterwards, variables can be accessed by doing:
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    
    Otherwise we could make a full url varaible: AZURE_SQL_URL

    
'''

# setup_database.py
'''from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker'''


"""
# Define the base class for SQLAlchemy models
''' this acts as the foundational class that SQLAlchemy works from, it knows that any class that uses this is a table
    stores metadata, allows for table to be easily built
'''
Base = declarative_base()

''' table details for search data'''

class SearchData(Base):
    __tablename__ = 'search_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    '''Session id given by Flask like so:  session_id = datetime.now().strftime('%Y%m%d%H%M%S')'''
    session_id = Column(String, unique=True, nullable=False)
    ''' Time would be translated to a readable time, different to the strftime format above'''
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    containers_active = Column(String)  # Stores a list of containers active during the search
    data_path = Column(String)  # Path where search data was stored
    gpx_file_path = Column(String)  # Path to the GPX file
    '''
"""
# Function to create the database connection string

import pyodbc
import get_key
def get_database_url():
    server = 'cits3200server.database.windows.net'
    database = 'cits3200DB'
    username = 'cits3200group4'
    password = get_key.get_db_password()
    connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    return connection_string

# Function to connect to database
def connect_database():
    try:
        with pyodbc.connect(get_database_url(), timeout=5) as conn:
            cursor = conn.cursor()
            print("Connection successful!")
            
            return cursor

    except Exception as e:
        print(f"Error: {e}")
        return

def upload_search_data(session):
    print(session)
    base_stations = session["gps_data"].keys()
    try:

        with pyodbc.connect(get_database_url(), timeout=5) as conn:
            cursor = conn.cursor()
            

            for base_station in base_stations:
                session_id = session["session_id"]
                start_time = session["start_time"]
                end_time = session["end_time"]
                gpx_data = session["gpx_data"]
                query = f"INSERT INTO search_history (session_id, base_station, start_time, end_time, gpx_data) VALUES ('{session_id}', '{base_station}', '{start_time}', '{end_time}', '{gpx_data}');"
                cursor.execute(query)
                conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        return
    
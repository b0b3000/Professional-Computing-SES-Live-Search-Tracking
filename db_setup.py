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
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

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

# Function to create the database connection string
def get_database_url():
    server = os.getenv('AZURE_SQL_SERVER')
    database = os.getenv('AZURE_SQL_DATABASE')
    username = os.getenv('AZURE_SQL_USERNAME')
    password = os.getenv('AZURE_SQL_PASSWORD')
    driver = 'ODBC Driver 17 for SQL Server'

    return f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"

# Function to create tables
def setup_database():
    
    """ engine object prepares the connection to the database we are using, by giving it the appropriate parameters"""
    engine = create_engine(get_database_url(), echo=True)

    # Create all tables defined in the Base metadata
    Base.metadata.create_all(engine)
    print("Database schema created successfully.")

if __name__ == '__main__':
    setup_database()

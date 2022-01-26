import os
from sqlalchemy import create_engine

def get(table):
    # an Engine, which the Session will use for connection resources
    db_string = os.getenv('DATABASE_URI')
    db = create_engine(db_string)

    # Retrieve relevant data from table (ENGLISH)
    result = db.execute("SELECT phone, firstName, email FROM " + table + " WHERE CURRENT_DATE<cancelDate OR cancelDate IS NULL")
    
    return result
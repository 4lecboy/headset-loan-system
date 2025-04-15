"""
Database configuration and connection utilities
"""
import pymysql
from utils.env_loader import get_env, load_env

# Load environment variables
load_env()

def connect_to_mysql():
    """
    Create and return a connection to the MySQL database
    """
    conn = pymysql.connect(
        host=get_env('DB_HOST'),
        user=get_env('DB_USER', 'root'),
        password=get_env('DB_PASSWORD', ''),
        database=get_env('DB_NAME', 'headsets'),
        autocommit=True
    )
    return conn

def execute_query(query, params=None, fetch_one=False):
    """
    Execute a SQL query with optional parameters
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        fetch_one (bool, optional): Whether to fetch one result or all
        
    Returns:
        list/tuple/None: Query results or None if error
    """
    conn = connect_to_mysql()
    cursor = None
    result = None
    
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if query.strip().upper().startswith(('SELECT', 'SHOW')):
            if fetch_one:
                result = cursor.fetchone()
            else:
                result = cursor.fetchall()
        else:
            conn.commit()
            result = True
            
    except Exception as e:
        print(f"Database error: {e}")
        if not query.strip().upper().startswith(('SELECT', 'SHOW')):
            conn.rollback()
        result = None
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
    return result
import pymysql

def connect_to_mysql():
    """
    Create and return a connection to the MySQL database
    
    Returns:
        pymysql.connections.Connection: Database connection object
    """
    conn = pymysql.connect(
        host='10.42.10.38',  # Server address
        user='root',         # Username
        password='',         # Password
        database='headsets', # Database name
        autocommit=True      # Auto-commit transactions
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
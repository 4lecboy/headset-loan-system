from config.database import connect_to_mysql, execute_query
from datetime import datetime

class LogsModel:
    def get_all_logs(self):
        """
        Get all system logs ordered by most recent first
        
        Returns:
            list: List of log entries
        """
        query = "SELECT AshimaID, Name, Performed, Item, Date FROM tbllogs ORDER BY ID DESC"
        return execute_query(query)
    
    def create_log(self, ashima_id, name, action, item):
        """
        Create a new log entry
        
        Args:
            ashima_id (str): User's Ashima ID
            name (str): User's name
            action (str): Action performed
            item (str): Item affected
            
        Returns:
            bool: True if successful, False otherwise
        """
        current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = """
        INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (ashima_id, name, action, item, current_datetime))
    
    def get_logs_by_date_range(self, start_date, end_date):
        """
        Get logs within a specific date range
        
        Args:
            start_date (str): Start date (YYYY-MM-DD)
            end_date (str): End date (YYYY-MM-DD)
            
        Returns:
            list: List of log entries within date range
        """
        query = """
        SELECT AshimaID, Name, Performed, Item, Date 
        FROM tbllogs 
        WHERE DATE(Date) >= %s AND DATE(Date) <= %s 
        ORDER BY Date DESC
        """
        return execute_query(query, (start_date, end_date))
    
    def get_logs_by_user(self, ashima_id):
        """
        Get logs for a specific user
        
        Args:
            ashima_id (str): User's Ashima ID
            
        Returns:
            list: List of log entries for the user
        """
        query = """
        SELECT AshimaID, Name, Performed, Item, Date 
        FROM tbllogs 
        WHERE AshimaID = %s 
        ORDER BY Date DESC
        """
        return execute_query(query, (ashima_id,))
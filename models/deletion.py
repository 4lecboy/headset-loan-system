from config.database import connect_to_mysql, execute_query
from datetime import datetime

class DeletionModel:
    def fetch_admin_users(self):
        """
        Fetch all admin users
        
        Returns:
            list: List of admin user records
        """
        query = "SELECT AshimaID, Name FROM admin_login"
        return execute_query(query)
    
    def fetch_employees(self):
        """
        Fetch all employees
        
        Returns:
            list: List of employee records
        """
        query = "SELECT AshimaID, FirstName FROM empinfo"
        return execute_query(query)
    
    def fetch_campaigns(self):
        """
        Fetch all campaigns
        
        Returns:
            list: List of campaign records
        """
        query = "SELECT CampaignName, Id FROM tblcampaign"
        return execute_query(query)
    
    def fetch_rooms(self):
        """
        Fetch all rooms
        
        Returns:
            list: List of room records
        """
        query = "SELECT RoomNumber, Id FROM tblroom"
        return execute_query(query)
    
    def fetch_headsets(self):
        """
        Fetch all headsets
        
        Returns:
            list: List of headset records
        """
        query = "SELECT AssetTagID, Description FROM storage_list"
        return execute_query(query)
    
    def delete_row(self, table_name, column_name, row_id):
        """
        Delete a row from a table
        
        Args:
            table_name (str): Name of the table
            column_name (str): Name of the ID column
            row_id (str): ID of the row to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = f"DELETE FROM {table_name} WHERE {column_name} = %s"
        return execute_query(query, (row_id,))
    
    def log_deletion(self, admin_ashima, admin_name, action, item_id, date):
        """
        Log a deletion action
        
        Args:
            admin_ashima (str): Admin's Ashima ID
            admin_name (str): Admin's name
            action (str): Action performed (usually "Deleted")
            item_id (str): ID of deleted item
            date (str): Date and time of deletion
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (admin_ashima, admin_name, action, item_id, date))
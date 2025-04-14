from models.deletion import DeletionModel
from datetime import datetime

class DeletionController:
    def __init__(self, user_name=None, ashima_id=None):
        self.deletion_model = DeletionModel()
        self.user_name = user_name
        self.ashima_id = ashima_id
    
    def fetch_table_data(self):
        """
        Fetch data for all tables to be displayed in deletion interface
        
        Returns:
            Dictionary with table data
        """
        return {
            'userinfo': self.deletion_model.fetch_admin_users(),
            'empinfo': self.deletion_model.fetch_employees(),
            'campaigns': self.deletion_model.fetch_campaigns(),
            'rooms': self.deletion_model.fetch_rooms(),
            'headsets': self.deletion_model.fetch_headsets()
        }
    
    def delete_record(self, table_name, record_id, column_name):
        """
        Delete a record from a specified table
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to delete
            column_name: Name of the ID column
            
        Returns:
            Boolean indicating success
        """
        try:
            # Delete the record
            self.deletion_model.delete_row(table_name, column_name, record_id)
            
            # Log the action
            if self.user_name and self.ashima_id:
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.deletion_model.log_deletion(
                    self.ashima_id, 
                    self.user_name, 
                    "Deleted", 
                    record_id, 
                    current_datetime
                )
            
            return True
        except Exception:
            return False
    
    def search_records(self, search_term):
        """
        Search records across all tables
        
        Args:
            search_term: Term to search for
            
        Returns:
            Dictionary with filtered table data
        """
        if not search_term.strip():
            return self.fetch_table_data()
        
        # Get all records
        all_data = self.fetch_table_data()
        filtered_data = {}
        
        # Filter each table's records
        for table_name, records in all_data.items():
            filtered_records = []
            for record in records:
                if any(search_term.lower() in str(field).lower() for field in record):
                    filtered_records.append(record)
            filtered_data[table_name] = filtered_records
            
        return filtered_data
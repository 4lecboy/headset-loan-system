from models.logs import LogsModel
import csv
from tkinter import filedialog

class LogsController:
    def __init__(self):
        self.logs_model = LogsModel()
    
    def fetch_logs(self):
        """
        Fetch all system logs
        
        Returns:
            List of log entries
        """
        return self.logs_model.get_all_logs()
    
    def search_logs(self, search_term):
        """
        Search logs by keyword
        
        Args:
            search_term: Term to search for
            
        Returns:
            Filtered list of log entries
        """
        all_logs = self.logs_model.get_all_logs()
        
        if not search_term.strip():
            return all_logs
        
        search_term = search_term.lower()
        filtered_logs = []
        
        for log in all_logs:
            if any(search_term in str(field).lower() for field in log):
                filtered_logs.append(log)
                
        return filtered_logs
    
    def add_log_entry(self, ashima_id, name, action, item):
        """
        Add a new log entry
        
        Args:
            ashima_id: User's Ashima ID
            name: User's name
            action: Action performed
            item: Item affected
            
        Returns:
            Boolean indicating success
        """
        try:
            self.logs_model.create_log(ashima_id, name, action, item)
            return True
        except Exception:
            return False
    
    def export_logs_to_csv(self, logs):
        """
        Export logs to CSV
        
        Args:
            logs: List of logs to export
            
        Returns:
            Path to CSV file if successful, None otherwise
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='logs_export',
            title='Save CSV file'
        )
        
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write header row
                writer.writerow(['AshimaID', 'Name', 'Action', 'Item', 'Date'])
                # Write all items to CSV
                for log in logs:
                    writer.writerow(log)
            return file_path
        
        return None
    
    def get_logs_by_date_range(self, start_date, end_date):
        """
        Get logs within a specific date range
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            
        Returns:
            List of logs within date range
        """
        return self.logs_model.get_logs_by_date_range(start_date, end_date)
    
    def get_logs_by_user(self, ashima_id):
        """
        Get logs for a specific user
        
        Args:
            ashima_id: User's Ashima ID
            
        Returns:
            List of logs for the specified user
        """
        return self.logs_model.get_logs_by_user(ashima_id)
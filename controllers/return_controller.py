from models.loan import LoanModel
from models.headset import HeadsetModel
from models.user import UserModel
from datetime import datetime
import csv
from tkinter import filedialog

class ReturnController:
    def __init__(self):
        self.loan_model = LoanModel()
        self.headset_model = HeadsetModel()
        self.user_model = UserModel()
    
    def fetch_loan_records(self):
        """
        Fetch all active loan records
        
        Returns:
            List of loan records
        """
        return self.loan_model.get_active_loans()
    
    def get_issued_returned_counts(self):
        """
        Get counts of issued and available headsets
        
        Returns:
            Tuple (issued_count, available_count)
        """
        return self.headset_model.get_issued_available_counts()
    
    def check_asset_exists(self, asset_tag):
        """
        Check if an asset is currently issued
        
        Args:
            asset_tag: Asset tag to check
            
        Returns:
            Boolean indicating if asset is currently issued
        """
        return self.loan_model.is_asset_issued(asset_tag)
    
    def process_return(self, asset_tag, received_by, borrower_ashima, admin_ashima, admin_name):
        """
        Process a headset return
        
        Args:
            asset_tag: Asset tag being returned
            received_by: Name of person receiving the return
            borrower_ashima: Ashima ID of person who borrowed the headset
            admin_ashima: Admin's Ashima ID for logging
            admin_name: Admin's name for logging
            
        Returns:
            Boolean indicating success
        """
        try:
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Update loan record
            self.loan_model.update_return_record(
                asset_tag=asset_tag,
                received_by=received_by,
                return_date=current_datetime
            )
            
            # Update asset status
            self.headset_model.update_asset_status(asset_tag, available=True)
            
            # Log the action
            self.user_model.log_action(
                admin_ashima, admin_name, 
                f"Returned {borrower_ashima}'s Headset", 
                asset_tag, current_datetime
            )
            
            return True
        except Exception:
            return False
    
    def export_selected_to_csv(self, selected_records):
        """
        Export selected records to CSV file
        
        Args:
            selected_records: List of records to export
            
        Returns:
            Filename if successful, None otherwise
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='exported_data',
            title='Save CSV file'
        )
        
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write header row
                writer.writerow(['Date Issued','AshimaID','Issued To','Campaign',
                               'Room Number','Asset Tag','Issued By', 'Status'])
                # Write selected items to CSV
                for record in selected_records:
                    writer.writerow(record)
            return file_path
        
        return None
    
    def export_all_to_csv(self, all_records):
        """
        Export all records to CSV file
        
        Args:
            all_records: List of all records to export
            
        Returns:
            Filename if successful, None otherwise
        """
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV files', '*.csv')],
            initialfile='exported_data',
            title='Save CSV file'
        )
        
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write header row
                writer.writerow(['Date Issued','AshimaID','Issued To','Campaign',
                               'Room Number','Asset Tag','Issued By', 'Status'])
                # Write all items to CSV
                for record in all_records:
                    writer.writerow(record)
            return file_path
        
        return None
    
    def format_tree_data_for_html(self, data):
        """
        Format tree data for HTML email display
        
        Args:
            data: List of record data
            
        Returns:
            HTML table string
        """
        # Define header WITHOUT "Campaign"
        header = ["Date Issued", "AshimaID", "Issued To", "Room Number", 
                "Asset Tags", "Issued By", "Status"]

        # Create HTML table
        html_table = '<table border="1" cellspacing="0" cellpadding="5">'
        
        # Add header row
        html_table += '<tr>' + ''.join(f'<th>{col}</th>' for col in header) + '</tr>'
        
        # Add data rows, SKIPPING index 3 (Campaign)
        for row in data:
            html_table += '<tr>'
            for i, item in enumerate(row):
                if i == 3:  # Skip Campaign column
                    continue
                html_table += f'<td>{item}</td>'
            html_table += '</tr>'
        
        html_table += '</table>'
        return html_table
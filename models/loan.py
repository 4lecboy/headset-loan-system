from config.database import connect_to_mysql, execute_query
from datetime import datetime

class LoanModel:
    def create_loan_record(self, date_issued, ashima_id, name, campaign, room_number, asset_tag, issued_by):
        """
        Create a new loan record
        
        Args:
            date_issued (str): Date issued
            ashima_id (str): Employee's Ashima ID
            name (str): Employee's full name
            campaign (str): Campaign name
            room_number (str): Room number
            asset_tag (str): Asset tag ID
            issued_by (str): Name of issuer
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        INSERT INTO SentRecords 
        (DateIssued, AshimaID, Name, Campaign, RoomNumber, AssetTag, IssuedBy, Status) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, 'Issued')
        """
        params = (date_issued, ashima_id, name, campaign, room_number, asset_tag, issued_by)
        return execute_query(query, params)
    
    def get_active_loans(self):
        """
        Get all active loans (status = 'Issued')
        
        Returns:
            list: List of active loan records
        """
        query = """
        SELECT DateIssued, AshimaID, Name, Campaign, RoomNumber, AssetTag, IssuedBy, Status 
        FROM sentrecords 
        WHERE Status = 'Issued' 
        ORDER BY ID DESC
        """
        return execute_query(query)
    
    def is_asset_issued(self, asset_tag):
        """
        Check if an asset is currently issued
        
        Args:
            asset_tag (str): Asset tag to check
            
        Returns:
            bool: True if issued, False otherwise
        """
        query = "SELECT COUNT(*) FROM sentrecords WHERE AssetTag = %s AND Status = 'Issued'"
        result = execute_query(query, (asset_tag,), fetch_one=True)
        return result[0] > 0 if result else False
    
    def update_return_record(self, asset_tag, received_by, return_date=None):
        """
        Update a record when an asset is returned
        
        Args:
            asset_tag (str): Asset tag being returned
            received_by (str): Name of person receiving the return
            return_date (str, optional): Date of return
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not return_date:
            return_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
        query = """
        UPDATE SentRecords 
        SET Status = 'Returned', RecievedBy = %s, ReturnedDate = %s 
        WHERE AssetTag = %s AND Status = 'Issued'
        """
        return execute_query(query, (received_by, return_date, asset_tag))
    
    def count_issued_items(self, name):
        """
        Count the number of items issued to a specific person
        
        Args:
            name (str): Person's name
            
        Returns:
            int: Count of issued items
        """
        query = "SELECT COUNT(*) FROM SentRecords WHERE Name = %s AND Status = 'Issued'"
        result = execute_query(query, (name,), fetch_one=True)
        return result[0] if result else 0
    
    def get_campaigns(self):
        """
        Get list of all campaigns
        
        Returns:
            list: List of campaign names
        """
        query = "SELECT CampaignName FROM tblcampaign"
        records = execute_query(query)
        return [record[0] for record in records] if records else []
    
    def get_rooms(self):
        """
        Get list of all rooms
        
        Returns:
            list: List of room numbers
        """
        query = "SELECT RoomNumber FROM tblroom"
        records = execute_query(query)
        return [record[0] for record in records] if records else []
    
    def add_campaign(self, campaign_name):
        """
        Add a new campaign
        
        Args:
            campaign_name (str): Name of campaign
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "INSERT INTO tblcampaign (CampaignName) VALUES (%s)"
        return execute_query(query, (campaign_name,))
    
    def add_room(self, room_number):
        """
        Add a new room
        
        Args:
            room_number (str): Room number
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "INSERT INTO tblroom (RoomNumber) VALUES (%s)"
        return execute_query(query, (room_number,))
    
    def check_campaign_exists(self, campaign_name):
        """
        Check if a campaign already exists
        
        Args:
            campaign_name (str): Campaign name to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM tblcampaign WHERE CampaignName = %s"
        result = execute_query(query, (campaign_name,), fetch_one=True)
        return result[0] > 0 if result else False
    
    def check_room_exists(self, room_number):
        """
        Check if a room already exists
        
        Args:
            room_number (str): Room number to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM tblroom WHERE RoomNumber = %s"
        result = execute_query(query, (room_number,), fetch_one=True)
        return result[0] > 0 if result else False
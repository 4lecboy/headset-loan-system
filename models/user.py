from config.database import connect_to_mysql, execute_query
from datetime import datetime

class UserModel:
    def check_credentials(self, ashima_id, password):
        """
        Check user login credentials
        
        Args:
            ashima_id (str): User's Ashima ID
            password (str): User's password
            
        Returns:
            tuple: User information if valid, None otherwise
        """
        query = "SELECT * FROM admin_login WHERE AshimaID = %s AND PASSWORD = %s"
        return execute_query(query, (ashima_id, password), fetch_one=True)
    
    def get_user_name(self, ashima_id):
        """
        Get user's name from Ashima ID
        
        Args:
            ashima_id (str): User's Ashima ID
            
        Returns:
            str: User's name or None if not found
        """
        query = "SELECT Name FROM admin_login WHERE AshimaID = %s"
        result = execute_query(query, (ashima_id,), fetch_one=True)
        return result[0] if result else None
    
    def get_privilege_level(self, ashima_id):
        """
        Get user's privilege level
        
        Args:
            ashima_id (str): User's Ashima ID
            
        Returns:
            int: Privilege level (1, 2, or 3) or 0 if not found
        """
        query = "SELECT Privilege FROM admin_login WHERE AshimaID = %s"
        result = execute_query(query, (ashima_id,), fetch_one=True)
        return result[0] if result else 0
    
    def create_user(self, username, ashima_id, password, privilege=3):
        """
        Create a new user account
        
        Args:
            username (str): User's name
            ashima_id (str): User's Ashima ID
            password (str): User's password
            privilege (int): Privilege level (default: 3)
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        INSERT INTO admin_login (Name, AshimaID, Password, Privilege) 
        VALUES (%s, %s, %s, %s)
        """
        return execute_query(query, (username, ashima_id, password, privilege))
    
    def fetch_employee_info(self, ashima_id):
        """
        Fetch employee information based on Ashima ID
        
        Args:
            ashima_id (str): Employee's Ashima ID
            
        Returns:
            dict: Dictionary with employee info or None if not found
        """
        query = "SELECT FirstName, LastName, Campaign FROM empinfo WHERE AshimaID = %s"
        result = execute_query(query, (ashima_id,), fetch_one=True)
        
        if result:
            return {
                'FirstName': result[0],
                'LastName': result[1],
                'Campaign': result[2]
            }
        return None
    
    def check_ashima_exists(self, ashima_id):
        """
        Check if an Ashima ID exists in the database
        
        Args:
            ashima_id (str): Ashima ID to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM empinfo WHERE AshimaID = %s"
        result = execute_query(query, (ashima_id,), fetch_one=True)
        return result[0] > 0 if result else False
    
    def check_asset_exists(self, asset_tag):
        """
        Check if an asset tag exists in the database
        
        Args:
            asset_tag (str): Asset tag to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM storage_list WHERE AssetTagID = %s"
        result = execute_query(query, (asset_tag,), fetch_one=True)
        return result[0] > 0 if result else False
    
    def insert_employee(self, ashima_id, privilege, first_name, last_name, campaign):
        """
        Insert new employee information
        
        Args:
            ashima_id (str): Employee's Ashima ID
            privilege (int): Employee's privilege level
            first_name (str): Employee's first name
            last_name (str): Employee's last name
            campaign (str): Employee's campaign
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        INSERT INTO empinfo (AshimaID, FirstName, LastName, Campaign, Privilege) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (ashima_id, first_name, last_name, campaign, privilege))
    
    def log_action(self, ashima_id, name, action, item, date):
        """
        Log an action in the system
        
        Args:
            ashima_id (str): User's Ashima ID
            name (str): User's name
            action (str): Action performed
            item (str): Item affected
            date (str): Date and time of action
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = """
        INSERT INTO tbllogs (AshimaID, Name, Performed, Item, Date) 
        VALUES (%s, %s, %s, %s, %s)
        """
        return execute_query(query, (ashima_id, name, action, item, date))
    
    def get_max_allowed_issued(self, ashima_id):
        """
        Get maximum allowed issued items for a user based on privilege
        
        Args:
            ashima_id (str): User's Ashima ID
            
        Returns:
            int: Maximum number of allowed issued items
        """
        query = "SELECT Privilege FROM empinfo WHERE AshimaID = %s"
        result = execute_query(query, (ashima_id,), fetch_one=True)
        
        if result:
            privilege = result[0]
            if privilege == 2:
                return 10  # Supervisors can have up to 10 headsets
            else:
                return 2   # Regular employees can have up to 2 headsets
        else:
            return 2  # Default value if AshimaID is not found
    
    def fetch_empID(self):
        """
        Fetch all employee Ashima IDs
        
        Returns:
            list: List of Ashima IDs
        """
        query = "SELECT AshimaID FROM empinfo"
        records = execute_query(query)
        return [record[0] for record in records] if records else []
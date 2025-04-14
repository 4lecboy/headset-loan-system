from models.user import UserModel
from datetime import datetime

class UserController:
    def __init__(self):
        self.user_model = UserModel()
    
    def check_user_credentials(self, ashima_id, password):
        """
        Verify user credentials
        
        Args:
            ashima_id: User's Ashima ID
            password: User's password
            
        Returns:
            user_info tuple if valid, None otherwise
        """
        return self.user_model.check_credentials(ashima_id, password)
    
    def get_user_name(self, ashima_id):
        """
        Get user's name from Ashima ID
        
        Args:
            ashima_id: User's Ashima ID
            
        Returns:
            User's name or None if not found
        """
        return self.user_model.get_user_name(ashima_id)
    
    def get_user_privilege_level(self, ashima_id):
        """
        Get user's privilege level
        
        Args:
            ashima_id: User's Ashima ID
            
        Returns:
            Privilege level (int) or 0 if not found
        """
        return self.user_model.get_privilege_level(ashima_id)
    
    def create_new_user(self, username, ashima_id, password, privilege=3):
        """
        Create a new user account
        
        Args:
            username: User's name
            ashima_id: User's Ashima ID
            password: User's password
            privilege: User's privilege level (default: 3)
            
        Returns:
            Boolean indicating success
        """
        try:
            self.user_model.create_user(username, ashima_id, password, privilege)
            return True
        except Exception:
            return False
    
    def fetch_emp(self, ashima_id):
        """
        Fetch employee information based on Ashima ID
        
        Args:
            ashima_id: Employee's Ashima ID
            
        Returns:
            Dictionary with employee info or None if not found
        """
        return self.user_model.fetch_employee_info(ashima_id)
    
    def check_ashima_id_exists(self, ashima_id):
        """
        Check if an Ashima ID exists in the database
        
        Args:
            ashima_id: Ashima ID to check
            
        Returns:
            Boolean indicating if the ID exists
        """
        return self.user_model.check_ashima_exists(ashima_id)
    
    def check_asset_id_exists(self, asset_tag):
        """
        Check if an asset tag exists in the database
        
        Args:
            asset_tag: Asset tag to check
            
        Returns:
            Boolean indicating if the asset tag exists
        """
        return self.user_model.check_asset_exists(asset_tag)
    
    def insert_empinfo(self, ashima_id, privilege, first_name, last_name, campaign, admin_ashima=None, admin_name=None):
        """
        Insert new employee information
        
        Args:
            ashima_id: Employee's Ashima ID
            privilege: Employee's privilege level
            first_name: Employee's first name
            last_name: Employee's last name
            campaign: Employee's campaign
            admin_ashima: Admin's Ashima ID for logging
            admin_name: Admin's name for logging
            
        Returns:
            Boolean indicating success
        """
        try:
            self.user_model.insert_employee(ashima_id, privilege, first_name, last_name, campaign)
            
            # Log the action
            if admin_ashima and admin_name:
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.user_model.log_action(
                    admin_ashima, admin_name, "Added Employee", ashima_id, current_datetime
                )
            return True
        except Exception:
            return False
    
    def get_max_allowed_issued(self, ashima_id):
        """
        Get maximum allowed issued items for a user
        
        Args:
            ashima_id: User's Ashima ID
            
        Returns:
            Maximum number of allowed issued items
        """
        return self.user_model.get_max_allowed_issued(ashima_id)
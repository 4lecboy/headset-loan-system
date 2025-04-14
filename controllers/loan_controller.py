from models.loan import LoanModel
from models.user import UserModel
from models.headset import HeadsetModel
from datetime import datetime

class LoanController:
    def __init__(self):
        self.loan_model = LoanModel()
        self.user_model = UserModel()
        self.headset_model = HeadsetModel()
    
    def validate_loan_form(self, date_issued, ashima_id, first_name, last_name, campaign, room, asset_tags, issued_by):
        """
        Validate loan form inputs
        
        Returns:
            Boolean indicating if form is valid
        """
        required_fields = [
            room.strip(),
            issued_by.strip(),
            isinstance(asset_tags, list) and len(asset_tags) > 0 and all(tag.strip() for tag in asset_tags),
            campaign.strip(),
            ashima_id.strip(),
            first_name.strip(),
            last_name.strip()
        ]
        
        return all(required_fields)
    
    def submit_loan(self, date_issued, ashima_id, first_name, last_name, campaign, 
                   room_number, asset_tags, issued_by, admin_ashima=None, admin_name=None):
        """
        Process loan submission with validations
        
        Args:
            date_issued: Date when issued
            ashima_id: Employee's Ashima ID
            first_name: Employee's first name
            last_name: Employee's last name
            campaign: Campaign name
            room_number: Room number
            asset_tags: List of asset tags
            issued_by: Name of person issuing equipment
            admin_ashima: Admin's Ashima ID for logging
            admin_name: Admin's name for logging
            
        Returns:
            Tuple (success: bool, message: str)
        """
        # Validate form input
        if not self.validate_loan_form(date_issued, ashima_id, first_name, last_name, 
                                     campaign, room_number, asset_tags, issued_by):
            return False, "Please fill out all required fields!"
        
        # Create full name
        name = f"{first_name} {last_name}"
        
        # Check if employee exists
        if not self.user_model.check_ashima_exists(ashima_id):
            # If employee doesn't exist, add them to the system
            self.user_model.insert_employee(
                ashima_id=ashima_id,
                first_name=first_name,
                last_name=last_name,
                campaign=campaign,
                privilege=1  # Default privilege
            )
            
            # Log the action
            if admin_ashima and admin_name:
                current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.user_model.log_action(
                    admin_ashima, admin_name, "Added Employee", ashima_id, current_datetime
                )
        
        # Check maximum allowed items
        max_allowed = self.user_model.get_max_allowed_issued(ashima_id)
        current_count = self.loan_model.count_issued_items(name)
        
        if current_count + len(asset_tags) > max_allowed:
            return False, f"Maximum number of issued items ({max_allowed}) reached for {name}!"
        
        # Process each asset tag
        success_count = 0
        failed_tags = []
        
        for asset_tag in asset_tags:
            asset_tag = asset_tag.strip()
            
            # Verify asset exists
            if not self.headset_model.check_asset_exists(asset_tag):
                failed_tags.append(f"{asset_tag} (not found)")
                continue
                
            # Verify asset is available
            if not self.headset_model.is_asset_available(asset_tag):
                failed_tags.append(f"{asset_tag} (already issued)")
                continue
                
            # Issue the asset
            try:
                self.loan_model.create_loan_record(
                    date_issued=date_issued,
                    ashima_id=ashima_id,
                    name=name,
                    campaign=campaign,
                    room_number=room_number,
                    asset_tag=asset_tag,
                    issued_by=issued_by
                )
                
                # Mark headset as loaned
                self.headset_model.update_asset_status(asset_tag, available=False)
                
                # Log the action
                if admin_ashima and admin_name:
                    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.user_model.log_action(
                        admin_ashima, admin_name, "Loaned Headset", asset_tag, current_datetime
                    )
                    
                success_count += 1
                
            except Exception as e:
                failed_tags.append(f"{asset_tag} (error: {str(e)})")
        
        # Prepare result message
        if success_count == len(asset_tags):
            return True, "Loan records added successfully!"
        elif success_count > 0:
            return True, f"Partially successful: {success_count}/{len(asset_tags)} assets loaned. Failed: {', '.join(failed_tags)}"
        else:
            return False, f"Loan failed. Issues: {', '.join(failed_tags)}"
    
    def fetch_campaigns(self):
        """
        Fetch available campaigns
        
        Returns:
            List of campaign names
        """
        return self.loan_model.get_campaigns()
    
    def fetch_rooms(self):
        """
        Fetch available rooms
        
        Returns:
            List of room numbers
        """
        return self.loan_model.get_rooms()
    
    def fetch_asset_tags(self):
        """
        Fetch available asset tags
        
        Returns:
            List of available asset tags
        """
        return self.headset_model.get_available_assets()
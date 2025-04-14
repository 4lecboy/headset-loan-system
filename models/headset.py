from config.database import connect_to_mysql, execute_query

class HeadsetModel:
    def get_available_assets(self):
        """
        Get list of all available asset tags
        
        Returns:
            list: List of available asset tags
        """
        query = "SELECT AssetTagID FROM storage_list WHERE Flag = 1"
        records = execute_query(query)
        return [record[0] for record in records] if records else []
    
    def check_asset_exists(self, asset_tag):
        """
        Check if an asset tag exists in the storage list
        
        Args:
            asset_tag (str): Asset tag to check
            
        Returns:
            bool: True if exists, False otherwise
        """
        query = "SELECT COUNT(*) FROM storage_list WHERE AssetTagID = %s"
        result = execute_query(query, (asset_tag,), fetch_one=True)
        return result[0] > 0 if result else False
    
    def is_asset_available(self, asset_tag):
        """
        Check if an asset is available (Flag = 1)
        
        Args:
            asset_tag (str): Asset tag to check
            
        Returns:
            bool: True if available, False otherwise
        """
        query = "SELECT Flag FROM storage_list WHERE AssetTagID = %s"
        result = execute_query(query, (asset_tag,), fetch_one=True)
        return result[0] == 1 if result else False
    
    def update_asset_status(self, asset_tag, available=True):
        """
        Update asset status (Flag value)
        
        Args:
            asset_tag (str): Asset tag to update
            available (bool): Whether asset is available
            
        Returns:
            bool: True if successful, False otherwise
        """
        flag_value = 1 if available else 0
        query = "UPDATE storage_list SET Flag = %s WHERE AssetTagID = %s"
        return execute_query(query, (flag_value, asset_tag))
    
    def add_headset(self, asset_tag, description):
        """
        Add a new headset to inventory
        
        Args:
            asset_tag (str): Asset tag ID
            description (str): Headset description
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "INSERT INTO storage_list (AssetTagID, Description, Flag) VALUES (%s, %s, 1)"
        return execute_query(query, (asset_tag, description))
    
    def delete_headset(self, asset_tag):
        """
        Delete a headset from inventory
        
        Args:
            asset_tag (str): Asset tag ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        query = "DELETE FROM storage_list WHERE AssetTagID = %s"
        return execute_query(query, (asset_tag,))
    
    def get_headset_details(self, asset_tag):
        """
        Get details for a specific headset
        
        Args:
            asset_tag (str): Asset tag ID
            
        Returns:
            tuple: Headset details or None if not found
        """
        query = "SELECT * FROM storage_list WHERE AssetTagID = %s"
        return execute_query(query, (asset_tag,), fetch_one=True)
    
    def get_issued_available_counts(self):
        """
        Get counts of issued and available headsets
        
        Returns:
            tuple: (issued_count, available_count)
        """
        issued_query = "SELECT COUNT(*) FROM storage_list WHERE Flag = 0"
        available_query = "SELECT COUNT(*) FROM storage_list WHERE Flag = 1"
        
        issued_result = execute_query(issued_query, fetch_one=True)
        available_result = execute_query(available_query, fetch_one=True)
        
        issued_count = issued_result[0] if issued_result else 0
        available_count = available_result[0] if available_result else 0
        
        return issued_count, available_count
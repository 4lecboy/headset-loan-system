"""
Validation utilities for the Headset Loan System
Provides functions to validate various types of input data
"""

def on_validate(P):
    """
    Validate numeric input with optional hyphen
    Used for Ashima ID validation
    
    Args:
        P: Input string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(P) > 10:
        return False
    if all(char.isdigit() or char == '-' for char in P) or P == "":
        return True
    return False

def on_validatename(P):
    """
    Validate name input (max 15 characters)
    
    Args:
        P: Input string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(P) > 15:
        return False
    return True

def on_validatepass(P):
    """
    Validate password input (max 25 characters)
    
    Args:
        P: Input string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(P) > 25:
        return False
    return True

def on_validateasset(P):
    """
    Validate asset tag input (alphanumeric with optional hyphen)
    
    Args:
        P: Input string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(P) > 15:
        return False
    if all(char.isalnum() or char == '-' for char in P) or P == "":
        return True
    return False

def on_validateroom(P):
    """
    Validate room number input (alphanumeric only)
    
    Args:
        P: Input string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(P) > 20:
        return False
    if all(char.isalnum() for char in P) or P == "":
        return True
    return False

def on_validatecampaign(P):
    """
    Validate campaign name input (alphanumeric only)
    
    Args:
        P: Input string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if len(P) > 15:
        return False
    if all(char.isalnum() for char in P) or P == "":
        return True
    return False

def validate_email(email):
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_date_format(date_str):
    """
    Validate date string format (YYYY-MM-DD)
    
    Args:
        date_str: Date string to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    import re
    from datetime import datetime
    
    # Check format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False
    
    # Check if it's a valid date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_loan_form(date_issued, ashima_id, first_name, last_name, campaign, room, asset_tags, issued_by):
    """
    Validate loan form input fields
    
    Args:
        Various form fields
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = [
        (room, "Room number is required"),
        (issued_by, "Issued by is required"),
        (asset_tags, "Asset tag is required"),
        (campaign, "Campaign is required"),
        (ashima_id, "Ashima ID is required"),
        (first_name, "First name is required"),
        (last_name, "Last name is required")
    ]
    
    for field, message in required_fields:
        if not field or (isinstance(field, str) and not field.strip()):
            return False, message
    
    # Check if campaign and room are not default values
    if campaign == "Select Campaign":
        return False, "Please select a campaign"
    
    if room == "Select Room":
        return False, "Please select a room"
    
    # Validate asset tags if multiple
    if isinstance(asset_tags, str) and ',' in asset_tags:
        tags = [tag.strip() for tag in asset_tags.split(',')]
        if not all(tags):
            return False, "Invalid asset tag format"
    
    return True, ""
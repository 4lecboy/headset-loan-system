"""
Custom exceptions for the Headset Loan System
"""

class HeadsetLoanSystemError(Exception):
    """Base exception for all application-specific errors"""
    pass

class DatabaseConnectionError(HeadsetLoanSystemError):
    """Raised when a database connection cannot be established"""
    pass

class ValidationError(HeadsetLoanSystemError):
    """Raised when data validation fails"""
    def __init__(self, message="Validation failed", field=None):
        self.field = field
        self.message = f"{message}{f' for {field}' if field else ''}"
        super().__init__(self.message)

class AuthenticationError(HeadsetLoanSystemError):
    """Raised when authentication fails"""
    pass

class AssetNotFoundError(HeadsetLoanSystemError):
    """Raised when an asset is not found"""
    def __init__(self, asset_tag=None):
        self.asset_tag = asset_tag
        message = f"Asset not found{f': {asset_tag}' if asset_tag else ''}"
        super().__init__(message)

class AssetAlreadyIssuedError(HeadsetLoanSystemError):
    """Raised when attempting to issue an already issued asset"""
    def __init__(self, asset_tag=None):
        self.asset_tag = asset_tag
        message = f"Asset already issued{f': {asset_tag}' if asset_tag else ''}"
        super().__init__(message)

class MaxLoanLimitExceededError(HeadsetLoanSystemError):
    """Raised when a user has reached their maximum loan limit"""
    def __init__(self, user_name=None, limit=None):
        self.user_name = user_name
        self.limit = limit
        message = f"Maximum loan limit exceeded"
        if user_name:
            message += f" for {user_name}"
        if limit:
            message += f" (limit: {limit})"
        super().__init__(message)

class EmailSendingError(HeadsetLoanSystemError):
    """Raised when email sending fails"""
    pass

class ReportGenerationError(HeadsetLoanSystemError):
    """Raised when report generation fails"""
    pass
from fastapi import HTTPException, status

class CivicPlatformException(Exception):
    """Base exception for the platform"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthenticationError(CivicPlatformException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED)

class AuthorizationError(CivicPlatformException):
    """Raised when user lacks permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN)

class ResourceNotFoundError(CivicPlatformException):
    """Raised when a resource is not found"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, status_code=status.HTTP_404_NOT_FOUND)

class ValidationError(CivicPlatformException):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class DuplicateResourceError(CivicPlatformException):
    """Raised when attempting to create a duplicate resource"""
    def __init__(self, resource: str, field: str):
        message = f"{resource} with this {field} already exists"
        super().__init__(message, status_code=status.HTTP_409_CONFLICT)

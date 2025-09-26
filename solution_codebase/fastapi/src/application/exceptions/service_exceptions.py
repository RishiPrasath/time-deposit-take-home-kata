"""
Service layer exceptions
"""

class ServiceException(Exception):
    """Base exception for service layer errors."""
    pass

class RepositoryException(ServiceException):
    """Exception for repository operation failures."""
    pass

class ValidationException(ServiceException):
    """Exception for data validation failures."""
    pass

class BusinessRuleException(ServiceException):
    """Exception for business rule violations."""
    pass
# Base
class NotFoundError(Exception):
    """Base exception for when a resource is not found"""
    def __init__(self, resource: str, identifier: str | int):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id '{identifier}' not found")

class AlreadyExistsError(Exception):
    """Base exception for when a resource already exists"""
    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with identifier '{identifier}' already exists")

class UnauthorizedError(Exception):
    """Base exception for authentication/authorization failures"""
    pass

class ForbiddenError(Exception):
    """Base exception for when access is forbidden"""
    pass

class TokenError(Exception):
    """Base exception for token related errors"""

    def __init__(self, message: str = "Token authentication failed"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


# User
class UserNotFoundError(NotFoundError):
    """Raised when a user is not found"""
    def __init__(self, identifier: str | int):
        super().__init__("User", identifier)

class UserAlreadyExistsError(AlreadyExistsError):
    """Raised when trying to create a user that already exists"""
    def __init__(self, username: str):
        super().__init__("User", username)
        self.username = username


# Auth
class InvalidCredentialsError(UnauthorizedError):
    """Raised when login credentials are invalid"""
    pass

class InactiveUserError(ForbiddenError):
    """Raised when trying to log in with inactive user"""
    pass

class RegistrationNotAllowedError(ForbiddenError):
    """Raised when registration is not allowed"""
    pass


# Token / Security
class TokenExpiredError(TokenError):
    """Raised when token has expired"""

    def __init__(self):
        super().__init__("Token has expired")

class InvalidTokenError(TokenError):
    """Raised when token is invalid"""

    def __init__(self):
        super().__init__("Invalid token")

class MissingTokenError(TokenError):
    """Raised when token is missing"""

    def __init__(self):
        super().__init__("Authorization token is missing")

class InvalidTokenPayloadError(TokenError):
    """Raised when token payload is invalid"""
    def __init__(self, field: str):
        self.field = field
        message = f"Missing required field in token: '{field}'"
        super().__init__(message)

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
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message)

class ForbiddenError(Exception):
    """Base exception for when access is forbidden"""
    def __init__(self, message: str = "Action is forbidden"):
        super().__init__(message)

class TokenError(Exception):
    """Base exception for token related errors"""

    def __init__(self, message: str = "Token authentication failed"):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message

class PermissionDeniedError(Exception):
    """Base exception for permission denied"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message)


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


# Project
class ProjectNotFoundError(NotFoundError):
    """Raised when a project is not found"""
    def __init__(self, identifier: str | int):
        super().__init__("Project", identifier)

class ProjectAlreadyExistsError(AlreadyExistsError):
    """Raised when trying to create a project that already exists"""
    def __init__(self, project_id: str):
        super().__init__("Project", project_id)
        self.project_id = project_id


# Task
class TaskNotFoundError(NotFoundError):
    """Raised when a task is not found"""
    def __init__(self, identifier: str | int):
        super().__init__("Task", identifier)

class TaskAlreadyExistsError(AlreadyExistsError):
    """Raised when trying to create a task that already exists"""
    def __init__(self, task_id: str):
        super().__init__("Task", task_id)
        self.project_id = task_id


# Auth
class InvalidCredentialsError(UnauthorizedError):
    """Raised when login credentials are invalid"""
    def __init__(self):
        super().__init__("Invalid credentials")

class InactiveUserError(ForbiddenError):
    """Raised when trying to log in with inactive user"""
    def __init__(self):
        super().__init__("Inactive user")

class RegistrationNotAllowedError(ForbiddenError):
    """Raised when registration is not allowed"""
    def __init__(self):
        super().__init__("User registration is not allowed")


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

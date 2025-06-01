"""
Custom Exception Classes for the WhatsApp RPG GM application.
"""

class AppException(Exception):
    """Base class for custom application exceptions."""
    def __init__(self, message: str = "An application error occurred."):
        self.message = message
        super().__init__(self.message)

class GameManagerError(AppException):
    """For errors specific to GameManager logic."""
    def __init__(self, message: str = "A Game Manager error occurred."):
        super().__init__(message)

class SessionNotFoundError(GameManagerError):
    """When a game session is not found."""
    def __init__(self, session_id: str = None, message: str = "Game session not found."):
        if session_id:
            message = f"Game session not found: {session_id}"
        super().__init__(message)

class CharacterError(AppException):
    """For errors related to character management."""
    def __init__(self, message: str = "A Character error occurred."):
        super().__init__(message)

class CharacterNotFoundError(CharacterError):
    """When a character is not found."""
    def __init__(self, character_id: str = None, message: str = "Character not found."):
        if character_id:
            message = f"Character not found: {character_id}"
        super().__init__(message)

class AIInteractionError(AppException):
    """For errors during interaction with AI services."""
    def __init__(self, message: str = "An AI interaction error occurred."):
        super().__init__(message)

class ExternalServiceError(AppException):
    """For errors from external services."""
    def __init__(self, service_name: str = "External service", message: str = "An external service error occurred."):
        self.message = f"Error with {service_name}: {message}"
        super().__init__(self.message)

class EvolutionAPIError(ExternalServiceError):
    """Specific to Evolution API errors."""
    def __init__(self, message: str = "An Evolution API error occurred.", status_code: int = None):
        self.status_code = status_code
        full_message = f"Evolution API error: {message}"
        if status_code:
            full_message += f" (Status Code: {status_code})"
        super().__init__(service_name="Evolution API", message=full_message)

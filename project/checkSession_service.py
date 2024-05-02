from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class SessionCheckResponse(BaseModel):
    """
    This model returns the status of session validation, indicating whether the session is still active or has expired.
    """

    session_valid: bool
    message: str


async def checkSession(session_token: str) -> SessionCheckResponse:
    """
    Verifies if the user's session token remains valid for continued access to protected routes. This is crucial for maintaining secure user sessions and activity. Returns session validity status.

    Args:
        session_token (str): The session token that needs to be validated to verify the active session. It is usually passed in the Authorization header as a Bearer token.

    Returns:
        SessionCheckResponse: This model returns the status of session validation, indicating whether the session is still active or has expired.

    Example:
        token = '1'  # Session ID token example
        result = await checkSession(token)
        > SessionCheckResponse(session_valid=True, message='Session is valid.')
    """
    session = await prisma.models.Session.prisma().find_first(
        where={"id": int(session_token)}
    )
    if session:
        current_time = datetime.now()
        if current_time < session.expiresAt:
            return SessionCheckResponse(session_valid=True, message="Session is valid.")
        else:
            return SessionCheckResponse(
                session_valid=False, message="Session has expired."
            )
    else:
        return SessionCheckResponse(session_valid=False, message="Session not found.")

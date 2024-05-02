from datetime import datetime

import prisma
import prisma.models
from pydantic import BaseModel


class LogoutRequest(BaseModel):
    """
    Request model for logging out a user. Requires session identification via headers or authentication method.
    """

    pass


class LogoutResponse(BaseModel):
    """
    Response model for a logout request. Indicates if the logout was successful or if any errors occurred.
    """

    message: str


async def logoutUser(request: LogoutRequest) -> LogoutResponse:
    """
    This route handles session terminations for logged-in users. It invalidates the session to prevent further access to protected resources.
    The expected response confirms the successful logout.

    Args:
        request (LogoutRequest): Request model for logging out a user. Requires session identification via headers or authentication method.

    Returns:
        LogoutResponse: Response model for a logout request. Indicates if the logout was successful or if any errors occurred.

    Example:
        request = LogoutRequest(session_id=123)
        response = await logoutUser(request)
        print(response.message)  # Logout successful.
    """
    session = await prisma.models.Session.prisma().find_unique(
        where={"id": request.session_id}
    )  # TODO(autogpt): Cannot access attribute "session_id" for class "LogoutRequest"
    #     Attribute "session_id" is unknown. reportAttributeAccessIssue
    if not session:
        return LogoutResponse(message="No session found.")
    updated_session = await prisma.models.Session.prisma().update(
        where={"id": request.session_id}, data={"expiresAt": datetime.datetime.utcnow()}
    )  # TODO(autogpt): Cannot access attribute "session_id" for class "LogoutRequest"
    #     Attribute "session_id" is unknown. reportAttributeAccessIssue
    if not updated_session:
        return LogoutResponse(message="Failed to logout.")
    return LogoutResponse(message="Logout successful.")

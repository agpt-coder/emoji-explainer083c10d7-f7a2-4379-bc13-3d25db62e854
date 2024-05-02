from datetime import datetime

import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UserDetails(BaseModel):
    """
    A model representing detailed aspects of the user such as name, email and role.
    """

    id: int
    email: str
    role: prisma.enums.Role


class SessionDetails(BaseModel):
    """
    Information regarding the user's current session.
    """

    sessionId: int
    createdAt: datetime
    expiresAt: datetime


class UserResponse(BaseModel):
    """
    Contains detailed information about the user, including their profile and session data.
    """

    userDetails: UserDetails
    sessionData: SessionDetails


async def getUser(userId: int) -> UserResponse:
    """
    Retrieves a user's information based on the user ID.

    Args:
        userId (int): The unique identifier of the user whose information is being retrieved.

    Returns:
        UserResponse: Contains detailed information about the user, including their profile and session data.

    Raises:
        ValueError: If the user is not found.
    """
    user = await prisma.models.User.prisma().find_unique(
        where={"id": userId},
        include={
            "sessions": {
                "where": {"expiresAt": {"gt": datetime.now()}},
                "take": 1,
                "order": {"createdAt": "desc"},
            }
        },
    )
    if not user:
        raise ValueError("User not found")
    user_details = UserDetails(id=user.id, email=user.email, role=user.role)
    session_details = None
    if user.sessions and len(user.sessions) > 0:
        session = user.sessions[0]
        session_details = SessionDetails(
            sessionId=session.id,
            createdAt=session.createdAt,
            expiresAt=session.expiresAt,
        )
    user_response = UserResponse(userDetails=user_details, sessionData=session_details)
    return user_response

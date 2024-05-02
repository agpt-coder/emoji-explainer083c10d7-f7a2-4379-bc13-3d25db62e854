from typing import Optional

import bcrypt
import prisma
import prisma.models
from pydantic import BaseModel


class LoginResponse(BaseModel):
    """
    This model represents the response given after a login attempt. It can either be a session token if the login was successful or an error message in case of failure.
    """

    token: Optional[str] = None
    error: Optional[str] = None


async def loginUser(email: str, password: str) -> LoginResponse:
    """
    This endpoint manages user logins by verifying user credentials against the stored data. On success, it returns a session token for accessing protected routes. Expected response includes a token or error message.

    Args:
        email (str): The email of the user attempting to log in.
        password (str): The password provided by the user for login verification. This should be handled securely.

    Returns:
        LoginResponse: This model represents the response given after a login attempt. It can either be a session token if the login was successful or an error message in case of failure.
    """
    try:
        user = await prisma.models.User.prisma().find_unique(where={"email": email})
        if user is None:
            return LoginResponse(error="No user found with this email")
        if bcrypt.checkpw(
            password.encode("utf-8"), user.hashedPassword.encode("utf-8")
        ):
            session = await prisma.models.Session.prisma().create(
                data={"userId": user.id}
            )
            return LoginResponse(token=f"session-{session.id}")
        else:
            return LoginResponse(error="Invalid password")
    except Exception as e:
        return LoginResponse(
            error=f"An error occurred during the login process: {str(e)}"
        )

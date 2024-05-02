import bcrypt
import prisma
import prisma.enums
import prisma.models
from pydantic import BaseModel


class UserRegistrationResponse(BaseModel):
    """
    Provides feedback regarding the success or failure of the user registration.
    """

    success: bool
    message: str


async def registerUser(
    username: str, password: str, email: str
) -> UserRegistrationResponse:
    """
    This endpoint allows for the registration of new users. It accepts user details such as username, password, and email, then stores these credentials securely. Expected response includes success status and a message.

    Args:
        username (str): Username for the new user.
        password (str): Password for the new user which will be encrypted before storage.
        email (str): Email address for the new user.

    Returns:
        UserRegistrationResponse: Provides feedback regarding the success or failure of the user registration.
    """
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user:
        return UserRegistrationResponse(
            success=False, message="Email already registered."
        )
    try:
        new_user = await prisma.models.User.prisma().create(
            data={
                "email": email,
                "hashedPassword": hashed_password,
                "role": prisma.enums.Role.User,
            }
        )
        return UserRegistrationResponse(
            success=True, message="User registered successfully."
        )
    except Exception as e:
        return UserRegistrationResponse(
            success=False, message=f"Failed to register user: {str(e)}"
        )

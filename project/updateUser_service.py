import bcrypt
import prisma
import prisma.models
from pydantic import BaseModel


class UpdateUserDetailsResponse(BaseModel):
    """
    Response model indicating the success or failure of the update operation. Includes any messages or statuses relevant to the operation.
    """

    success: bool
    message: str


async def updateUser(
    userId: int, email: str, password: str
) -> UpdateUserDetailsResponse:
    """
    Updates user details such as email or password for the authenticated user. Requires input of updated fields and validates changes against security standards.

    Args:
        userId (int): The unique identifier of the user whose details are to be updated. This should match the authenticated user's ID in the session for security reasons.
        email (str): The new email address to update. Must be unique across all users.
        password (str): The new password. This should be hashed server-side before storing.

    Returns:
        UpdateUserDetailsResponse: Response model indicating the success or failure of the update operation. Includes any messages or statuses relevant to the operation.

    Example usage:
        await updateUser(1, "newemail@example.com", "newSecureP@ssw0rd")
    """
    existing_user = await prisma.models.User.prisma().find_unique(
        where={"email": email}
    )
    if existing_user and existing_user.id != userId:
        return UpdateUserDetailsResponse(
            success=False, message="Email is already in use by another account."
        )
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    try:
        update_result = await prisma.models.User.prisma().update(
            where={"id": userId},
            data={"email": email, "hashedPassword": hashed_password.decode()},
        )
    except Exception as e:
        return UpdateUserDetailsResponse(
            success=False, message=f"Update failed: {str(e)}"
        )
    return UpdateUserDetailsResponse(success=True, message="User updated successfully.")

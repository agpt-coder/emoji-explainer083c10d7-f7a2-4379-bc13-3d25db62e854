import prisma
import prisma.models
from pydantic import BaseModel


class DeleteLogEntryResponse(BaseModel):
    """
    Response model indicating the outcome of a log deletion operation. It primarily confirms the deletion without returning any specific data.
    """

    success: bool
    message: str


async def deleteLog(logId: int) -> DeleteLogEntryResponse:
    """
    Allows deletion of specific log entries. This function is critical for managing log storage and complying with data retention policies. It requires precise identification of the log entry through 'logId', ensuring that only authorized operations are performed.

    Args:
        logId (int): The unique identifier for the log entry to be deleted. This must be determined from the path parameter in the API endpoint.

    Returns:
        DeleteLogEntryResponse: Response model indicating the outcome of a log deletion operation. It primarily confirms the deletion without returning any specific data.

    Example:
        response = await deleteLog(1234)
        > DeleteLogEntryResponse(success=True, message="Log entry successfully deleted.")
    """
    log = await prisma.models.Log.prisma().find_unique(where={"id": logId})
    if log is None:
        return DeleteLogEntryResponse(success=False, message="Log entry not found.")
    try:
        await prisma.models.Log.prisma().delete(where={"id": logId})
        return DeleteLogEntryResponse(
            success=True, message="Log entry successfully deleted."
        )
    except Exception as e:
        return DeleteLogEntryResponse(
            success=False, message=f"Failed to delete log entry: {str(e)}"
        )

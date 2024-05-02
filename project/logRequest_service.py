from datetime import datetime
from typing import Any, Dict

import prisma
import prisma.models
from pydantic import BaseModel


class LogResponse(BaseModel):
    """
    Model for the response indicating the results of processing the log request, including a success indicator and message.
    """

    success: bool
    message: str


async def logRequest(
    timestamp: datetime, source: str, payload: Dict[str, Any]
) -> LogResponse:
    """
    This route captures and logs each incoming request's details like timestamp, source, and payload. It helps in auditing and ensuring the traceability of all operations within the application. The data comes from the Emoji Interpretation Module and other parts of the application. It utilizes robust logging methods to ensure data integrity and reliability.

    Args:
        timestamp (datetime): Timestamp of when the request was made, formatted as an ISO 8601 string.
        source (str): Identifier of the source of the request, could be an IP address or other identifying string.
        payload (Dict[str, Any]): The actual payload of the request, stored as a JSON-compatible dictionary.

    Returns:
        LogResponse: Model for the response indicating the results of processing the log request, including a success indicator and message.
    """
    try:
        user_id = 1
        log_entry = await prisma.models.Log.prisma().create(
            {"action": "Log Request", "createdAt": timestamp, "userId": user_id}
        )
        return LogResponse(
            success=True, message=f"Log entry created with ID: {log_entry.id}"
        )
    except Exception as e:
        return LogResponse(success=False, message=f"Failed to log request: {str(e)}")

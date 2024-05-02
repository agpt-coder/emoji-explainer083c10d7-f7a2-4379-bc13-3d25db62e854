from datetime import datetime
from typing import List, Optional

import prisma
import prisma.models
from pydantic import BaseModel


class LogEntry(BaseModel):
    """
    Detailed model for a single log entry.
    """

    id: int
    action: str
    createdAt: datetime
    userId: int
    details: Optional[str] = None


class LogRetrievalResponse(BaseModel):
    """
    The response model representing a list of log entries matching the provided filter criteria, including detailed information about each log entry.
    """

    logs: List[LogEntry]


async def fetchLogs(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    source: Optional[str],
    operation_type: Optional[str],
) -> LogRetrievalResponse:
    """
    Retrieves the logged data based on provided criteria such as date range, source, or type of operation.
    This endpoint is essential for audits and reviewing the historical operations within the application.
    It supports advanced query capabilities to filter and retrieve relevant log entries efficiently.

    Args:
        start_date (Optional[datetime]): The start date of the range for which logs are to be retrieved. If provided, it should be an ISO 8601 formatted date.
        end_date (Optional[datetime]): The end date of the range for which logs are to be retrieved. If provided, it should be an ISO 8601 formatted date.
        source (Optional[str]): The identifier of the source user whose logs are to be retrieved.
        operation_type (Optional[str]): The type of operation for which logs are to be retrieved, such as 'create', 'update', 'delete', etc.

    Returns:
        LogRetrievalResponse: The response model representing a list of log entries matching the provided filter criteria, including detailed information about each log entry.
    """
    query_filters = {}
    if start_date:
        query_filters["createdAt"] = {"gte": start_date}
    if end_date:
        query_filters.setdefault("createdAt", {})["lte"] = end_date
    if source:
        query_filters["userId"] = int(source)
    if operation_type:
        query_filters["action"] = operation_type
    logs = await prisma.models.Log.prisma().find_many(where=query_filters)
    log_entries = [
        LogEntry(
            id=log.id, action=log.action, createdAt=log.createdAt, userId=log.userId
        )
        for log in logs
    ]
    return LogRetrievalResponse(logs=log_entries)

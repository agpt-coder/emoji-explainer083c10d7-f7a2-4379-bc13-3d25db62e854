import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, Optional

import project.checkSession_service
import project.deleteLog_service
import project.deleteUser_service
import project.explainEmoji_service
import project.fetchLogs_service
import project.getUser_service
import project.interpretEmoji_service
import project.loginUser_service
import project.logoutUser_service
import project.logRequest_service
import project.registerUser_service
import project.updateUser_service
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response
from prisma import Prisma

logger = logging.getLogger(__name__)

db_client = Prisma(auto_register=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_client.connect()
    yield
    await db_client.disconnect()


app = FastAPI(
    title="emoji-explainer",
    lifespan=lifespan,
    description="create a single endpoint that takes in an emoji and explains what it means. Use groq and llama3 for the explaination",
)


@app.delete(
    "/users/{userId}", response_model=project.deleteUser_service.DeleteUserResponse
)
async def api_delete_deleteUser(
    userId: int,
) -> project.deleteUser_service.DeleteUserResponse | Response:
    """
    Allows users to delete their account. This process requires user authentication and will remove all associated data permanently from the database.
    """
    try:
        res = project.deleteUser_service.deleteUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users/logout", response_model=project.logoutUser_service.LogoutResponse)
async def api_get_logoutUser(
    request: project.logoutUser_service.LogoutRequest,
) -> project.logoutUser_service.LogoutResponse | Response:
    """
    This route handles session terminations for logged-in users. It invalidates the session token to prevent further access to protected resources. Expected response confirms successful logout.
    """
    try:
        res = await project.logoutUser_service.logoutUser(request)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.delete(
    "/api/log/{logId}", response_model=project.deleteLog_service.DeleteLogEntryResponse
)
async def api_delete_deleteLog(
    logId: int,
) -> project.deleteLog_service.DeleteLogEntryResponse | Response:
    """
    Allows deletion of specific log entries. This function is critical for managing log storage and complying with data retention policies. It requires precise identification of the log entry through 'logId', ensuring that only authorized operations are performed.
    """
    try:
        res = await project.deleteLog_service.deleteLog(logId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/users/register",
    response_model=project.registerUser_service.UserRegistrationResponse,
)
async def api_post_registerUser(
    username: str, password: str, email: str
) -> project.registerUser_service.UserRegistrationResponse | Response:
    """
    This endpoint allows for the registration of new users. It accepts user details such as username, password, and email, then stores these credentials securely. Expected response includes success status and a message.
    """
    try:
        res = await project.registerUser_service.registerUser(username, password, email)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/api/log/request", response_model=project.logRequest_service.LogResponse)
async def api_post_logRequest(
    timestamp: datetime, source: str, payload: Dict[str, Any]
) -> project.logRequest_service.LogResponse | Response:
    """
    This route captures and logs each incoming request's details like timestamp, source, and payload. It helps in auditing and ensuring the traceability of all operations within the application. The data comes from the Emoji Interpretation Module and other parts of the application. It utilizes robust logging methods to ensure data integrity and reliability.
    """
    try:
        res = await project.logRequest_service.logRequest(timestamp, source, payload)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/emoji/explain", response_model=project.explainEmoji_service.EmojiExplainResponse
)
async def api_post_explainEmoji(
    emoji: str,
) -> project.explainEmoji_service.EmojiExplainResponse | Response:
    """
    Takes an emoji as input and returns its meaning using llama3. The response includes a clear, concise explanation of the emoji utilizing GROQ and Llama3 APIs for data processing.
    """
    try:
        res = await project.explainEmoji_service.explainEmoji(emoji)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get(
    "/users/checkSession",
    response_model=project.checkSession_service.SessionCheckResponse,
)
async def api_get_checkSession(
    session_token: str,
) -> project.checkSession_service.SessionCheckResponse | Response:
    """
    Verifies if the user's session token remains valid for continued access to protected routes. This is crucial for maintaining secure user sessions and activity. Returns session validity status.
    """
    try:
        res = await project.checkSession_service.checkSession(session_token)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post("/users/login", response_model=project.loginUser_service.LoginResponse)
async def api_post_loginUser(
    email: str, password: str
) -> project.loginUser_service.LoginResponse | Response:
    """
    This endpoint manages user logins by verifying user credentials against the stored data. On success, it returns a session token for accessing protected routes. Expected response includes a token or error message.
    """
    try:
        res = await project.loginUser_service.loginUser(email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.post(
    "/api/emoji/interpret",
    response_model=project.interpretEmoji_service.EmojiInterpretationResponse,
)
async def api_post_interpretEmoji(
    emoji: str,
) -> project.interpretEmoji_service.EmojiInterpretationResponse | Response:
    """
    This endpoint receives an emoji character as input and uses the llama3 AI engine to generate a textual explanation of the emoji. It accepts a JSON payload with an 'emoji' field, sends this data to llama3 for processing, and returns the interpreted text as a response. Before processing, it verifies the user's logged status with the User Management Module and logs the request details in the Data Logging Module for auditing.
    """
    try:
        res = await project.interpretEmoji_service.interpretEmoji(emoji)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.put(
    "/users/{userId}",
    response_model=project.updateUser_service.UpdateUserDetailsResponse,
)
async def api_put_updateUser(
    userId: int, email: str, password: str
) -> project.updateUser_service.UpdateUserDetailsResponse | Response:
    """
    Updates user details such as email or password for the authenticated user. Requires input of updated fields and validates changes against security standards.
    """
    try:
        res = await project.updateUser_service.updateUser(userId, email, password)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/api/log", response_model=project.fetchLogs_service.LogRetrievalResponse)
async def api_get_fetchLogs(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    source: Optional[str],
    operation_type: Optional[str],
) -> project.fetchLogs_service.LogRetrievalResponse | Response:
    """
    Retrieves the logged data based on provided criteria such as date range, source, or type of operation. This endpoint is essential for audits and reviewing the historical operations within the application. It supports advanced query capabilities to filter and retrieve relevant log entries efficiently.
    """
    try:
        res = await project.fetchLogs_service.fetchLogs(
            start_date, end_date, source, operation_type
        )
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )


@app.get("/users/{userId}", response_model=project.getUser_service.UserResponse)
async def api_get_getUser(
    userId: int,
) -> project.getUser_service.UserResponse | Response:
    """
    Retrieves a user's information based on the user ID. It requires authentication and returns detailed user profile data.
    """
    try:
        res = await project.getUser_service.getUser(userId)
        return res
    except Exception as e:
        logger.exception("Error processing request")
        res = dict()
        res["error"] = str(e)
        return Response(
            content=jsonable_encoder(res),
            status_code=500,
            media_type="application/json",
        )

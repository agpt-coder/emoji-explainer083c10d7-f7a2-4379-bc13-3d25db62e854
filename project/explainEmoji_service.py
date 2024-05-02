import json

import httpx
import prisma
import prisma.models
from pydantic import BaseModel


class EmojiExplainResponse(BaseModel):
    """
    Provides a descriptive explanation of the input emoji.
    """

    emoji: str
    explanation: str


async def groq_query_to_llama3(query: str) -> dict:
    """
    Sends a GROQ query to the llama3 API and retrieves the explanation for an emoji.

    Args:
        query (str): The GROQ query string to be sent to llama3 API.

    Returns:
        dict: The JSON response containing the text explanation of the emoji.

    Example:
        groq_query_to_llama3('*[_type == "emoji" && emoji == "😊"]')
        > {'explanation': 'A smiling face that expresses happiness and affection.'}
    """
    url = "https://api.llama3.com/groq"
    headers = {"Content-Type": "application/json"}
    body = {"query": query}
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, data=json.dumps(body))
        response_data = resp.json()
        return response_data


async def explainEmoji(emoji: str) -> EmojiExplainResponse:
    """
    Takes an emoji as input and returns its meaning using llama3 and GROQ queries. If not found in database,
    it queries llama3 API using GROQ and then stores the result in the database for future reference.

    Args:
    emoji (str): The emoji character for which the explanation is requested.

    Returns:
    EmojiExplainResponse: Provides a descriptive explanation of the input emoji.

    Example:
        emoji = '😊'
        response = explainEmoji(emoji)
        > EmojiExplainResponse(emoji='😊', explanation='A smiling face that expresses happiness and affection.')
    """
    interpretation = await prisma.models.EmojiInterpretation.prisma().find_unique(
        where={"emoji": emoji}
    )
    if interpretation:
        return EmojiExplainResponse(emoji=emoji, explanation=interpretation.explanation)
    groq_query = f'*[_type == "emoji" && emoji == "{emoji}"]'
    llama3_response = await groq_query_to_llama3(groq_query)
    if "explanation" in llama3_response:
        explanation = llama3_response["explanation"]
        await prisma.models.EmojiInterpretation.prisma().create(
            data={"emoji": emoji, "explanation": explanation, "createdBy": 1}
        )
        return EmojiExplainResponse(emoji=emoji, explanation=explanation)
    return EmojiExplainResponse(emoji=emoji, explanation="No explanation found")

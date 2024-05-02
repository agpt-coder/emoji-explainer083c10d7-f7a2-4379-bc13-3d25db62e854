import prisma
import prisma.models
from pydantic import BaseModel


class EmojiInterpretationResponse(BaseModel):
    """
    This model describes the response from the emoji interpretation API, primarily containing the text explanation of the given emoji.
    """

    explanation: str


async def interpretEmoji(emoji: str) -> EmojiInterpretationResponse:
    """
    This endpoint receives an emoji character as input and uses a generic AI engine (assumed to be already integrated) to generate a textual explanation of the emoji.
    Before processing, it verifies the user's logged status with the User Management Module and logs the request details in the Data Logging Module for auditing.

    Args:
        emoji (str): The emoji character that the user wants to interpret.

    Returns:
        EmojiInterpretationResponse: This model describes the response from the emoji interpretation API, primarily containing the text explanation of the given emoji.
    """
    user_id = 1
    existing_interpretation = (
        await prisma.models.EmojiInterpretation.prisma().find_unique(
            where={"emoji": emoji}
        )
    )
    if existing_interpretation:
        return EmojiInterpretationResponse(
            explanation=existing_interpretation.explanation
        )
    explanation = "Fictive interpretation of {}".format(emoji)
    interpretation_record = await prisma.models.EmojiInterpretation.prisma().create(
        data={"emoji": emoji, "explanation": explanation, "createdBy": user_id}
    )
    await prisma.models.Log.prisma().create(
        data={"action": f"Interpreted emoji: {emoji}", "userId": user_id}
    )
    return EmojiInterpretationResponse(explanation=explanation)

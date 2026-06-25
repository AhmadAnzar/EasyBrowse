import os
import logging
from groq import AsyncGroq
from app.llm.prompts import SUMMARIZER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def summarize_extracted_text(goal: str, extracted_content: str) -> str:
    """
    Summarizes or synthesizes the extracted content to fulfill the user's specific goal.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return "Error: GROQ_API_KEY is not set. Cannot synthesize final summary."
        
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = AsyncGroq(api_key=api_key)
    
    prompt = f"Goal: {goal}\n\nExtracted Content:\n{extracted_content[:15000]}"
    
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": SUMMARIZER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model=model,
            temperature=0.3,
            max_tokens=1000
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("Failed to query Groq Summarizer:")
        return f"Failed to synthesize summary: {str(e)}"

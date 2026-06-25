import os
import json
import logging
from typing import Dict, Any, List
from groq import AsyncGroq
from app.llm.prompts import PLANNER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

async def plan_next_action(
    goal: str,
    current_url: str,
    interactive_elements: List[Dict[str, Any]],
    visible_text: str,
    history: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calls Groq LLM with the current page state, goal, and history,
    requesting a structured JSON response specifying the next tool to run.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY environment variable is not set.")
        return {
            "tool": "finish_task",
            "element_id": None,
            "arguments": {"result": "Error: GROQ_API_KEY is not set."},
            "reasoning": "Missing configuration key.",
            "confidence": 0.0,
            "done": True
        }
        
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = AsyncGroq(api_key=api_key)
    
    # Strip out the CSS selectors and other heavy/redundant keys from elements sent to the LLM to save tokens
    compact_elements = []
    for el in interactive_elements[:45]:
        compact_elements.append({
            "id": el.get("id"),
            "tag": el.get("tag"),
            "role": el.get("role"),
            "label": el.get("label", ""),
            "placeholder": el.get("placeholder", "")
        })

    user_state = {
        "goal": goal,
        "current_url": current_url,
        "interactive_elements": compact_elements,
        "visible_text": visible_text[:1200],  # Truncate text content tightly
        "history": history[-5:]  # Send last 5 steps of history for context
    }
    
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(user_state, indent=2)}
            ],
            model=model,
            response_format={"type": "json_object"},
            temperature=0.1,  # Low temperature for highly deterministic tool usage
            max_tokens=800
        )
        
        raw_response = chat_completion.choices[0].message.content
        logger.info(f"Raw Planner Response: {raw_response}")
        plan = json.loads(raw_response)
        
        # Verify schema elements exist, default if missing
        plan.setdefault("tool", "finish_task")
        plan.setdefault("element_id", None)
        plan.setdefault("arguments", {})
        plan.setdefault("reasoning", "Completed or parsed with defaults.")
        plan.setdefault("confidence", 1.0)
        plan.setdefault("done", plan["tool"] == "finish_task")
        
        return plan
        
    except Exception as e:
        logger.exception("Failed to query Groq Planner:")
        return {
            "tool": "finish_task",
            "element_id": None,
            "arguments": {"result": f"Planner Error: {str(e)}"},
            "reasoning": "Failed to parse or execute Groq request.",
            "confidence": 0.0,
            "done": True
        }

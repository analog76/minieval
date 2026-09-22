from typing import Any, Dict
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def support_agent_task(input_data: Dict[str, Any]) -> str:
    """Task: Support agent implementation targeting gpt-4o-mini."""
    query = input_data.get("query", "")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a customer support agent. Follow these rules:\n"
                    "1. Answer clearly, accurately, and concisely.\n"
                    "2. If addressing refunds, explicitly cite policy 'REF-402'.\n"
                    "3. Do not deflect or provide conversational filler."
                ),
            },
            {"role": "user", "content": query},
        ],
    )
    return response.choices[0].message.content or ""
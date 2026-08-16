import asyncio
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .agentic_loop import process_agent_step
from .tools import tools

load_dotenv()


# Инициализируем клиент, перенаправляя его на серверы Google
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


async def run_agentic_loop(user_query: str, max_iterations: int = 15) -> Dict[str, Any]:
    """Асинхронный конечный автомат для управления агентом."""

    messages: list = [
        {"role": "system", "content": "You are AI assistant in bank"},
        {"role": "user", "content": user_query},
    ]
    for iteration in range(max_iterations):
        raw_response = await client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            tools=tools,  # type: ignore
            tool_choice="auto",
            temperature=0.0,
        )
        llm_response = raw_response.model_dump()
        message = llm_response["choices"][0]["message"]
        messages.append(message)

        if llm_response["choices"][0].get("finish_reason") != "tool_calls":
            return {"status": "success", "answer": message.get("content")}
        tool_calls = message.get("tool_calls", [])

        task = []
        for tool_call in tool_calls:
            tool_name = tool_call["function"]["name"]
            raw_args = json.loads(tool_call["function"]["arguments"])
            task.append(process_agent_step(tool_name, raw_args))
        results = await asyncio.gather(*task, return_exceptions=True)

        for index, tool_call in enumerate(tool_calls):
            result = results[index]
            if isinstance(result, Exception):
                content = f"error: {result}"
            elif not isinstance(result, str):
                content = json.dumps(result, ensure_ascii=False)
            else:
                content = result
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "content": content,
                }
            )
    raise RuntimeError("System Error: Agent exeedec count of iterations.")

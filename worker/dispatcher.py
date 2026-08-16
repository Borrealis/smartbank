import asyncio
import json
from typing import Any, Dict, List

from .agentic_loop import process_agent_step


async def run_agentic_loop(user_query: str, max_iterations: int = 15) -> Dict[str, Any]:
    """Асинхронный конечный автомат для управления агентом."""

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "You are AI assistant in bank"},
        {"role": "user", "content": user_query},
    ]
    for iteration in range(max_iterations):
        llm_responce = {
            "finish_reason": "tool_calls",
            "message": {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_cc1",
                        "function": {
                            "name": "search_compliance_knowledge",
                            "arguments": '{"search_query":"money transfer limits"}',
                        },
                    }
                ],
            },
        }
        messages.append(llm_responce["message"])

        if llm_responce.get("finish_reason") != "tool_calls":
            return {"status": "success", "answer": llm_responce["message"]["content"]}
        tool_calls = llm_responce["message"]["tool_calls"]
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
    raise RuntimeError("System Error: Агент превысил лимит итераций.")

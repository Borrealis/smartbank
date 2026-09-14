import os
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .tools import get_client_tariff_info, search_compliance_knowledge

load_dotenv()

tools = [get_client_tariff_info, search_compliance_knowledge]
tools_by_name = {tool.name: tool for tool in tools}


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
llm_get_tools = llm.bind_tools(tools)


async def run_agentic_loop(user_query: str, max_iterations: int = 15) -> Dict[str, Any]:
    messages: list = [
        SystemMessage(content="You are AI assistant in bank"),
        HumanMessage(content=user_query),
    ]

    for iteration in range(max_iterations):
        response = await llm_get_tools.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            return {"status": "success", "answer": response.content}

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            selected_tool = tools_by_name.get(tool_name)
            if selected_tool is None:
                raise ValueError(f"Unknown tool:{tool_name}")
            tool_output = await selected_tool.ainvoke(tool_call["args"])
            tool_message = ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
            messages.append(tool_message)
    raise RuntimeError("Limit is exceeded")

from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from app.llm import llm

from .tools import get_client_tariff_info, search_compliance_knowledge

tools = [get_client_tariff_info, search_compliance_knowledge]
tools_by_name = {tool.name: tool for tool in tools}

llm_get_tools = llm.bind_tools(tools)


async def run_agentic_loop(user_query: str, max_iterations: int = 15) -> Dict[str, Any]:
    messages: list = [
        SystemMessage(
            content=(
                "You are an AI banking assistant. Use internal tools to search the document "
                "database for bank rules before answering questions that require factual policy "
                "information. When a query includes a client ID and the answer depends on the "
                "client's tariff or status, call get_client_tariff_info. Base your answer only on "
                "results returned by tools; do not invent facts. If the available tools do not "
                "provide enough information, say so clearly. Answer in Russian."
            )
        ),
        HumanMessage(content=user_query),
    ]
    sources = []
    seen_sources = set()
    for iteration in range(max_iterations):
        response = await llm_get_tools.ainvoke(messages)
        messages.append(response)

        if not response.tool_calls:
            rscontent = response.content
            if isinstance(rscontent, str):
                answer = rscontent
            else:
                answer = "\n".join(
                    block["text"] for block in rscontent if block.get("type") == "text"
                )

            return {"status": "success", "answer": answer, "sources": sources}

        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            selected_tool = tools_by_name.get(tool_name)
            if selected_tool is None:
                raise ValueError(f"Unknown tool:{tool_name}")
            tool_output = await selected_tool.ainvoke(tool_call["args"])
            if tool_name == search_compliance_knowledge.name:
                for chunk in tool_output["result"]:
                    source_url = chunk["source_url"]
                    if source_url not in seen_sources:
                        seen_sources.add(source_url)
                        sources.append(source_url)

            tool_message = ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
            messages.append(tool_message)
    raise RuntimeError("Limit is exceeded")

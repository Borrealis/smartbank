import json
from dataclasses import dataclass
from typing import Dict, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, ValidationError

from .schemas import ClientTariffInfo, SearchComplianceTool
from .tools import get_client_tariff_info, search_compliance_knowledge


@dataclass(frozen=True)
class ToolDefinition:
    schema: Type[BaseModel]
    handler: BaseTool


TOOL_REGISTRY: Dict[str, ToolDefinition] = {
    "get_client_tariff_info": ToolDefinition(
        schema=ClientTariffInfo, handler=get_client_tariff_info
    ),
    "search_compliance_knowledge": ToolDefinition(
        schema=SearchComplianceTool, handler=search_compliance_knowledge
    ),
}


async def process_agent_step(tool_name: str, raw_arguments: str):
    tool = TOOL_REGISTRY.get(tool_name)
    if not tool:
        return f"system error: Tool'{tool_name}' not found"

    try:
        parsed_args = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
        validated_args = tool.schema.model_validate(parsed_args)
        kwargs = validated_args.model_dump()
        result = await tool.handler.ainvoke(**kwargs)
        return json.dumps(result, ensure_ascii=False)
    except json.JSONDecodeError:
        return "System Error: Invalid JSON format provided by LLM."
    except ValidationError as e:
        return f"Validation Error in arguments: {e}"
    except Exception as e:
        return f"Execution Error: {e}"

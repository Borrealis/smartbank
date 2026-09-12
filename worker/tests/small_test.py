import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.tools import search_compliance_knowledge


async def main():
    result = await search_compliance_knowledge.ainvoke(
        {"search_query": "когда я могу перести деньги если я пополнил их на свой счет сегодня"}
    )
    print(result)


asyncio.run(main())

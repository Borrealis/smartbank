import asyncio

from app.tools import search_compliance_knowledge


async def main():
    result = await search_compliance_knowledge.ainvoke(
        {
            "search_query": "когда я могу перести деньги если я "
            "пополнил их на свой счет сегодня с обычной карты black "
        }
    )
    print(result)


asyncio.run(main())

import pytest
from app.tools import search_compliance_knowledge

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_search_compliance_knowledge_query_search():
    result = await search_compliance_knowledge.ainvoke(
        {
            "product_category": "Compliance",
            "search_query": "Какие огранчиения дейтсвуют при переводе денег ",
        }
    )
    assert result["result"]
    assert all(chunk["source"] == "Методические рекомендации ЦБ" for chunk in result["result"])

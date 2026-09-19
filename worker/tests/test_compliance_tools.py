import pytest
from app.tools import search_compliance_knowledge

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_search_compliance_knowledge_query_search(monkeypatch: pytest.MonkeyPatch):
    async def fake_embedding(text: str) -> list[float]:
        return [1.0] + [0.0] * 1535

    monkeypatch.setattr("app.tools.get_embedding", fake_embedding)

    result = await search_compliance_knowledge.ainvoke(
        {
            "product_category": "Compliance",
            "search_query": "Какие огранчиения дейтсвуют при переводе денег ",
        }
    )

    assert result["result"]
    assert all(chunk["source"] == "Методические рекомендации ЦБ" for chunk in result["result"])

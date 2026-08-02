from typing import Optional

from pydantic import BaseModel, Field


class SearchComplianceKnowledge(BaseModel):
    search_query: str = Field(description="Поисковой запрос по банковским "
    "продуктам внутри компании")
    product_category: Optional[str] = Field(default=None,
                                         description= "Фильтр по банковскому продукту")

class GetClientTariffInfo(BaseModel):
    client_id: str = Field(description="Содержит уникальный ключ клиента")


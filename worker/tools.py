def get_client_tariff_info(client_id: str) -> str:
    mock_db = {"client_123": "Premium", "client_S934": "Base", "client_ff94": "Diamond"}
    tariff = mock_db.get(client_id, "Standart")

    return f"Current client tariff {tariff}"


def search_compilance_knowledge(search_query: str, product_category: str | None = None) -> str:
    filer_info = "with category filter: '{product_category}'" if product_category else ""
    return f"Found documents for query : '{search_query}'{filer_info}'"

def get_client_tariff_info(client_id: str) -> str:
    mock_db = {"client_123": "Premium", "client_S934": "Base", "client_ff94": "Diamond"}
    tariff = mock_db.get(client_id, "Standart")
    return f"Current client tariff {tariff}"


def search_compliance_knowledge(search_query: str, product_category: str | None = None) -> str:
    filter_info = f" with category filter: '{product_category}'" if product_category else ""
    return f"Found documents for query: '{search_query}'{filter_info}"


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_client_tariff_info",
            "description": "Returns the current tariff plan of a bank client by their ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "client_id": {
                        "type": "string",
                        "description": "Client identifier, for example client_123",
                    }
                },
                "required": ["client_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_compliance_knowledge",
            "description": "Searches the compliance knowledge base for bank policies "
            "(money transfer limits, KYC/AML requirements, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "Search query for the compliance knowledge base",
                    },
                    "product_category": {
                        "type": "string",
                        "description": "Optional product category filter "
                        "(for example, 'transfers', 'loans')",
                    },
                },
                "required": ["search_query"],
            },
        },
    },
]

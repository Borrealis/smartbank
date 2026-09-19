import pytest
from app.tools import ComplianceSearchInput
from pydantic import ValidationError


def test_search_compliance_knowledge():
    with pytest.raises(ValidationError):
        ComplianceSearchInput(product_category="Compliance")  # type: ignore

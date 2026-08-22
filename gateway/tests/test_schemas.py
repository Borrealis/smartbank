import pytest
from app.schemas import AskRequest
from pydantic import ValidationError


def test_asl_request_schemas():
    with pytest.raises(ValidationError):
        AskRequest(query="")

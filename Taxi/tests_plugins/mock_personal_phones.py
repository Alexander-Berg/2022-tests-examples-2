import pytest


@pytest.fixture(autouse=True)
def peronal_phones_default_handlers(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def mock_personal_phones_store(request):
        return {}

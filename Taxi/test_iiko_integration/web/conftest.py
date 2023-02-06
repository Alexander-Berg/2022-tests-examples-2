import pytest


@pytest.fixture(autouse=True)
def mock_api_key_validation(patch):
    @patch('iiko_integration.utils.restaurants._to_api_key_hash')
    def patched_func(secdist, api_key):  # pylint: disable=unused-variable
        return api_key

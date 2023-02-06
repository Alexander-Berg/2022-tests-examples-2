import pytest


@pytest.fixture(autouse=True)
def use_url_mocks(fake_grafana_url, mock_conductor_url):
    pass

# flake8: noqa
import pytest

from test_pricing_modifications_validator.plugins.mock_pricing_admin import (
    mock_pricing_admin,
)


async def test_ping(web_app_client):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''

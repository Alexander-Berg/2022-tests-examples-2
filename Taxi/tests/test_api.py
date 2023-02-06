import json
import logging

import pytest
from mock import patch, MagicMock

from context import settings

logger = logging.getLogger(__name__)


@pytest.fixture
@patch("core.logger.setup_logger", MagicMock(return_value=None))
def api_client():
    from app import init_app
    settings._settings = None
    extra_test_settings = {
        'SQS': {
            'ACCESS_KEY': 'mock',
            'SESSION_TOKEN': 'mock',
            'ENDPOINT': 'mock',
        }
    }
    flask_app = init_app(extra_test_settings)
    flask_app.testing = True
    return flask_app.test_client()


@pytest.mark.slow
def test_ping(api_client):
    result = api_client.get('/ping')
    assert result.status_code == 200
    data = json.loads(result.data)
    assert 'success' in data
    assert data['success']


@pytest.mark.slow
def test_status(api_client):
    result = api_client.get('/status/1')
    assert result.status_code == 404
    data = json.loads(result.data)
    assert 'message' in data
    assert data['message'] == "Process UUID not found"



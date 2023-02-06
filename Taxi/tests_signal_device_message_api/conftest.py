# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from signal_device_message_api_plugins import *  # noqa: F403 F401


@pytest.fixture(name='mock_iam_api', autouse=True)
def _mock_iam_api(mockserver):
    @mockserver.json_handler('/iam-api-cloud/iam/v1/tokens')
    def _get_iam(request):
        return {'iamToken': 'xzxzxz123'}

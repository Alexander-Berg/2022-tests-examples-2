import urllib.parse

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from communication_scenario_plugins import *  # noqa: F403 F401
from testsuite.utils import matching


@pytest.fixture(name='mock_ucommunications')
def _mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push(request):
        callback = request.json['callback']
        assert callback['tvm_name'] == 'communication-scenario'
        url = callback['url']
        assert url.startswith(mockserver.url('/v1/report-event'))
        parse_result = urllib.parse.urlparse(url)
        queries = urllib.parse.parse_qs(parse_result.query)
        assert queries == {
            'event_name': ['delivered'],
            'event_id': [matching.uuid_string],
        }
        return {'payload': {'value': 1234}}

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _sms(_):
        return {
            'message': 'OK',
            'code': '200',
            'content': 'content',
            'message_id': '12f7ccb4dcf14f8ca1fd1da2f994dc99',
            'status': 'sent',
        }

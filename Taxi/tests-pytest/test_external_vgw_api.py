import json

import pytest

from taxi.core import async
from taxi.core import arequests
from taxi.external import vgw_api


@pytest.mark.usefixtures('asyncenv')
@pytest.mark.parametrize(
    [
        'vgw_response_mock', 'expected_forwardings_count',
        'expected_talks_count', 'api_error'
    ],
    [
        ('get_forwardings_empty.json', 0, 0, False),
        ('get_forwardings_one_created_no_talks.json', 1, 0, False),
        ('get_forwardings_one_created_one_talk.json', 1, 1, False),
        ('get_forwardings_one_drafted.json', 0, 0, False),
        ('get_forwardings_drafted_and_created_with_talks.json', 1, 1, False),
        ('', 0, 0, True),
    ]
)
@pytest.inline_callbacks
def test_get_talks_and_forwardings(
        load, patch,
        vgw_response_mock, expected_forwardings_count, expected_talks_count,
        api_error
):
    @patch('taxi.external.vgw_api.get_forwardings_by_order')
    @async.inline_callbacks
    def get_forwardings_by_order(order_id, log_extra=None):
        if api_error:
            raise arequests.HTTPError('')
        yield
        async.return_value(json.loads(load(vgw_response_mock)))

    talks, forwardings = yield vgw_api.get_talks_and_forwardings('')
    assert len(talks) == expected_talks_count
    assert len(forwardings) == expected_forwardings_count

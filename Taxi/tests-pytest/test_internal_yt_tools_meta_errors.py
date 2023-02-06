import datetime

import pytest
import yt.common
import yt.wrapper.errors

from taxi.internal import event_monitor
from taxi.internal.yt_tools.meta import errors as yt_errors


NOW = datetime.datetime(year=2018, month=1, day=30,
                        hour=19, minute=16, second=0)


@pytest.mark.parametrize('yt_exc_cls,error_code,cluster_name,num,expected', [
    (
        yt.wrapper.errors.YtProxyUnavailable,
        None,
        'hahn',
        1,
        {'hahn': {'yt_proxy_unavailable': 1}},
    ),
    (
        yt.wrapper.errors.YtRequestTimedOut,
        3,
        'hahn',
        1,
        {'hahn': {'yt_request_timed_out': 1}},
    ),
    (
        yt.common.YtResponseError,
        None,
        'arnold',
        2,
        {'arnold': {'other_yt_response_error': 2}},
    ),
    (
        yt.common.YtError,
        None,
        'seneca-man',
        3,
        {'seneca-man': {'other_yt_error': 3}},
    ),
])
@pytest.mark.now(NOW.isoformat())
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_report_error(yt_exc_cls, error_code, cluster_name, num, expected):
    class DummyYtError(yt_exc_cls):
        def __init__(self):
            self.error = {'code': error_code or 0}

    for _ in xrange(num):
        yt_exc = DummyYtError()
        yield yt_errors.report_error(yt_exc, cluster_name)
    stats_list = yield event_monitor.yt_replication_errors.get_stats_list(
        NOW, NOW + datetime.timedelta(minutes=1)
    )
    assert len(stats_list) == 1
    assert stats_list[0]['stats'] == expected

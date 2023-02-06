import datetime

import pytest

from taxi_adjust.generated.web.event_logger import plugin as event_logger


NOW = datetime.datetime(
    2018,
    6,
    27,
    15,
    15,
    0,
    tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
)
NOW_GMT_STR = 'Wed, 27 Jun 2018 12:15:00 GMT'


@pytest.mark.now(NOW.isoformat())
def test_log_request(event_logger_logs):
    logs = event_logger_logs

    evlog = event_logger.EventLogger(
        None, {'ident': 'some-ident', 'tskv_format': 'evlog-tskv'}, [None],
    )
    evlog.log_request({'query': 'b'}, aa='bb')
    assert len(logs) == 1
    data = logs[0].split('\t')
    assert len(set(data)) == len(data)
    assert set(data) == {
        'tskv',
        'tskv_format=evlog-tskv',
        'a_query=b',
        'aa=bb',
        'timestamp=%s' % int(NOW.timestamp()),
        'h_date=' + NOW_GMT_STR,
    }

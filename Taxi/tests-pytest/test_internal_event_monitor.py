import datetime

import pytest

from taxi.core import async
from taxi.internal import event_monitor


@pytest.mark.now('2016-09-21T15:00:00+0300')
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_event_monitor(patch):
    @patch('taxi.internal.dbh.event_monitor.Doc.register_event')
    @async.inline_callbacks
    def register_event(doc):
        yield

    test_event = event_monitor.EventType('test')
    yield test_event(foo='bar')
    assert register_event.calls == [
        {
            'args': (
                {
                    'name': 'test',
                    'created': datetime.datetime(2016, 9, 21, 12, 0, 0),
                    'foo': 'bar',
                },
            ),
            'kwargs': {}
        }
    ]

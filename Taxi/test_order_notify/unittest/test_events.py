import pytest

from order_notify.logic import events


@pytest.mark.parametrize(
    'event_key, expected_event',
    [
        pytest.param('handle_driving', events.Events.DRIVING, id='driving'),
        pytest.param('handle_waiting', events.Events.WAITING, id='waiting'),
        pytest.param(
            'handle_transporting',
            events.Events.TRANSPORTING,
            id='transporting',
        ),
    ],
)
async def test_simple(event_key, expected_event):
    event = events.Events(event_key)
    assert event == expected_event


async def test_unknown():
    assert events.Events('handle_unknown').is_unknown

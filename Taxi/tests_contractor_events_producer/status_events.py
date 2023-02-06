import json
from typing import List

OFFLINE_STATUS = 'offline'
BUSY_STATUS = 'busy'
ONLINE_STATUS = 'online'

_EVENT_SEPARATOR = '\n'


def make_raw_event(dbid: str, uuid: str, status: str, timestamp: str):
    event = {
        'park_id': dbid,
        'profile_id': uuid,
        'status': status,
        'updated_ts': timestamp,
        'orders': [],
    }

    return json.dumps(event)


async def post_event(taxi_contractor_events_producer, raw_events: List[str]):
    response = await taxi_contractor_events_producer.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'statuses-events-consumer',
                'data': _EVENT_SEPARATOR.join(raw_events),
                'topic': '/taxi/testing-contractor-statuses-events',
                'cookie': 'my_cookie',
            },
        ),
    )

    assert response.status_code == 200


def make_logbroker_testpoint(testpoint):
    @testpoint('logbroker_commit')
    def logbroker_commit_testpoint(cookie):
        assert cookie == 'my_cookie'

    return logbroker_commit_testpoint

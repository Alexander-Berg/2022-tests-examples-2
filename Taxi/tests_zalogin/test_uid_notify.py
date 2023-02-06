import datetime

import pytest


@pytest.mark.now('2019-08-26T14:00:00Z')
async def test_uid_unbind(taxi_zalogin, stq):
    response = await taxi_zalogin.post(
        'v1/uid-notify',
        params={
            'event_type': 'bind',
            'portal_uid': '11111',
            'phonish_uid': '222222',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert stq.uid_notify.times_called == 1

    stq_call = stq.uid_notify.next_call()
    link = stq_call['kwargs']['log_extra']['_link']
    assert link
    assert isinstance(link, str)

    task_id = stq_call['id']
    assert task_id
    assert isinstance(task_id, str)

    assert stq_call == {
        'queue': 'uid_notify',
        'id': task_id,
        'eta': datetime.datetime(2019, 8, 26, 14, 0),
        'args': [],
        'kwargs': {
            'log_extra': {'_link': link},
            'event_type': 'bind',
            'portal_uid': '11111',
            'phonish_uid': '222222',
            'event_at': '2019-08-26T14:00:00+0000',
        },
    }


async def test_uid_notify_event_at(taxi_zalogin, stq):
    response = await taxi_zalogin.post(
        'v1/uid-notify',
        params={
            'event_type': 'bind',
            'portal_uid': '11111',
            'phonish_uid': '222222',
            'timestamp_event_at': 1594122776,
        },
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert (
        stq.uid_notify.next_call()['kwargs']['event_at']
        == '2020-07-07T14:52:56+0300'
    )

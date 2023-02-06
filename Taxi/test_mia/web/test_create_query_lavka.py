import datetime

import pytest
import pytz


@pytest.mark.config(TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}])
@pytest.mark.now('2019-02-04T14:20:00.0+0200')
async def test_create_query_lavka(taxi_mia_web, now):
    response = await taxi_mia_web.post(
        '/v1/lavka/query', {'completed_only': True, 'exact': {}},
    )
    assert response.status == 200
    content = await response.json()
    assert content['id']
    request_id = content['id']
    assert content['status'] == 'pending'

    response = await taxi_mia_web.get('/v1/lavka/query/' + content['id'], {})
    assert response.status == 200

    content = await response.json()
    state = content['state']

    assert state['id'] == request_id
    assert state['status'] == 'pending'

    created_time = datetime.datetime.fromisoformat(state['created_time'])
    assert created_time.astimezone(pytz.utc).replace(tzinfo=None) == now


@pytest.mark.parametrize(
    'test',
    [
        {  # now < to
            'request': {
                'request_body': {
                    'completed_only': True,
                    'period': {
                        'created': {
                            'from': '2019-02-04T14:20:00.0+0200',
                            'to': '2019-02-06T14:21:45.0+0200',
                        },
                    },
                },
            },
        },
        {  # now < from
            'request': {
                'request_body': {
                    'completed_only': True,
                    'period': {
                        'created': {
                            'from': '2019-02-06T14:20:00.0+0200',
                            'to': '2019-02-06T14:21:45.0+0200',
                        },
                    },
                },
            },
        },
        {  # to < from
            'request': {
                'request_body': {
                    'completed_only': True,
                    'period': {
                        'created': {
                            'from': '2019-02-04T14:19:45.0+0200',
                            'to': '2019-02-04T14:19:00.0+0200',
                        },
                    },
                },
            },
        },
    ],
)
@pytest.mark.now('2019-02-04T14:20:00.0+0200')
async def test_create_query_bad_dates_lavka(taxi_mia_web, now, test):
    response = await taxi_mia_web.post(
        '/v1/lavka/query', test['request']['request_body'],
    )
    content = await response.json()

    assert response.status == 400
    assert content['message'] == 'Period fields are incorrect!'

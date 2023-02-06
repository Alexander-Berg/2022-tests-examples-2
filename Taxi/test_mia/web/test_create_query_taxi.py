import datetime

import pytest
import pytz


@pytest.mark.config(
    TVM_RULES=[{'src': 'mia', 'dst': 'stq-agent'}],
    MIA_FILTER_BY_COUNTRIES_ENABLED=False,
)
@pytest.mark.now('2019-02-04T14:20:00.0+0200')
async def test_create_query_taxi(taxi_mia_web, now):
    response = await taxi_mia_web.post(
        '/v1/taxi/query', {'check_all_candidates': True, 'exact': {}},
    )
    assert response.status == 200
    content = await response.json()
    assert content['id']
    request_id = content['id']
    assert content['status'] == 'pending'

    response = await taxi_mia_web.get('/v1/taxi/query/' + content['id'], {})
    assert response.status == 200

    content = await response.json()
    state = content['state']

    assert state['id'] == request_id
    assert state['status'] == 'pending'

    created_time = datetime.datetime.fromisoformat(state['created_time'])
    assert created_time.astimezone(pytz.utc).replace(tzinfo=None) == now


@pytest.mark.config(MIA_FILTER_BY_COUNTRIES_ENABLED=False)
@pytest.mark.parametrize(
    'test',
    [
        {  # now < to
            'request': {
                'request_body': {
                    'check_all_candidates': True,
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
                    'check_all_candidates': True,
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
                    'check_all_candidates': True,
                    'period': {
                        'created': {
                            'from': '2019-02-04T14:19:45.0+0200',
                            'to': '2019-02-04T14:19:00.0+0200',
                        },
                    },
                },
            },
        },
        {  # now < to
            'request': {
                'request_body': {
                    'check_all_candidates': True,
                    'period': {
                        'request_due': {
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
                    'check_all_candidates': True,
                    'period': {
                        'request_due': {
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
                    'check_all_candidates': True,
                    'period': {
                        'request_due': {
                            'from': '2019-02-04T14:19:45.0+0200',
                            'to': '2019-02-04T14:19:00.0+0200',
                        },
                    },
                },
            },
        },
    ],
)
@pytest.mark.now('2019-02-05T14:20:00.0+0200')
async def test_create_query_bad_dates_taxi(taxi_mia_web, now, test):
    response = await taxi_mia_web.post(
        '/v1/taxi/query', test['request']['request_body'],
    )
    content = await response.json()

    assert response.status == 400
    assert content['message'] == 'Period fields are incorrect!'


@pytest.mark.config(MIA_FILTER_BY_COUNTRIES_ENABLED=False)
@pytest.mark.now('2019-02-05T14:20:00.0+0200')
async def test_empty_query_taxi(taxi_mia_web, now):
    request = {'check_all_candidates': True}

    response = await taxi_mia_web.post('/v1/taxi/query', request)
    content = await response.json()

    assert response.status == 400
    assert content['message'] == 'Request body is empty!'


@pytest.mark.config(MIA_FILTER_BY_COUNTRIES_ENABLED=False)
@pytest.mark.now('2019-07-04T12:20:00.0')
@pytest.mark.parametrize(
    'case',
    [
        {
            'test_input': {
                'request': {
                    'exact': {'masked_pan': '123456***1234'},
                    'period': {
                        'payment': {
                            'from': '2019-04-06T12:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected': {'message': 'Masked PAN is not in acceptable format!'},
        },
        {
            'test_input': {
                'request': {
                    'exact': {'masked_pan': '123456****1234'},
                    'period': {
                        'payment': {
                            'from': '2019-04-04T11:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected': {
                'message': 'Payment search period should be less than 3 days!',
            },
        },
        {
            'test_input': {
                'request': {
                    'exact': {'cost': 12.34},
                    'period': {
                        'payment': {
                            'from': '2019-04-06T12:00:00.0',
                            'to': '2019-04-08T12:00:00.0',
                        },
                    },
                },
            },
            'expected': {
                'message': (
                    'To search by payments data, '
                    'request body must contain payment period and at least '
                    'one of: masked_pan, RRN, approval_code!'
                ),
            },
        },
    ],
)
async def test_taxi_bad_card_request(taxi_mia_web, now, case):
    request = case['test_input']['request']
    request.update({'check_all_candidates': False})
    response = await taxi_mia_web.post('/v1/taxi/query', request)

    assert response.status == 400
    content = await response.json()
    assert content['message'] == case['expected']['message']

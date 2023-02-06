import json

import pytest
import pytz

NOW = '2019-11-18T19:03:08+00:00'


@pytest.mark.parametrize(
    'data,code',
    [
        (
            {
                'park_id': 'park_id_0',
                'order_id': 'order_id_0',
                'user_name': 'John Doe [T777TT 77RUS]',
                'message': 'Order message',
            },
            200,
        ),
        (
            {
                'park_id': 'park_id_0',
                'order_id': 'order_id_0',
                'user_name': 'John Doe [T777TT 77RUS]',
                'message': 'Order message',
                'info': 'Additional info',
            },
            200,
        ),
        (
            {
                'park_id': 'park_id_0',
                'order_id': 'order_id_0',
                'date': '2019-11-18T17:05:07+00:00',
                'user_name': 'John Doe [T777TT 77RUS]',
                'message': 'Order message',
            },
            200,
        ),
        (
            {
                'order_id': 'order_id_0',
                'user_name': 'John Doe [T777TT 77RUS]',
                'message': 'Order message',
            },
            400,
        ),
        (
            {
                'park_id': 'park_id_0',
                'user_name': 'John Doe [T777TT 77RUS]',
                'message': 'Order message',
            },
            400,
        ),
        (
            {
                'park_id': 'park_id_0',
                'order_id': 'order_id_0',
                'message': 'Order message',
            },
            400,
        ),
        (
            {
                'park_id': 'park_id_0',
                'order_id': 'order_id_0',
                'user_name': 'John Doe [T777TT 77RUS]',
            },
            400,
        ),
    ],
)
@pytest.mark.now(NOW)
async def test_handle_responsive(
        mongodb, taxi_driver_order_messages, data, code,
):
    response = await taxi_driver_order_messages.post(
        'v1/messages/add', data=json.dumps(data),
    )
    assert response.status_code == code
    if code == 200:
        assert response.json() == {}
        messages = list(mongodb.ordermessages.find({}))
        assert len(messages) == 1
        assert messages[0]['db'] == data['park_id']
        assert messages[0]['order'] == data['order_id']
        date = messages[0]['date'].replace(tzinfo=pytz.utc).isoformat()
        if 'date' in data:
            assert date == data['date']
        else:
            assert date == NOW
        assert messages[0]['user_name'] == data['user_name']
        assert messages[0]['message'] == data['message']
        assert ('info' in messages[0]) == ('info' in data)
        if 'info' in data:
            assert messages[0]['info'] == data['info']


@pytest.mark.parametrize(
    'data_array',
    [
        (
            [
                {
                    'data': {
                        'headers': {'X-Idempotency-Token': 'super_token_2'},
                        'data': {
                            'park_id': 'park_id_0',
                            'order_id': 'order_id_0',
                            'user_name': 'John Doe [T777TT 77RUS]',
                            'message': 'Order message',
                        },
                        'code': 200,
                    },
                    'times': 1,
                },
                {
                    'data': {
                        'headers': {'X-Idempotency-Token': 'super_token_2'},
                        'data': {
                            'park_id': 'park_id',
                            'order_id': 'order_id_0',
                            'user_name': 'John Doe [T777TT 77RUS]',
                            'message': 'Order message',
                        },
                        'code': 200,
                    },
                    'times': 1,
                },
            ]
        ),
        (
            [
                {
                    'data': {
                        'headers': {'X-Idempotency-Token': 'super_token_2'},
                        'data': {
                            'park_id': 'park_id_0',
                            'order_id': 'order_id_0',
                            'user_name': 'John Doe [T777TT 77RUS]',
                            'message': 'Order message',
                        },
                        'code': 200,
                    },
                    'times': 2,
                },
            ]
        ),
        (
            [
                {
                    'data': {
                        'headers': {'X-Idempotency-Token': 'super_token_3'},
                        'data': {
                            'park_id': 'park_id_0',
                            'order_id': 'order_id_0',
                            'user_name': 'John Doe [T777TT 77RUS]',
                            'message': 'Order message',
                        },
                        'code': 200,
                    },
                    'times': 2,
                },
                {
                    'data': {
                        'headers': {'X-Idempotency-Token': 'super_token_4'},
                        'data': {
                            'park_id': 'park_id_1',
                            'order_id': 'order_id_1',
                            'user_name': 'John Moe [T777TT 77RUS]',
                            'message': 'Different order message',
                        },
                        'code': 200,
                    },
                    'times': 2,
                },
            ]
        ),
    ],
)
async def test_idempotency(mongodb, taxi_driver_order_messages, data_array):
    for value in data_array:
        for _ in range(value['times']):
            response = await taxi_driver_order_messages.post(
                'v1/messages/add',
                data=json.dumps(value['data']['data']),
                headers=value['data']['headers'],
            )
            assert response.status_code == value['data']['code']

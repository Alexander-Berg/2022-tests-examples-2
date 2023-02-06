import pytest


@pytest.mark.parametrize(
    'data,headers,expected_code,expected_stq_put',
    [
        ({}, {}, 400, None),
        ({}, {'X-Yandex-UID': '123'}, 400, None),
        ({'phone': '+123'}, {}, 400, None),
        (
            {'phone': '+79011231234'},
            {'X-Yandex-UID': '123'},
            200,
            {
                'task_id': '2104653bdac343e39ac57869d0bd738d',
                'args': ['123', '+79011231234'],
                'kwargs': {'locale': 'ru', 'urgent': True},
            },
        ),
        (
            {'phone': '+79001231234'},
            {'X-Yandex-UID': '1234', 'Accept-Language': 'en-En'},
            200,
            {
                'task_id': '2104653bdac343e39ac57869d0bd738d',
                'args': ['1234', '+79001231234'],
                'kwargs': {'locale': 'en', 'urgent': True},
            },
        ),
        (
            {'phone': '+79001231234', 'urgent': False},
            {'X-Yandex-UID': '1234', 'Accept-Language': 'en-En'},
            200,
            {
                'task_id': '2104653bdac343e39ac57869d0bd738d',
                'args': ['1234', '+79001231234'],
                'kwargs': {'locale': 'en', 'urgent': False},
            },
        ),
        (
            {'phone': '+79001231234', 'urgent': True},
            {'X-Yandex-UID': '1234', 'Accept-Language': 'en-En'},
            200,
            {
                'task_id': '2104653bdac343e39ac57869d0bd738d',
                'args': ['1234', '+79001231234'],
                'kwargs': {'locale': 'en', 'urgent': True},
            },
        ),
    ],
)
async def test_doctor_callback(
        stq,
        mock_uuid_fixture,
        protocol_client,
        data,
        headers,
        expected_code,
        expected_stq_put,
):
    response = await protocol_client.post(
        '/perseus/doctor_callback/', json=data, headers=headers,
    )
    assert response.status == expected_code

    if expected_code == 200:
        stq_put_call = stq.support_info_doctor_callback.next_call()
        del stq_put_call['kwargs']['log_extra']
        del stq_put_call['eta']
        stq_put_call['task_id'] = stq_put_call.pop('id')
        del stq_put_call['queue']
        assert stq_put_call == expected_stq_put

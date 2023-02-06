import pytest


@pytest.mark.pgsql('callcenter_queues', files=['insert_call.sql'])
@pytest.mark.parametrize(
    ['request_data', 'expected_status', 'expected_body'],
    (
        pytest.param(
            {'commutation_id': 'test_1'},
            200,
            {
                'personal_phone_id': 'test_phone_id',
                'called_number': '+71234567890',
                'metaqueue': 'disp',
                'subcluster': '1',
            },
            id='Successfully fetched',
        ),
        pytest.param(
            {'commutation_id': 'test_2'},
            500,
            {'code': 'Invalid raw', 'message': 'No numbers in db'},
            id='Not found',
        ),
        pytest.param(
            {'commutation_id': 'test_3'},
            500,
            {'code': 'Invalid raw', 'message': 'No numbers in db'},
            id='Not found',
        ),
        pytest.param(
            {'commutation_id': 'test_4'},
            404,
            {
                'code': 'Not found',
                'message': 'No call with requested commutation_id',
            },
            id='Not found',
        ),
    ),
)
async def test_base(
        taxi_callcenter_queues, request_data, expected_status, expected_body,
):
    response = await taxi_callcenter_queues.post(
        '/v1/call_info', json=request_data,
    )
    assert response.status == expected_status
    assert response.json() == expected_body

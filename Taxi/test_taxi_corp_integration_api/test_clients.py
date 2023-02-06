import pytest


@pytest.mark.parametrize(
    'limit, timestamp, expected_response',
    [
        pytest.param(
            None,
            None,
            {
                'clients': [
                    {
                        'id': 'client1',
                        'billing_client_id': 'billing_id1',
                        'yandex_uid': 'client1_uid',
                        'updated_at': '1532470703.0',
                    },
                    {
                        'id': 'client2',
                        'billing_client_id': 'billing_id2',
                        'yandex_uid': 'client2_uid',
                        'updated_at': '1552470703.65',
                    },
                    {
                        'id': 'client3',
                        'billing_client_id': None,
                        'yandex_uid': 'client3_uid',
                        'updated_at': '1582470703.13',
                    },
                ],
            },
            id='get_without_params',
        ),
        pytest.param(
            2,
            '1562470703.0',
            {
                'clients': [
                    {
                        'id': 'client3',
                        'billing_client_id': None,
                        'yandex_uid': 'client3_uid',
                        'updated_at': '1582470703.13',
                    },
                ],
            },
            id='get_with_params',
        ),
    ],
)
async def test_get_clients(
        web_app_client, limit, timestamp, expected_response,
):
    params = {}
    if limit is not None:
        params['limit'] = limit
    if timestamp is not None:
        params['updated_at'] = timestamp
    response = await web_app_client.get('/v1/clients/list', params=params)

    assert response.status == 200
    assert (await response.json()) == expected_response


@pytest.mark.parametrize(
    'limit, timestamp',
    [
        pytest.param(0, None, id='limit_is_0'),
        pytest.param(1500, None, id='limit_is_big'),
        pytest.param('wrong_limit', None, id='limit_not_int'),
        pytest.param(1, 'wrong_date', id='wrong_timestamp'),
    ],
)
async def test_400(web_app_client, limit, timestamp):
    params = {}
    if limit is not None:
        params['limit'] = limit
    if timestamp is not None:
        params['updated_at'] = timestamp
    response = await web_app_client.get('/v1/clients/list', params=params)

    assert response.status == 400

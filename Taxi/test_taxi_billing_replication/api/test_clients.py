import pytest


@pytest.mark.parametrize(
    'yandex_uid,expected_result',
    [
        pytest.param(
            'yandex_uid1',
            {'billing_id': 'client_id1_billing_id', 'client_id': 'client_id1'},
            id='standart',
        ),
        pytest.param('yandex_uid2', {}, id='unknown uid'),
    ],
)
async def test_get_corp_client(
        taxi_billing_replication_client, yandex_uid, expected_result,
):
    response = await taxi_billing_replication_client.request(
        'GET', '/corp-client/', params={'yandex_uid': yandex_uid},
    )

    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.parametrize('yandex_uid', [pytest.param(None, id='none uid')])
async def test_get_corp_client_fail(
        taxi_billing_replication_client, yandex_uid,
):
    with pytest.raises(TypeError):
        await taxi_billing_replication_client.request(
            'GET', '/corp-client/', params={'yandex_uid': yandex_uid},
        )


@pytest.mark.parametrize(
    'params, expected_data,expected_max_revision',
    [
        (
            {'revision': 0, 'limit': 1},
            [{'client_id': 'client_id2', 'park_id': 'park_id2'}],
            1,
        ),
        ({'revision': 0, 'limit': 0}, [], 0),
    ],
)
async def test_get_clients_by_revision(
        taxi_billing_replication_client,
        params,
        expected_data,
        expected_max_revision,
):
    response = await taxi_billing_replication_client.request(
        'GET', '/v1/clients/by_revision/', params=params,
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['clients'] == expected_data
    assert expected_max_revision == response_data['max_revision']

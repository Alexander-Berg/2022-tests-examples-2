import pytest

from tests_eats_retail_categories import utils


def mock_eats_eaters(mockserver):
    @mockserver.json_handler(utils.Handlers.FIND_BY_PASPORT_UIDS)
    def _mock_eats_eaters_v1_eaters_find_by_passport_uids(request):
        eaters = []
        for eater_id in request.json['passport_uids']:
            item = {
                'id': eater_id,
                'uuid': f'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa{eater_id}',
                'created_at': '2022-01-01T07:59:59+00:00',
                'updated_at': '2022-01-01T07:59:59+00:00',
            }
            eaters.append(item)
        return {
            'eaters': eaters,
            'pagination': {'limit': 1000, 'has_more': False},
        }


@pytest.mark.parametrize('network_error', [True, False])
async def test_takeout_eats_eaters_error(
        mockserver, taxi_eats_retail_categories, network_error,
):
    """
    Тест проверяет, что если ручка /eats-eaters/v1/eaters/find-by-passport-uids
    вернула 500, то ручка статуса в ответ вернет тоже 500.
    """

    @mockserver.json_handler(utils.Handlers.FIND_BY_PASPORT_UIDS)
    def _mock_eats_eaters_v1_eaters_find_by_passport_uids(request):
        if network_error:
            raise mockserver.NetworkError()
        else:
            return mockserver.make_response(status=500)

    response = await taxi_eats_retail_categories.post(
        '/takeout/v1/status',
        headers=utils.HEADERS,
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in ['1', '2', '3']
            ],
        },
    )
    assert _mock_eats_eaters_v1_eaters_find_by_passport_uids.times_called == 1
    assert response.status_code == 500


@pytest.mark.parametrize(
    'request_yandex_uids, expected_state',
    [
        (['1', '2', '3'], 'ready_to_delete'),
        (['1', '2', '4'], 'ready_to_delete'),
        (['4', '5', '6'], 'empty'),
    ],
)
async def test_takeout_status(
        mockserver,
        taxi_eats_retail_categories,
        pg_add_user_orders_updates,
        pg_add_user_crossbrand_product,
        pg_add_user_ordered_product,
        pg_add_brand,
        request_yandex_uids,
        expected_state,
):
    """
    Тест проверяет наличие записей с данными eater_id.
    Ручка отдаст ответ с соответствующим статусом
    """
    mock_eats_eaters(mockserver)
    pg_add_brand()
    for yandex_uid in ['1', '2', '3']:
        pg_add_user_orders_updates(eater_id=yandex_uid)
        pg_add_user_crossbrand_product(eater_id=yandex_uid)
        pg_add_user_ordered_product(
            public_id=utils.PUBLIC_IDS[0], eater_id=yandex_uid,
        )

    response = await taxi_eats_retail_categories.post(
        '/takeout/v1/status',
        headers=utils.HEADERS,
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in request_yandex_uids
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'data_state': expected_state}


@pytest.mark.parametrize(
    'request_yandex_uids, expected_state',
    [
        (['1', '2', '3'], 'empty'),
        (['1', '2', '4'], 'ready_to_delete'),
        (['4', '5', '6'], 'ready_to_delete'),
    ],
)
async def test_takeout_delete(
        mockserver,
        taxi_eats_retail_categories,
        pg_add_user_orders_updates,
        pg_add_user_crossbrand_product,
        pg_add_user_ordered_product,
        pg_add_brand,
        request_yandex_uids,
        expected_state,
):
    """
    Тест проверяет удаление записей с данными eater_id.
    """
    mock_eats_eaters(mockserver)
    pg_add_brand()
    for yandex_uid in ['1', '2', '3']:
        pg_add_user_orders_updates(eater_id=yandex_uid)
        pg_add_user_crossbrand_product(eater_id=yandex_uid)
        pg_add_user_ordered_product(
            public_id=utils.PUBLIC_IDS[0], eater_id=yandex_uid,
        )

    response = await taxi_eats_retail_categories.post(
        '/takeout/v1/delete',
        headers=utils.HEADERS,
        json={
            'request_id': 'request_id',
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in request_yandex_uids
            ],
        },
    )
    assert response.status_code == 200

    response = await taxi_eats_retail_categories.post(
        '/takeout/v1/status',
        headers=utils.HEADERS,
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in ['1', '2', '3']
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'data_state': expected_state}

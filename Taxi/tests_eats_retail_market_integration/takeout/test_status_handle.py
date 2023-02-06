import pytest

from tests_eats_retail_market_integration import models

STATUS_HANDLER = '/takeout/v1/status'
EATS_EATERS_FIND_BY_PASSPORT_UIDS_HANDLER = (
    '/eats-eaters/v1/eaters/find-by-passport-uids'
)
PASSPORT_UID_1 = 'passport_uid_1'
PASSPORT_UID_2 = 'passport_uid_2'
PASSPORT_UID_3 = 'passport_uid_3'
EATER_ID_1 = 'eater_id_1'
EATER_ID_2 = 'eater_id_2'
EATER_ID_3 = 'eater_id_3'
ORDER_NR_1 = 'order_nr_1'
ORDER_NR_2 = 'order_nr_2'

PASSPORT_TO_EATER_ID_MAP = {
    PASSPORT_UID_1: EATER_ID_1,
    PASSPORT_UID_2: EATER_ID_2,
    PASSPORT_UID_3: EATER_ID_3,
}


@pytest.mark.parametrize(
    'known_passport_uids_by_eats_eaters, expected_status',
    [({}, 'empty'), ({PASSPORT_UID_1}, 'ready_to_delete')],
)
async def test_status_handle_depending_on_eats_eaters_known_passport_uids(
        taxi_eats_retail_market_integration,
        mockserver,
        save_orders_to_db,
        # parametrize
        known_passport_uids_by_eats_eaters,
        expected_status,
):
    mock_eats_eaters(mockserver, known_passport_uids_by_eats_eaters)

    orders = [models.Order(ORDER_NR_1, EATER_ID_1)]
    save_orders_to_db(orders)

    response = await taxi_eats_retail_market_integration.post(
        STATUS_HANDLER,
        json={'yandex_uids': [{'uid': PASSPORT_UID_1, 'is_portal': False}]},
    )

    assert response.status == 200
    assert response.json() == {'data_state': expected_status}


@pytest.mark.parametrize(
    'yandex_uids, expected_status',
    [
        pytest.param(
            [PASSPORT_UID_1], 'ready_to_delete', id='one_present_uid',
        ),
        pytest.param(
            [PASSPORT_UID_1, PASSPORT_UID_2],
            'ready_to_delete',
            id='two_present_uids',
        ),
        pytest.param(
            [PASSPORT_UID_1, PASSPORT_UID_3],
            'ready_to_delete',
            id='present_and_missing_uids',
        ),
        pytest.param([PASSPORT_UID_3], 'empty', id='one_missing_uid'),
    ],
)
async def test_status_handle(
        taxi_eats_retail_market_integration,
        mockserver,
        save_orders_to_db,
        # parametrize
        yandex_uids,
        expected_status,
):
    mock_eats_eaters(mockserver)

    orders = [
        models.Order(ORDER_NR_1, EATER_ID_1),
        models.Order(ORDER_NR_2, EATER_ID_2),
    ]
    save_orders_to_db(orders)

    response = await taxi_eats_retail_market_integration.post(
        STATUS_HANDLER,
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in yandex_uids
            ],
        },
    )

    assert response.status == 200
    assert response.json() == {'data_state': expected_status}


async def test_eats_eaters_pagination(
        taxi_eats_retail_market_integration,
        mockserver,
        save_orders_to_db,
        update_taxi_config,
):
    mock_eats_eaters_with_pagination(
        mockserver, eaters_pages=[[EATER_ID_1, EATER_ID_2], [EATER_ID_3]],
    )
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_EATS_EATERS_SETTINGS',
        {'pagination_page_size': 2},
    )

    yandex_uids = [PASSPORT_UID_1, PASSPORT_UID_2, PASSPORT_UID_3]
    expected_status = 'ready_to_delete'

    orders = [
        models.Order(ORDER_NR_1, EATER_ID_1),
        models.Order(ORDER_NR_2, EATER_ID_2),
    ]
    save_orders_to_db(orders)

    response = await taxi_eats_retail_market_integration.post(
        STATUS_HANDLER,
        json={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in yandex_uids
            ],
        },
    )

    assert response.status == 200
    assert response.json() == {'data_state': expected_status}


def mock_eats_eaters(mockserver, known_passport_uids=None):
    @mockserver.json_handler(EATS_EATERS_FIND_BY_PASSPORT_UIDS_HANDLER)
    def _mock_eats_eaters_v1_eaters_find_by_passport_uids(request):
        eaters = []
        for passport_id in request.json['passport_uids']:
            if (known_passport_uids is None) or (
                    passport_id in known_passport_uids
            ):
                eaters.append(
                    {
                        'id': PASSPORT_TO_EATER_ID_MAP[passport_id],
                        # fields below are dummy - required by schema
                        'uuid': '00000000-0000-0000-0000-000000000000',
                        'created_at': '2022-01-01T07:59:59+00:00',
                        'updated_at': '2022-01-01T07:59:59+00:00',
                    },
                )

        return {
            'eaters': eaters,
            'pagination': {'limit': 1000, 'has_more': False},
        }


# pylint: disable=C0103
def mock_eats_eaters_with_pagination(mockserver, eaters_pages):
    @mockserver.json_handler(EATS_EATERS_FIND_BY_PASSPORT_UIDS_HANDLER)
    def _mock_eats_eaters_v1_eaters_find_by_passport_uids(request):
        page_number = 0 if request.json['pagination']['after'] == '0' else 1
        return {
            'eaters': [
                {
                    'id': eater_id,
                    # fields below are dummy - required by schema
                    'uuid': '00000000-0000-0000-0000-000000000000',
                    'created_at': '2022-01-01T07:59:59+00:00',
                    'updated_at': '2022-01-01T07:59:59+00:00',
                }
                for eater_id in eaters_pages[page_number]
            ],
            'pagination': {
                'limit': request.json['pagination']['limit'],
                'has_more': (page_number == 0),
            },
        }

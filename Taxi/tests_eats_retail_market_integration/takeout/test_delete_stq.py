import pytest

from tests_eats_retail_market_integration import models


EATS_EATERS_FIND_BY_PASSPORT_UIDS_HANDLER = (
    '/eats-eaters/v1/eaters/find-by-passport-uids'
)
DELETE_STQ_COMPONENT_NAME = 'stq_takeout_delete'
PASSPORT_UID_1 = 'passport_uid_1'
PASSPORT_UID_2 = 'passport_uid_2'
EATER_ID_1 = 'eater_id_1'
EATER_ID_2 = 'eater_id_2'
ORDER_NR_1 = 'order_nr_1'
ORDER_NR_2 = 'order_nr_2'
ORDER_NR_3 = 'order_nr_3'

PASSPORT_TO_EATER_ID_MAP = {
    PASSPORT_UID_1: EATER_ID_1,
    PASSPORT_UID_2: EATER_ID_2,
}


@pytest.mark.parametrize(
    'orders, yandex_uids, test_id',
    [
        pytest.param([], [PASSPORT_UID_1], 'eater_not_present_in_db'),
        pytest.param(
            [
                {'order_nr': ORDER_NR_1, 'eater_id': EATER_ID_1},
                {'order_nr': ORDER_NR_2, 'eater_id': EATER_ID_2},
            ],
            [PASSPORT_UID_1],
            'delete_exact_eater_with_single_order',
        ),
        pytest.param(
            [
                {'order_nr': ORDER_NR_1, 'eater_id': EATER_ID_1},
                {'order_nr': ORDER_NR_2, 'eater_id': EATER_ID_1},
            ],
            [PASSPORT_UID_1],
            'delete_eater_with_multiple_orders',
        ),
        pytest.param(
            [
                {'order_nr': ORDER_NR_1, 'eater_id': EATER_ID_1},
                {'order_nr': ORDER_NR_2, 'eater_id': EATER_ID_1},
                {'order_nr': ORDER_NR_3, 'eater_id': EATER_ID_2},
            ],
            [PASSPORT_UID_1, PASSPORT_UID_2],
            'delete_multiple_eaters',
        ),
    ],
)
async def test_delete_stq(
        get_orders_from_db,
        mockserver,
        save_orders_to_db,
        stq_runner,
        # parametrize
        orders,
        yandex_uids,
        test_id,
):
    mock_eats_eaters(mockserver)

    orders = [models.Order(**order_args) for order_args in orders]
    save_orders_to_db(orders)

    await stq_runner.eats_retail_market_integration_takeout_delete.call(
        task_id=test_id,
        args=[],
        kwargs={
            'yandex_uids': [
                {'uid': yandex_uid, 'is_portal': False}
                for yandex_uid in yandex_uids
            ],
        },
        expect_fail=False,
    )

    expected_orders = []
    if test_id == 'delete_exact_eater_with_single_order':
        expected_orders.append(
            models.Order(order_nr=ORDER_NR_2, eater_id=EATER_ID_2),
        )

    assert get_orders_from_db() == expected_orders


async def test_stq_error_limit(
        mockserver, stq_runner, testpoint, update_taxi_config,
):
    max_retries_on_error = 3
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_STQ_PROCESSING',
        {
            DELETE_STQ_COMPONENT_NAME: {
                'max_retries_on_error': max_retries_on_error,
            },
        },
    )

    @testpoint('eats-retail-market-integration-takeout-delete::fail')
    def _task_testpoint(param):
        return {'inject_failure': True}

    for i in range(max_retries_on_error):
        await stq_runner.eats_retail_market_integration_takeout_delete.call(  # noqa: E501 pylint: disable=line-too-long
            task_id='1',
            args=[],
            kwargs={
                'yandex_uids': [{'uid': PASSPORT_UID_1, 'is_portal': False}],
            },
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_retail_market_integration_takeout_delete.call(
        task_id='1',
        args=[],
        kwargs={'yandex_uids': [{'uid': PASSPORT_UID_1, 'is_portal': False}]},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )


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

import copy
import datetime
import time

import pytest

REQUEST = {'series_id': 'first', 'yandex_uids': ['1', '2', '3', '4', '5']}
COUPONS_SERIES_INFO_RESPONSE = {
    'series_id': REQUEST['series_id'],
    'services': ['taxi'],
    'is_unique': True,
    'start': '2016-03-01',
    'finish': '2020-03-01',
    'descr': 'Уникальный, истек срок действия',
    'value': 123,
    'created': '2016-03-01T03:00:00+0300',
    'user_limit': 2,
    'currency': 'RUB',
    'country': 'rus',
}

COUPONS_SERIES_INFO_RESPONS_EXPIRED_NOW = {
    'series_id': REQUEST['series_id'],
    'services': ['taxi'],
    'is_unique': True,
    'start': '2016-03-01',
    'finish': datetime.date.fromtimestamp(time.time()).isoformat(),
    'descr': 'Уникальный, истек срок действия',
    'value': 123,
    'created': '2016-03-01T03:00:00+0300',
    'user_limit': 2,
    'currency': 'RUB',
    'country': 'rus',
}


def insert_into_dict(main_dict, **kwargs):
    result = copy.deepcopy(main_dict)
    for key, value in kwargs.items():
        result[key] = value
    return result


def get_uids_in_series_white_list(pgsql, series_id):
    cursor = pgsql['eats_coupons'].cursor()
    cursor.execute(
        f"""SELECT yandex_uid
        FROM eats_coupons.promocodes_white_lists
        WHERE series_id=\'{series_id}\';""",
    )
    result = cursor.fetchall()
    return list(x[0] for x in result)


@pytest.mark.config(
    EATS_COUPONS_ADD_USERS_TO_WHITE_LIST_SETTINGS={
        'batch_size': 50,
        'series_checks': {
            'is_series_exist_enabled': True,
            'is_series_contain_white_list_enabled': True,
        },
    },
)
@pytest.mark.config(
    EATS_COUPONS_SERIES_WHITELIST_CLEANUP_SETTINGS={
        'cleanup_enabled': True,
        'ttl_after_series_finish_sec': 10,
        'task_period_frequency_sec': 1,
        'batch_size': 1,
    },
)
@pytest.mark.parametrize(
    'coupons_response,coupons_code, expected_code',
    [
        pytest.param(
            insert_into_dict(
                COUPONS_SERIES_INFO_RESPONSE,
                external_meta={'check-users-in-whitelist': True},
            ),
            200,
            200,
            id='white list validator is enabled success insert',
        ),
        pytest.param({'message': 'error'}, 404, 400, id='Series not found'),
    ],
)
async def test_yandex_uids_insert_and_delete(
        testpoint,
        taxi_eats_coupons,
        pgsql,
        mockserver,
        coupons_response,
        coupons_code,
        expected_code,
):
    @mockserver.json_handler('/coupons/internal/series/info')
    def _mock_series_info(request):
        assert request.json == {'series_id': REQUEST['series_id']}
        return mockserver.make_response(
            status=coupons_code, json=coupons_response,
        )

    await taxi_eats_coupons.post('/internal/white-list', json=REQUEST)

    @testpoint('series-whitelist-cleaner-finished')
    async def handle_finished(arg):
        return

    async with taxi_eats_coupons.spawn_task(
            'distlock/series-whitelist-cleaner',
    ):
        await handle_finished.wait_call()

    now_series = get_uids_in_series_white_list(
        pgsql=pgsql, series_id=REQUEST['series_id'],
    )
    assert not now_series


@pytest.mark.config(
    EATS_COUPONS_ADD_USERS_TO_WHITE_LIST_SETTINGS={
        'batch_size': 50,
        'series_checks': {
            'is_series_exist_enabled': True,
            'is_series_contain_white_list_enabled': True,
        },
    },
)
@pytest.mark.config(
    EATS_COUPONS_SERIES_WHITELIST_CLEANUP_SETTINGS={
        'cleanup_enabled': True,
        'ttl_after_series_finish_sec': 99999999,
        'task_period_frequency_sec': 1,
        'batch_size': 1,
    },
)
async def test_yandex_uids_insert_and_time_is_not_expired(
        testpoint, taxi_eats_coupons, pgsql, mockserver,
):
    @mockserver.json_handler('/coupons/internal/series/info')
    def _mock_series_info(request):
        assert request.json == {'series_id': REQUEST['series_id']}
        return mockserver.make_response(
            status=200,
            json=insert_into_dict(
                COUPONS_SERIES_INFO_RESPONS_EXPIRED_NOW,
                external_meta={'check-users-in-whitelist': True},
            ),
        )

    await taxi_eats_coupons.post('/internal/white-list', json=REQUEST)

    @testpoint('series-whitelist-cleaner-finished')
    async def handle_finished(arg):
        return

    async with taxi_eats_coupons.spawn_task(
            'distlock/series-whitelist-cleaner',
    ):
        await handle_finished.wait_call()

    now_series = get_uids_in_series_white_list(
        pgsql=pgsql, series_id=REQUEST['series_id'],
    )
    assert now_series

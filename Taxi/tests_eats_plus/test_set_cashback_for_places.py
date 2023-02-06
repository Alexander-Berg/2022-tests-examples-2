import datetime

import pytest

from . import cashback_settings


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': False,
        'update_period_ms': 1000,
    },
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_set_cashback_for_places_happy_path(
        taxi_eats_plus,
        pgsql,
        mocked_time,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
):
    eats_order_stats()
    passport_blackbox()
    plus_wallet({'RUB': 123321})
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 20,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                    'place_cashback': {
                        'cashback': 5,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['eats_plus'].cursor()
    settings = cashback_settings.get_plus_settings(place_id=20, cursor=cursor)

    assert settings is not None
    assert len(settings.eda_cashback) == 1
    assert len(settings.place_cashback) == 1


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': False,
        'update_period_ms': 1000,
    },
)
@pytest.mark.parametrize(
    'place_id, eda_cashback, place_cashback, expected_code',
    [
        (
            20,
            {'cashback': 10, 'active_from': '2021-07-29T00:00:00.000000Z'},
            {'cashback': 5, 'active_from': '2021-07-29T00:00:00.000000Z'},
            200,
        ),
        (
            21,
            {
                'cashback': 6,
                'active_from': datetime.datetime.now().strftime(
                    '%Y-%m-%dT%H:%M:%S.000000Z',
                ),
            },
            {
                'cashback': 6,
                'active_from': datetime.datetime.now().strftime(
                    '%Y-%m-%dT%H:%M:%S.000000Z',
                ),
            },
            200,
        ),
        (
            123123,
            {
                'cashback': 10,
                'active_from': (
                    datetime.datetime.now() + datetime.timedelta(hours=48)
                ).strftime('%Y-%m-%dT%H:%M:%S.000000Z'),
            },
            {
                'cashback': 7.5,
                'active_from': (
                    datetime.datetime.now() + datetime.timedelta(hours=48)
                ).strftime('%Y-%m-%dT%H:%M:%S.000000Z'),
            },
            200,
        ),
    ],
)
async def test_set_cashback_for_places_check_duplicates_double_call(
        taxi_eats_plus,
        pgsql,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
        place_id,
        eda_cashback,
        place_cashback,
        expected_code,
):
    eats_order_stats()
    passport_blackbox()
    plus_wallet({'RUB': 123321})
    first_response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': place_id,
                    'plus': True,
                    'eda_cashback': eda_cashback,
                    'place_cashback': place_cashback,
                },
            ],
        },
    )
    assert first_response.status_code == expected_code

    second_response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': place_id,
                    'plus': True,
                    'eda_cashback': eda_cashback,
                    'place_cashback': place_cashback,
                },
            ],
        },
    )
    assert second_response.status_code == expected_code

    cursor = pgsql['eats_plus'].cursor()
    cursor.execute(
        'SELECT cashback, active_from, active_till, type '
        'FROM eats_plus.cashback_settings '
        f'WHERE place_id={place_id}'
        'ORDER BY type',
    )
    settings = cursor.fetchall()

    assert settings is not None
    assert len(settings) == 2

    assert settings[0][3] == 'eda'
    assert settings[0][0] == eda_cashback['cashback']
    assert settings[0][2] is None

    assert settings[1][3] == 'place'
    assert settings[1][0] == place_cashback['cashback']
    assert settings[1][2] is None


@pytest.mark.now('2020-11-26T00:00:01.000000Z')
@pytest.mark.experiments3(
    filename='exp3_eats_plus_place_cashback_presentation.json',
)
async def test_set_cashback_for_places_invalid_params(taxi_eats_plus, pgsql):
    await taxi_eats_plus.invalidate_caches()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 28,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-11-25T00:00:00.000000Z',
                    },
                    'place_cashback': {
                        'cashback': 5,
                        'active_from': '2020-11-26T00:00:00.000000Z',
                    },
                },
            ],
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'INVALID_PLACES',
        'message': 'Some places has invalid settings',
        'details': {'place_ids': [28]},
    }


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': False,
        'update_period_ms': 1000,
    },
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_set_cashback_for_places_update_old_settings(
        taxi_eats_plus,
        pgsql,
        mocked_time,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
):
    eats_order_stats()
    passport_blackbox()
    plus_wallet({'RUB': 123321})
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 1,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 8,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                    'place_cashback': {
                        'cashback': 9,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['eats_plus'].cursor()
    settings = cashback_settings.get_plus_settings(place_id=1, cursor=cursor)
    # новые данные должны попасть в future таблицу
    assert settings is not None
    # для старых настроек проставлен active_till
    assert (
        settings.place_cashback[0].active_till
        == settings.place_cashback[1].active_from
    )
    assert (
        settings.eda_cashback[0].active_till
        == settings.eda_cashback[1].active_from
    )


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': False,
        'update_period_ms': 1000,
    },
)
async def test_set_cashback_for_places_update_new_settings(
        taxi_eats_plus,
        pgsql,
        mocked_time,
        passport_blackbox,
        eats_order_stats,
        plus_wallet,
):
    eats_order_stats()
    passport_blackbox()
    plus_wallet({'RUB': 123321})
    mocked_time.set(datetime.datetime.now())
    await taxi_eats_plus.invalidate_caches()
    real_future = datetime.datetime.now() + datetime.timedelta(hours=48)
    real_future = real_future.strftime('%Y-%m-%dT%H:%M:%S')
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 5,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 8,
                        'active_from': real_future + '.0000Z',
                    },
                    'place_cashback': {
                        'cashback': 9,
                        'active_from': real_future + '.0000Z',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['eats_plus'].cursor()
    settings = cashback_settings.get_plus_settings(place_id=1, cursor=cursor)
    assert settings is not None
    assert len(settings.place_cashback) == 1
    assert len(settings.eda_cashback) == 1


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': True,
        'update_period_ms': 1000,
    },
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_update_cashback_for_places_periodic(taxi_eats_plus, pgsql):
    cursor = pgsql['eats_plus'].cursor()
    cursor.execute(
        'SELECT count(*) '
        'FROM eats_plus.place_plus_settings '
        f'WHERE NOT active;',
    )
    inactive_count = cursor.fetchone()
    assert inactive_count[0] == 2
    cursor.execute(
        'SELECT count(*) '
        'FROM eats_plus.cashback_settings '
        'WHERE EXISTS ( '
        'SELECT 1 FROM eats_plus.place_plus_settings '
        'WHERE NOT active AND '
        f'place_plus_settings.place_id = cashback_settings.place_id);',
    )
    inactive_count = cursor.fetchone()
    assert inactive_count[0] == 4

    await taxi_eats_plus.run_periodic_task('clean-plus-settings')

    cursor.execute(
        'SELECT count(*) '
        'FROM eats_plus.place_plus_settings '
        f'WHERE NOT active;',
    )
    inactive_count = cursor.fetchone()
    assert inactive_count[0] == 0
    cursor.execute(
        'SELECT count(*) '
        'FROM eats_plus.cashback_settings '
        'WHERE EXISTS ( '
        'SELECT 1 FROM eats_plus.place_plus_settings '
        'WHERE NOT active AND '
        f'place_plus_settings.place_id = cashback_settings.place_id);',
    )
    inactive_count = cursor.fetchone()
    assert inactive_count[0] == 0

    current_settings = cashback_settings.get_plus_settings(
        place_id=3, cursor=cursor,
    )
    assert current_settings is not None
    assert len(current_settings.place_cashback) == 1
    assert len(current_settings.eda_cashback) == 1

    current_settings = cashback_settings.get_plus_settings(
        place_id=4, cursor=cursor,
    )
    assert current_settings is not None
    assert len(current_settings.place_cashback) == 1
    assert not current_settings.eda_cashback

    current_settings = cashback_settings.get_plus_settings(
        place_id=28, cursor=cursor,
    )
    assert current_settings is None


@pytest.mark.config(
    EATS_PLUS_SETTINGS_UPDATE_TASK_CONFIGS={
        'enabled': True,
        'update_period_ms': 1000,
    },
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_delete_duplicates_periodic(taxi_eats_plus, pgsql):
    cursor = pgsql['eats_plus'].cursor()
    cursor.execute(
        'SELECT count(*) '
        'FROM eats_plus.cashback_settings '
        f'WHERE place_id = 111;',
    )
    cashbacks_count = cursor.fetchone()
    assert cashbacks_count[0] == 6

    await taxi_eats_plus.run_periodic_task('clean-plus-settings')

    cursor.execute(
        'SELECT count(*) '
        'FROM eats_plus.cashback_settings '
        f'WHERE place_id = 111;',
    )
    cashbacks_count = cursor.fetchone()
    assert cashbacks_count[0] == 2


@pytest.mark.now('2020-12-08T11:37:01+03:00')
async def test_set_cashback_for_places_active_from_tomorrow(
        taxi_eats_plus, pgsql,
):
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 20,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-12-09T00:00:00+03:00',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['eats_plus'].cursor()
    current_settings = cashback_settings.get_plus_settings(
        place_id=20, cursor=cursor,
    )
    assert current_settings is not None
    assert not current_settings.place_cashback
    assert len(current_settings.eda_cashback) == 1


@pytest.mark.now('2020-12-08T11:37:01+03:00')
async def test_set_cashback_for_places_new_active_from_past(
        taxi_eats_plus, pgsql,
):
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 12,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-12-01T00:00:00+03:00',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['eats_plus'].cursor()
    current_settings = cashback_settings.get_plus_settings(
        place_id=12, cursor=cursor,
    )
    assert current_settings is not None
    assert not current_settings.place_cashback
    assert len(current_settings.eda_cashback) == 1


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_set_cashback_for_places_history(taxi_eats_plus, pgsql):
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={
            'places_settings': [
                {
                    'place_id': 20,
                    'plus': True,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                    'place_cashback': {
                        'cashback': 5,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                },
            ],
        },
    )
    assert response.status_code == 200
    cursor = pgsql['eats_plus'].cursor()
    cursor.execute(
        'SELECT place_id, active '
        'FROM eats_plus.plus_settings_change_history '
        f'WHERE place_id=20;',
    )
    settings = cursor.fetchone()
    assert settings is not None


@pytest.mark.parametrize(
    ['places_settings', 'expected_code'],
    [
        ([{'place_id': 111, 'plus': False}], 200),
        ([{'place_id': 111, 'plus': True}], 400),
        ([{'place_id': 222, 'plus': False}], 400),
        (
            [
                {
                    'place_id': 20,
                    'plus': False,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                    'place_cashback': {
                        'cashback': 5,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                },
            ],
            200,
        ),
        (
            [
                {
                    'place_id': 222,
                    'plus': False,
                    'eda_cashback': {
                        'cashback': 10,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                    'place_cashback': {
                        'cashback': 5,
                        'active_from': '2020-11-27T00:00:00.000000Z',
                    },
                },
            ],
            200,
        ),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_set_cashback_plus_deactivating(
        taxi_eats_plus, pgsql, places_settings, expected_code,
):
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/settings/cashback',
        json={'places_settings': places_settings},
    )
    assert response.status_code == expected_code

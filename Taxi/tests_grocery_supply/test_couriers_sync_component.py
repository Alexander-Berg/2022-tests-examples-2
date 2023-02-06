import datetime

import pytest


DATETIME_NOW = datetime.datetime.strptime(
    '2020-11-26 10:00:00', '%Y-%m-%d %H:%M:%S',
)


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('couriers-sync-periodic')
async def test_basic(
        taxi_grocery_supply, pgsql, mockserver, eats_core_integration,
):
    courier_id = '2701621'
    full_name = 'Самозанятый курьер'
    inn = '1234567890'
    billing_client_id = '1'
    transport_type = 'pedestrian'
    phone = '79999999999'
    billing_type = 'self_employed'
    eats_region_id = '194'

    eats_core_integration.set_courier_responses(
        [
            {
                'cursor': '1337',
                'profiles': [
                    {
                        'id': courier_id,
                        'full_name': full_name,
                        'first_name': 'Самозанят',
                        'surname': 'Самозанятов',
                        'patronymic': 'Самозанятович',
                        'country_id': '35',
                        'region_id': eats_region_id,
                        'courier_service_id': None,
                        'inn_pd_id': inn,
                        'billing_client_id': billing_client_id,
                        'billing_type': billing_type,
                        'transport_type': transport_type,
                        'phone_pd_id': phone,
                        'work_status': 'lost',
                        'orders_provider': 'eda',
                        'cursor': '0_1615278161_2701621',
                        'is_fixed_shifts_option_enabled': False,
                        'is_picker': False,
                        'is_storekeeper': False,
                        'is_dedicated_picker': False,
                        'is_dedicated_courier': False,
                        'is_rover': False,
                        'is_hard_of_hearing': False,
                        'has_health_card': False,
                        'has_terminal_for_payment_on_site': False,
                        'has_own_bicycle': False,
                        'birthday': None,
                        'gender': None,
                        'started_work_at': '2001-04-01T10:00:00+03:00',
                    },
                ],
            },
        ],
    )

    await taxi_grocery_supply.run_periodic_task('couriers-sync-periodic')

    assert eats_core_integration.courier_times_called() == 1

    cursor = pgsql['grocery_supply'].cursor()
    cursor.execute(
        """SELECT courier_id,
        full_name,
        courier_transport_type,
        courier_service_id,
        phone_id,
        inn_id,
        billing_client_id,
        billing_type,
        eats_region_id FROM supply.couriers;""",
    )

    couriers = cursor.fetchall()
    assert len(couriers) == 1

    courier = couriers[0]
    assert courier[0] == courier_id
    assert courier[1] == full_name
    assert courier[2] == transport_type
    assert courier[3] is None
    assert courier[4] == phone
    assert courier[5] == inn
    assert courier[6] == billing_client_id
    assert courier[7] == billing_type
    assert courier[8] == eats_region_id


@pytest.mark.config(GROCERY_SUPPLY_COURIERS_SYNC_BATCH_SIZE=1)
@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('couriers-sync-periodic')
async def test_several_calls_include_cursor(
        taxi_grocery_supply, pgsql, mockserver, eats_core_integration,
):
    await taxi_grocery_supply.invalidate_caches()
    courier_id = '2701621'
    full_name = 'Самозанятый курьер'
    inn = '1234567890'
    billing_client_id = '1'
    transport_type = 'pedestrian'
    phone = '79999999999'
    billing_type = 'self_employed'

    eats_core_integration.set_courier_responses(
        [
            {
                'cursor': '1337',
                'profiles': [
                    {
                        'id': courier_id,
                        'full_name': full_name,
                        'first_name': 'Самозанят',
                        'surname': 'Самозанятов',
                        'patronymic': 'Самозанятович',
                        'country_id': '35',
                        'region_id': '1',
                        'courier_service_id': None,
                        'inn_pd_id': inn,
                        'billing_client_id': billing_client_id,
                        'billing_type': billing_type,
                        'transport_type': transport_type,
                        'phone_pd_id': phone,
                        'work_status': 'lost',
                        'orders_provider': 'eda',
                        'cursor': '0_1615278161_2701621',
                        'is_fixed_shifts_option_enabled': False,
                        'is_picker': False,
                        'is_storekeeper': False,
                        'is_dedicated_picker': False,
                        'is_dedicated_courier': False,
                        'is_rover': False,
                        'is_hard_of_hearing': False,
                        'has_health_card': False,
                        'has_terminal_for_payment_on_site': False,
                        'has_own_bicycle': False,
                        'birthday': None,
                        'gender': None,
                        'started_work_at': '2001-04-01T10:00:00+03:00',
                    },
                ],
            },
            {'cursor': '1234', 'profiles': []},
        ],
    )

    await taxi_grocery_supply.run_periodic_task('couriers-sync-periodic')

    assert eats_core_integration.courier_times_called() == 2


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('couriers-sync-periodic')
async def test_cursor_is_saved(
        taxi_grocery_supply,
        pgsql,
        mockserver,
        mocked_time,
        eats_core_integration,
):
    await taxi_grocery_supply.invalidate_caches()
    courier_id = '2701621'
    full_name = 'Самозанятый курьер'
    inn = '1234567890'
    billing_client_id = '1'
    transport_type = 'pedestrian'
    phone = '79999999999'
    billing_type = 'self_employed'

    profile = {
        'id': courier_id,
        'full_name': full_name,
        'first_name': 'Самозанят',
        'surname': 'Самозанятов',
        'patronymic': 'Самозанятович',
        'country_id': '35',
        'region_id': '1',
        'courier_service_id': None,
        'inn_pd_id': inn,
        'billing_client_id': billing_client_id,
        'billing_type': billing_type,
        'transport_type': transport_type,
        'phone_pd_id': phone,
        'work_status': 'lost',
        'orders_provider': 'eda',
        'cursor': '0_1615278161_2701621',
        'is_fixed_shifts_option_enabled': False,
        'is_picker': False,
        'is_storekeeper': False,
        'is_dedicated_picker': False,
        'is_dedicated_courier': False,
        'is_rover': False,
        'is_hard_of_hearing': False,
        'has_health_card': False,
        'has_terminal_for_payment_on_site': False,
        'has_own_bicycle': False,
        'birthday': None,
        'gender': None,
        'started_work_at': '2001-04-01T10:00:00+03:00',
    }

    mocked_time.set(DATETIME_NOW)

    eats_core_integration.set_courier_responses(
        [{'cursor': '1337', 'profiles': [profile]}],
    )

    await taxi_grocery_supply.run_periodic_task('couriers-sync-periodic')

    mocked_time.set(DATETIME_NOW + datetime.timedelta(minutes=10))

    # remove when mocked time works
    db = pgsql['grocery_supply']
    cursor = db.cursor()
    cursor.execute('TRUNCATE TABLE supply.distlock_periodic_updates')

    eats_core_integration.set_expected_courier_cursor('1337')
    eats_core_integration.set_courier_responses(
        [{'cursor': '1337', 'profiles': [profile]}],
    )

    await taxi_grocery_supply.run_periodic_task('couriers-sync-periodic')
    assert eats_core_integration.courier_times_called() == 2

import datetime

import pytest


DATETIME_NOW = datetime.datetime.strptime(
    '2020-11-26 10:00:00', '%Y-%m-%d %H:%M:%S',
)


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('courier-services-sync-periodic')
async def test_basic(taxi_grocery_supply, pgsql, eats_core_integration):
    courier_service_id = 127
    name = 'ООО ЦементТелеком'
    address = '039962, Оренбургская область, город Истра, наб. Сталина, 08'
    ogrn = '5177746048915'
    work_schedule = 'пн-пт с 10:00 до 18:00 время Московское'
    inn = '9721055933'
    vat = 20
    billing_client_id = 'wh21ish821'

    eats_core_integration.set_courier_service_responses(
        [
            {
                'cursor': '1337',
                'collection': [
                    {
                        'id': courier_service_id,
                        'name': name,
                        'address': address,
                        'ogrn': ogrn,
                        'work_schedule': work_schedule,
                        'inn': inn,
                        'vat': vat,
                        'billing_client_id': billing_client_id,
                        'commissions': {
                            'commission': '0.0',
                            'marketing_commission': '0.0',
                        },
                        'available_billing_types': ['courier_service'],
                    },
                ],
            },
        ],
    )

    await taxi_grocery_supply.run_periodic_task(
        'courier-services-sync-periodic',
    )

    assert eats_core_integration.courier_service_times_called() == 1

    cursor = pgsql['grocery_supply'].cursor()
    cursor.execute(
        """SELECT courier_service_id,
            name,
            address,
            ogrn,
            work_schedule,
            inn,
            vat,
            billing_client_id FROM supply.courier_services;""",
    )

    courier_services = cursor.fetchall()
    assert len(courier_services) == 1

    service = courier_services[0]
    assert service[0] == courier_service_id
    assert service[1] == name
    assert service[2] == address
    assert service[3] == ogrn
    assert service[4] == work_schedule
    assert service[5] == inn
    assert service[6] == vat
    assert service[7] == billing_client_id


@pytest.mark.config(GROCERY_SUPPLY_COURIER_SERVICES_SYNC_BATCH_SIZE=1)
@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('courier-services-sync-periodic')
async def test_several_calls_include_cursor(
        taxi_grocery_supply, pgsql, eats_core_integration,
):
    await taxi_grocery_supply.invalidate_caches()
    courier_service_id = 127
    name = 'ООО ЦементТелеком'
    address = '039962, Оренбургская область, город Истра, наб. Сталина, 08'
    ogrn = '5177746048915'
    work_schedule = 'пн-пт с 10:00 до 18:00 время Московское'
    inn = '9721055933'
    vat = 20
    billing_client_id = 'wh21ish821'

    eats_core_integration.set_courier_service_responses(
        [
            {
                'cursor': '1337',
                'collection': [
                    {
                        'id': courier_service_id,
                        'name': name,
                        'address': address,
                        'ogrn': ogrn,
                        'work_schedule': work_schedule,
                        'inn': inn,
                        'vat': vat,
                        'billing_client_id': billing_client_id,
                        'commissions': {
                            'commission': '0.0',
                            'marketing_commission': '0.0',
                        },
                        'available_billing_types': ['courier_service'],
                    },
                ],
            },
            {'cursor': '1234', 'collection': []},
        ],
    )

    await taxi_grocery_supply.run_periodic_task(
        'courier-services-sync-periodic',
    )

    assert eats_core_integration.courier_service_times_called() == 2


@pytest.mark.pgsql('grocery_supply', files=[])
@pytest.mark.suspend_periodic_tasks('courier-services-sync-periodic')
async def test_cursor_is_saved(
        taxi_grocery_supply, pgsql, mocked_time, eats_core_integration,
):
    await taxi_grocery_supply.invalidate_caches()
    courier_service_id = 127
    name = 'ООО ЦементТелеком'
    address = '039962, Оренбургская область, город Истра, наб. Сталина, 08'
    ogrn = '5177746048915'
    work_schedule = 'пн-пт с 10:00 до 18:00 время Московское'
    inn = '9721055933'
    vat = 20
    billing_client_id = 'wh21ish821'

    service = {
        'id': courier_service_id,
        'name': name,
        'address': address,
        'ogrn': ogrn,
        'work_schedule': work_schedule,
        'inn': inn,
        'vat': vat,
        'billing_client_id': billing_client_id,
        'commissions': {'commission': '0.0', 'marketing_commission': '0.0'},
        'available_billing_types': ['courier_service'],
    }

    mocked_time.set(DATETIME_NOW)

    eats_core_integration.set_courier_service_responses(
        [{'cursor': '1337', 'collection': [service]}],
    )

    await taxi_grocery_supply.run_periodic_task(
        'courier-services-sync-periodic',
    )

    mocked_time.set(DATETIME_NOW + datetime.timedelta(minutes=10))

    # remove when mocked time works
    db = pgsql['grocery_supply']
    cursor = db.cursor()
    cursor.execute('TRUNCATE TABLE supply.distlock_periodic_updates')

    eats_core_integration.set_courier_service_cursor('1337')
    eats_core_integration.set_courier_service_responses(
        [{'cursor': '1337', 'collection': [service]}],
    )

    await taxi_grocery_supply.run_periodic_task(
        'courier-services-sync-periodic',
    )
    assert eats_core_integration.courier_service_times_called() == 2

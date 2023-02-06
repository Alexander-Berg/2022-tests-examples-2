import datetime as dt
import decimal
import json
import typing as tp

import pytest

from fleet_rent.entities import driver as driver_entities
from fleet_rent.entities import rent as rent_entities
from fleet_rent.services import billing_reports


@pytest.fixture(name='common_patches')
def _common_patches(patch, park_stub_factory, mock_fleet_vehicles):
    @patch('fleet_rent.services.park_info.ParkInfoService.get_park_info')
    async def _get_park_info(park_id: str):
        assert park_id == 'park_id'
        return park_stub_factory(
            id=park_id, tz_offset=5, locale='ru', clid='clid_second',
        )

    @patch(
        'fleet_rent.services.driver_info.DriverInfoService.get_drivers_info',
    )
    async def _get_drivers_info(park_id: str, driver_ids):
        assert park_id == 'park_id'
        assert sorted(driver_ids) == ['park_driver_id']
        return [
            driver_entities.Driver(
                id='park_driver_id',
                park_id=park_id,
                full_name=driver_entities.Driver.FullName(
                    first_name='Хелло', last_name=None, middle_name='Вордович',
                ),
            ),
        ]

    @patch(
        'fleet_rent.components.currency_provider.'
        'CurrencyProvider.get_park_external_currency',
    )
    async def _get_park_external_currency(park_id: str, at_moment):
        assert park_id == 'park_id'
        return 'RUB'

    @mock_fleet_vehicles('/v1/vehicles/cache-retrieve')
    async def _v1_vehicles_retrieve(request):
        assert request.json == {'id_in_set': ['park_id_car_id1']}
        return {
            'vehicles': [
                {
                    'park_id_car_id': 'park_id_car_id1',
                    'data': {
                        'park_id': 'park_id',
                        'car_id': 'car_id1',
                        'number': '12345678',
                        'brand': 'BMV',
                        'model': 'X5',
                    },
                },
            ],
        }


@pytest.mark.now('2020-01-02T00:00+00:00')
@pytest.mark.pgsql('fleet_rent', files=['init_db.sql'])
@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'rents_terminate_on_clid_change_title': {
            'ru': 'Завершены списания из-за смены договора',
        },
        'rents_terminate_on_clid_change_text': {
            'ru': 'Периодические списания заверешны в связи со сменой договора.\nTаблица:\n{table}',  # noqa: E501
        },
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
async def test_basic_case(
        cron_context, common_patches, patch, mock_fleet_notifications,
):
    @patch(
        'fleet_rent.services.billing_reports.'
        'BillingReportsService.get_balances_by_rent',
    )
    async def _get_balances_by_rent(
            currency: str,
            rents: tp.Collection[rent_entities.Rent],
            now: dt.datetime,
    ):
        assert {x.record_id for x in rents} == {
            'rent_id1',
            'rent_id2',
            'rent_id3',
        }
        assert currency == 'RUB'
        return {
            'rent_id1': billing_reports.BalancesBySubaccount(
                withdraw=decimal.Decimal(10),
                withhold=decimal.Decimal(20),
                cancel=decimal.Decimal(5),
            ),
            'rent_id2': billing_reports.BalancesBySubaccount(
                withdraw=decimal.Decimal(10),
                withhold=decimal.Decimal(20),
                cancel=decimal.Decimal(10),
            ),
            'rent_id3': billing_reports.BalancesBySubaccount(
                withdraw=decimal.Decimal(20),
                withhold=decimal.Decimal(20),
                cancel=decimal.Decimal(0),
            ),
        }

    notifications = []

    @mock_fleet_notifications('/v1/notifications/create')
    async def _handle_notification(request):
        jss = request.json
        notifications.append(jss)
        return {}

    ucs = cron_context.use_cases.park_clid_change_react
    await ucs.check_all_rents()

    for notification in notifications:
        assert notification.pop('request_id')
    assert notifications == [
        {
            'destinations': [{'park_id': 'park_id'}],
            'payload': {
                'entity': {'type': 'fleet-rent/rent-termination-clid'},
                'text': (
                    'Периодические списания заверешны '
                    'в связи со сменой договора.\n'
                    'Tаблица:\n'
                    '№1 Хелло Вордович BMV X5 12345678 5.00;\n'
                    '№2 Хелло Вордович BMV X5 12345678 0.00;\n'
                    '№3 Хелло Вордович BMV X5 12345678 0.00;'
                ),
                'title': 'Завершены списания из-за смены договора',
            },
        },
    ]

    async with cron_context.pg.master.acquire() as conn:
        await conn.set_type_codec(
            'jsonb',
            decoder=json.loads,
            encoder=lambda x: json.dumps(x, ensure_ascii=False),
            schema='pg_catalog',
        )

        rows = await conn.fetch(
            """SELECT record_id,
             terminated_at_tz IS NOT NULL AS is_terminated
            FROM rent.records ORDER BY record_id""",
        )
        dicts = [dict(r) for r in rows]
        assert dicts == [
            {'record_id': 'rent_id1', 'is_terminated': True},
            {'record_id': 'rent_id2', 'is_terminated': True},
            {'record_id': 'rent_id3', 'is_terminated': True},
            {'record_id': 'rent_id4', 'is_terminated': False},
            {'record_id': 'rent_id5', 'is_terminated': False},
            {'record_id': 'rent_id6', 'is_terminated': False},
        ]

        rows = await conn.fetch(
            """SELECT rent_id, event_number
            FROM rent.event_queue ORDER BY rent_id, event_number""",
        )
        dicts = [dict(r) for r in rows]
        assert dicts == [
            {'event_number': 1, 'rent_id': 'rent_id1'},
            {'event_number': 1, 'rent_id': 'rent_id3'},
            {'event_number': 1, 'rent_id': 'rent_id4'},
            {'event_number': 1, 'rent_id': 'rent_id5'},
            {'event_number': 1, 'rent_id': 'rent_id6'},
        ]

        rows = await conn.fetch(
            """SELECT rent_id, event_number
            FROM rent.active_day_start_triggers
             ORDER BY rent_id, event_number""",
        )
        dicts = [dict(**r) for r in rows]
        assert dicts == [{'event_number': 1, 'rent_id': 'rent_id3'}]

        rows = await conn.fetch(
            """SELECT record_id,
                    payment_doc_ids,
                    is_complete,
                    created_by_json
            FROM rent.external_debt_cancellations
            ORDER BY record_id""",
        )
        dicts = [dict(r) for r in rows]
        assert dicts == [
            {
                'created_by_json': {'kind': 'platform'},
                'is_complete': False,
                'payment_doc_ids': [],
                'record_id': 'rent_id1',
            },
        ]

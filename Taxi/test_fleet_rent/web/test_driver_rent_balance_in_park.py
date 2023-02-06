import datetime
import decimal

import pytest

from fleet_rent.entities import balance
from fleet_rent.entities import park
from fleet_rent.generated.web import web_context as wc
from fleet_rent.use_cases import driver_balance_in_park


@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'Will be withheld automatically': {
            'ru': 'Будет удержано автоматически',
        },
        '"Will be withheld" explanation': {
            'ru': (
                'Текст, который говорит, что ты торчишь парку по безналу '
                'и мы удержим то, что должно.'
            ),
        },
        'driver_internal_park_balance_negative': {
            'ru': 'Вы должны парку наличными',
        },
        'driver_internal_park_balance_positive': {
            'ru': 'Парк должен вам наличными',
        },
        'Park "{park_name}"': {'ru': 'Парк "{park_name}"'},
        'rent_name': {'ru': 'Списание №{id}'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
@pytest.mark.now('2020-02-01T12:00:00')
async def test_balance_in_park(
        web_app_client,
        web_context: wc.Context,
        driver_auth_headers,
        patch,
        rent_stub_factory,
):
    @patch('fleet_rent.use_cases.driver_balance_in_park.get_data')
    async def _get_balances(
            context, park_id: str, driver_id: str, driver_park_id: str,
    ):
        assert park_id == 'park_id'
        assert driver_id == 'driver_id'
        assert driver_park_id == 'driver_park_id'
        _stub_dt = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
        internal = decimal.Decimal(-200.9999)
        balances = [
            balance.RentBalance(
                rent=rent_stub_factory(
                    record_id='record_id1',
                    owner_serial_id=9,
                    affiliation_id='affiliation_id',
                    accepted_at=_stub_dt,
                ),
                balance=decimal.Decimal(-400),
            ),
            balance.RentBalance(
                rent=rent_stub_factory(
                    record_id='record_id2',
                    owner_serial_id=113,
                    affiliation_id='affiliation_id',
                    accepted_at=_stub_dt,
                ),
                balance=decimal.Decimal(-200),
            ),
        ]
        return driver_balance_in_park.DriverBalanceInParkData(
            currency='RUB',
            park_info=park.Park(id=park_id, name='Агент 666'),
            balance_internal=internal,
            balance_by_rent=balances,
        )

    @patch(
        'fleet_rent.pg_access.affiliation.'
        'DriverAffiliationAccessor.is_driver_affiliated',
    )
    async def _is_driver_affiliated(
            park_id: str, original_driver_id: str, original_park_id: str,
    ) -> bool:
        assert park_id == 'park_id'
        assert original_driver_id == 'driver_id'
        assert original_park_id == 'driver_park_id'
        return True

    response = await web_app_client.get(
        '/driver/v1/periodic-payments/balance/in-park',
        headers=driver_auth_headers,
        params={'rent_park_id': 'park_id'},
    )
    assert response.status == 200

    data = await response.json()

    assert data == {
        'title': 'Парк "Агент 666"',
        'items': [
            {
                'horizontal_divider_type': 'none',
                'subtitle': '-600,<small>00</small> <small>₽</small>',
                'title': 'Будет удержано автоматически',
                'type': 'header',
                'html': True,
            },
            {
                'horizontal_divider_type': 'bottom_gap',
                'title': (
                    'Текст, который говорит, что ты торчишь парку по безналу '
                    'и мы удержим то, что должно.'
                ),
                'type': 'detail',
            },
            {
                'detail': '-200,<small>99</small> <small>₽</small>',
                'horizontal_divider_type': 'none',
                'title': 'Вы должны парку наличными',
                'type': 'detail',
                'html': True,
            },
            {'type': 'title'},
            {
                'detail': '-400,<small>00</small> <small>₽</small>',
                'horizontal_divider_type': 'bottom_gap',
                'payload': {
                    'rent_id': 'record_id1',
                    'type': 'navigate_rent_details',
                },
                'right_icon': 'navigate',
                'title': 'Списание №9',
                'type': 'detail',
                'html': True,
            },
            {
                'detail': '-200,<small>00</small> <small>₽</small>',
                'horizontal_divider_type': 'none',
                'payload': {
                    'rent_id': 'record_id2',
                    'type': 'navigate_rent_details',
                },
                'right_icon': 'navigate',
                'title': 'Списание №113',
                'type': 'detail',
                'html': True,
            },
        ],
    }


@pytest.mark.now('2020-02-01T12:00:00')
async def test_balance_in_park_without_park(
        web_app_client,
        web_context: wc.Context,
        driver_auth_headers,
        patch,
        rent_stub_factory,
):
    response = await web_app_client.get(
        '/driver/v1/periodic-payments/balance/in-park',
        headers=driver_auth_headers,
        params={'rent_park_id': 'park_id'},
    )
    assert response.status == 409

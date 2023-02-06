import datetime
import decimal

import pytest

from fleet_rent.entities import asset as asset_ent
from fleet_rent.entities import charging as charging_ent
from fleet_rent.entities import daily_periodicity as dp_ent
from fleet_rent.use_cases import driver_rent_details


@pytest.mark.config(
    FLEET_RENT_DRIVER_PERIODIC_PAYMENT_DETAILS={
        'additional_info_url': 'yandex.ru',
    },
)
@pytest.mark.translations(
    taximeter_backend_fleet_rent={
        'rent_name': {'ru': 'Списание {id}'},
        'rent_additional_info': {'ru': 'см. [сюда]({url})'},
        'rent_charging_daily': {
            'ru': 'Списания {periodicity}; в {time_of_day}',
        },
        'rent_charging_daily_fraction': {'ru': 'по периоду {n}/{d}'},
        'rent_charging_daily_isoweekdays': {'ru': 'по дням недели: {days}'},
        'rent_charging_daily_monthdays': {'ru': 'по дням месяца: {days}'},
        'isoweekdays': {'ru': 'пн,вт,ср,чт,пт,сб,вс'},
        'rent_asset_car': {'ru': '{model} {brand} {number}'},
        'Park name': {'ru': 'Название парка'},
        'Park owner': {'ru': 'Владелец парка'},
        'Park contacts': {'ru': 'Контактная информация парка'},
        'Order begins at': {'ru': 'Договор вступает в силу'},
        'Order ends at': {'ru': 'Договор действителен до'},
        'First charge': {'ru': 'Первое списание'},
        'Charging schedule': {'ru': 'Правила списаний'},
        'Additional information': {'ru': 'Дополнительная информация'},
        'Daily price': {'ru': 'Дневная стоимость'},
        'park_full_name': {'ru': '{park_name} ({park_legal_name})'},
    },
    tariff={
        'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'},
        'currency_sign.rub': {'ru': '₽'},
    },
    cities={'Москва': {'ru': 'Москва'}},
)
@pytest.mark.now('2020-02-01T12:00:00')
async def test_details(
        web_app_client,
        driver_auth_headers,
        patch,
        aff_stub_factory,
        rent_stub_factory,
        car_stub_factory,
        park_stub_factory,
        park_billing_data_stub_factory,
        park_contacts_stub_factory,
        load_json,
):
    @patch(
        'fleet_rent.use_cases.driver_rent_details.'
        'DriverRentDetails.get_rent_details',
    )
    async def _get_data(rent_id, driver_id, driver_park_id, now):
        if rent_id == 'bad_id':
            raise driver_rent_details.NotFound()
        aff = aff_stub_factory()
        asset = asset_ent.AssetCar('car_id', None)
        return driver_rent_details.Result(
            affiliation=aff,
            rent=rent_stub_factory(
                affiliation_id=aff.record_id,
                asset=asset,
                charging=charging_ent.ChargingDaily(
                    starts_at=datetime.datetime(
                        2020, 1, 2, tzinfo=datetime.timezone.utc,
                    ),
                    finishes_at=datetime.datetime(
                        2020, 1, 31, tzinfo=datetime.timezone.utc,
                    ),
                    total_withhold_limit=None,
                    daily_price=decimal.Decimal(100),
                    periodicity=dp_ent.DailyPeriodicityISOWeekDays([2, 4, 6]),
                    time=datetime.time(0, 0),
                ),
                charging_starts_at=datetime.datetime(
                    2020, 1, 2, tzinfo=datetime.timezone.utc,
                ),
                ends_at=datetime.datetime(
                    2020, 1, 31, tzinfo=datetime.timezone.utc,
                ),
            ),
            asset_data=driver_rent_details.AssetDataCar(
                car_data=car_stub_factory(), asset=asset,
            ),
            driver_park=park_stub_factory(id=driver_park_id),
            driver_currency='RUB',
            owner_park=park_stub_factory(id='park_id', owner=None),
            owner_park_billing=park_billing_data_stub_factory(
                legal_name='ООО ИмяПарка',
            ),
            owner_park_contacts=park_contacts_stub_factory(phone=None),
        )

    response404 = await web_app_client.get(
        '/driver/v1/periodic-payments/rent/details',
        params={'rent_id': 'bad_id'},
        headers=driver_auth_headers,
    )
    assert response404.status == 404

    response200 = await web_app_client.get(
        '/driver/v1/periodic-payments/rent/details',
        params={'rent_id': 'record_id'},
        headers=driver_auth_headers,
    )
    assert response200.status == 200

    data = await response200.json()

    assert data == load_json('ok.json')

import pytest


@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            [
                'begins_at',
                'ends_at',
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.daily_price',
                'charging.time',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql('fleet_rent', files=['test_simple.sql']),
                pytest.mark.now('2019-12-31 05:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'ends_at',
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.daily_price',
                'charging.time',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql('fleet_rent', files=['test_simple.sql']),
                pytest.mark.now('2020-01-03 05:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'ends_at',
                'title',
                'comment',
                'charging.daily_price',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql(
                    'fleet_rent',
                    files=['test_simple.sql'],
                    queries=[
                        """
                        UPDATE rent.records
                        SET charging_type = 'active_days',
                            charging_params = '{"daily_price": "100"}'
                        WHERE record_id = 'basic_rent_id'
                        """,
                    ],
                ),
                pytest.mark.now('2020-01-03 05:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'ends_at',
                'title',
                'comment',
                'charging.type',
                'charging.daily_price',
                'charging.time',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql(
                    'fleet_rent',
                    files=['test_simple.sql'],
                    queries=[
                        """
                        UPDATE rent.records
                        SET charging_params =
                            '{"daily_price": "100", "time":"12:00",
                            "periodicity":
                                {"type": "fraction", "params":
                                    {"numerator": 5, "denominator": 7}}}'
                        WHERE record_id = 'basic_rent_id'
                        """,
                    ],
                ),
                pytest.mark.now('2020-01-03 05:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'ends_at',
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.time',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql(
                    'fleet_rent',
                    files=['test_simple.sql'],
                    queries=[
                        """
                        UPDATE rent.records
                        SET asset_params = '{"subtype": "deposit"}',
                            charging_params =
                                '{"daily_price": "100", "time":"12:00",
                                "periodicity":
                                    {"type": "constant", "params": null},
                                    "total_withhold_limit": "500.00"}'
                        WHERE record_id = 'basic_rent_id'
                        """,
                    ],
                ),
                pytest.mark.now('2020-01-03 05:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'ends_at',
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.daily_price',
                'charging.time',
                'asset.car_id',
                'asset.car_copy_id',
            ],
            marks=[
                pytest.mark.pgsql(
                    'fleet_rent',
                    files=['test_simple.sql'],
                    queries=[
                        """
                        UPDATE rent.records
                        SET asset_type = 'car',
                            asset_params = '{"car_id": "belaz"}'
                        WHERE record_id = 'basic_rent_id'
                       """,
                    ],
                ),
                pytest.mark.now('2020-01-03 05:00+00:00'),
            ],
        ),
        pytest.param(
            [],
            marks=[
                pytest.mark.pgsql('fleet_rent', files=['test_simple.sql']),
                pytest.mark.now('2021-01-03 05:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.daily_price',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql('fleet_rent', files=['test_simple.sql']),
                pytest.mark.now('2020-01-03 8:00+00:00'),
            ],
        ),
        pytest.param(
            [
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.daily_price',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql('fleet_rent', files=['test_simple.sql']),
                pytest.mark.now('2020-01-03 6:58+00:00'),
            ],
        ),
        pytest.param(
            [
                'title',
                'comment',
                'charging.periodicity.type',
                'charging.periodicity.isoweekdays',
                'charging.periodicity.monthdays',
                'charging.type',
                'charging.daily_price',
                'asset.description',
            ],
            marks=[
                pytest.mark.pgsql(
                    'fleet_rent',
                    files=['test_simple.sql'],
                    queries=[
                        """
                        UPDATE rent.records
                        SET begins_at_tz = '2020-01-03 12:00+05'
                        WHERE record_id = 'basic_rent_id'
                        """,
                    ],
                ),
                pytest.mark.now('2020-01-03 6:58+00:00'),
            ],
        ),
    ],
    ids=[
        'not_began',
        'began',
        'active_days',
        'fraction_periodicity',
        'deposit',
        'car',
        'ended',
        'previous_event_not_finished',
        'next_event_soon',
        'first_event_soon',
    ],
)
async def test_ok(web_app_client, driver_auth_headers, expected):
    response = await web_app_client.get(
        '/fleet/rent/v1/park/rents/modifiable-fields?rent_id=basic_rent_id',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': 'park_id5',
            'X-Real-IP': '127.0.0.1',
        },
    )

    assert response.status == 200, await response.text()
    assert await response.json() == {'modifiable_fields': sorted(expected)}


@pytest.mark.pgsql('fleet_rent', files=['test_simple.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_404_wrong_park(web_app_client, driver_auth_headers):
    response = await web_app_client.get(
        '/fleet/rent/v1/park/rents/modifiable-fields?rent_id=basic_rent_id',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': 'park_id4',
            'X-Real-IP': '127.0.0.1',
        },
    )
    assert response.status == 404


@pytest.mark.pgsql('fleet_rent', files=['test_simple.sql'])
@pytest.mark.now('2020-01-03 05:00+00:00')
async def test_404_wrong_id(web_app_client, driver_auth_headers):
    response = await web_app_client.get(
        '/fleet/rent/v1/park/rents/modifiable-fields?rent_id=basic_rent_id2',
        headers={
            'Accept-Language': 'ru',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-Login': 'abacaba',
            'X-Yandex-UID': '123',
            'X-Park-Id': 'park_id5',
            'X-Real-IP': '127.0.0.1',
        },
    )
    assert response.status == 404

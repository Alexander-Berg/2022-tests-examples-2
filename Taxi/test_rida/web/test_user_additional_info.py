import datetime

import pytest

from test_rida import experiments_utils
from test_rida import helpers


_NOW = datetime.datetime(2021, 1, 1, tzinfo=datetime.timezone.utc)
_TARIFF_TRANSLATIONS = {
    'currency.ngn': {'en': 'NGN'},
    'currency_with_sign.default': {'en': '$VALUE$ $SIGN$$CURRENCY$'},
}


async def _check_additional_info(
        response,
        should_see_info: bool,
        drivers_near: str = '1',
        should_see_route_info: bool = True,
):
    assert response.status == 200
    offer = (await response.json())['data']['offer']
    if not should_see_info:
        assert 'additional_info' not in offer
    else:
        expected = [
            {
                'type': 2,
                'data': {
                    'key': {'text': 'Drivers near:', 'color': '#000000'},
                    'value': {'text': drivers_near, 'color': '#000000'},
                },
            },
        ]
        if should_see_route_info:
            expected += [
                {
                    'type': 2,
                    'data': {
                        'key': {'text': 'Cena', 'color': '#000000'},
                        'value': {'text': '36 NGN', 'color': '#000000'},
                    },
                },
                {
                    'type': 2,
                    'data': {
                        'key': {'text': 'Skolko ehat', 'color': '#000000'},
                        'value': {'text': '322 min', 'color': '#000000'},
                    },
                },
            ]
        expected.append({'type': 101, 'data': {}})
        additional_info = offer['additional_info']
        assert additional_info == expected


async def _check_user_info_additional_info(
        web_app_client,
        headers,
        offer_guid: str,
        should_see_info: bool,
        drivers_near: str = '1',
        should_see_route_info: bool = True,
):
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    await _check_additional_info(
        response, should_see_info, drivers_near, should_see_route_info,
    )


async def _create_offer(
        web_app_client,
        headers,
        offer_guid: str,
        lat: float = 40.2185869,
        lon: float = 44.580287,
):
    return await helpers.create_offer(
        web_app_client,
        headers,
        offer_guid=offer_guid,
        point_a_lat=lat,
        point_a_long=lon,
        country_id=2,
        direction_duration_ts=19320,
        zone_id=0,
    )


async def _bid_place(web_app_client, offer_guid: str):
    driver_headers = helpers.get_auth_headers(user_id=1449)
    response = await web_app_client.post(
        '/v3/driver/bid/place',
        headers=driver_headers,
        json={
            'bid_guid': 'bid_guid',
            'offer_guid': offer_guid,
            'proposed_price': 500,
        },
    )
    assert response.status == 200


async def _bid_cancel(web_app_client):
    driver_headers = helpers.get_auth_headers(user_id=1449)
    response = await web_app_client.post(
        '/v3/driver/bid/cancel',
        headers=driver_headers,
        json={'bid_guid': 'bid_guid'},
    )
    assert response.status == 200


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'offer_status, should_see_additional_info',
    [('PENDING', True), ('FINISHED', False)],
)
@experiments_utils.get_offer_info_units(
    [
        {
            'key': {'tanker_key': 'user_offer_info.drivers_near.key'},
            'value': {'tanker_key': 'user_offer_info.drivers_near.value'},
        },
        {
            'key': {'tanker_key': 'user_offer_info.price.key'},
            'value': {'tanker_key': 'user_offer_info.price.value'},
        },
        {
            'key': {
                'tanker_key': 'user_offer_info.start_to_finish_duration.key',
            },
            'value': {
                'tanker_key': 'user_offer_info.start_to_finish_duration.value',
            },
        },
    ],
    consumer='user',
)
@pytest.mark.translations(
    rida={
        'user_offer_info.drivers_near.key': {'en': 'Drivers near:'},
        'user_offer_info.drivers_near.value': {'en': '{count_drivers_near}'},
        'user_offer_info.price.key': {'en': 'Cena'},
        'user_offer_info.price.value': {'en': '{price_with_currency}'},
        'user_offer_info.start_to_finish_duration.key': {'en': 'Skolko ehat'},
        'user_offer_info.start_to_finish_duration.value': {
            'en': '{start_to_finish_duration}',
        },
    },
    tariff=_TARIFF_TRANSLATIONS,
)
async def test_offer_info_count_drivers_near(
        web_app_client,
        mongodb,
        offer_status: str,
        should_see_additional_info: bool,
):
    headers = helpers.get_auth_headers(user_id=1234)
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K'
    response = await _create_offer(web_app_client, headers, offer_guid)
    await _check_additional_info(response, True)
    mongodb.rida_offers.update({}, {'$set': {'offer_status': offer_status}})
    await _check_user_info_additional_info(
        web_app_client,
        headers,
        offer_guid,
        should_see_info=should_see_additional_info,
    )

    # if offer is not pending, passenger cant change the price
    if offer_status != 'PENDING':
        return

    request_body = {'offer_guid': offer_guid, 'initial_price': 35.5}
    headers['Content-Type'] = 'application/json'
    response = await web_app_client.post(
        '/v1/offer/priceChange', json=request_body, headers=headers,
    )
    await _check_additional_info(response, True)

    await _bid_place(web_app_client, offer_guid)
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    await _check_additional_info(response, should_see_additional_info)

    await _bid_cancel(web_app_client)
    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    await _check_additional_info(response, should_see_additional_info)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.client_experiments3(
    consumer='rida',
    experiment_name='rida_drivers_near_passenger',
    args=experiments_utils.get_default_user_args(),
    value={
        'rules': [
            {
                'info': [
                    {
                        'key': {
                            'tanker_key': 'user_offer_info.drivers_near.key',
                        },
                        'value': {
                            'tanker_key': (
                                'user_offer_info.drivers_near.few.value'
                            ),
                        },
                    },
                ],
                'count_greater_than_or_equal': 0,
                'count_less_than': 1,
            },
            {
                'info': [
                    {
                        'key': {
                            'tanker_key': 'user_offer_info.drivers_near.key',
                        },
                        'value': {
                            'tanker_key': (
                                'user_offer_info.drivers_near.ok.value'
                            ),
                        },
                    },
                ],
                'count_greater_than_or_equal': 1,
                'count_less_than': 2,
            },
            {
                'info': [
                    {
                        'key': {
                            'tanker_key': 'user_offer_info.drivers_near.key',
                        },
                        'value': {
                            'tanker_key': (
                                'user_offer_info.drivers_near.many.value'
                            ),
                        },
                    },
                ],
                'count_greater_than_or_equal': 2,
                'count_less_than': 3,
            },
        ],
    },
)
@pytest.mark.translations(
    rida={
        'user_offer_info.drivers_near.key': {'en': 'Drivers near:'},
        'user_offer_info.drivers_near.few.value': {'en': 'Malo'},
        'user_offer_info.drivers_near.ok.value': {'en': 'Normalno'},
        'user_offer_info.drivers_near.many.value': {'en': 'Mnogo'},
    },
    tariff=_TARIFF_TRANSLATIONS,
)
async def test_offer_info_count_drivers_near_approximately(web_app_client):
    headers = helpers.get_auth_headers(user_id=1234)
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K'
    await _create_offer(web_app_client, headers, offer_guid, lat=1, lon=1)
    await _check_user_info_additional_info(
        web_app_client,
        headers,
        offer_guid,
        should_see_info=True,
        should_see_route_info=False,
        drivers_near='Malo',
    )

    for i, driver_user_id in enumerate([5678, 1449]):
        driver_headers = helpers.get_auth_headers(user_id=driver_user_id)
        response = await web_app_client.post(
            '/v3/driver/position',
            headers=driver_headers,
            json={'position': [1, 1], 'heading': 1.234},
        )
        assert response.status == 200
        drivers_near = 'Normalno' if i == 0 else 'Mnogo'
        await _check_user_info_additional_info(
            web_app_client,
            headers,
            offer_guid,
            should_see_info=True,
            should_see_route_info=False,
            drivers_near=drivers_near,
        )


@pytest.mark.now(_NOW.isoformat())
@experiments_utils.get_sequential_offers_exp(
    '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
    value={'enabled': True, 'repeated_offers': {'enabled': True}},
)
@experiments_utils.get_offer_info_units(
    [
        {
            'key': {'tanker_key': 'user_offer_info.drivers_seen.key'},
            'value': {'tanker_key': 'user_offer_info.drivers_seen.value'},
        },
    ],
    consumer='user',
)
@pytest.mark.translations(
    rida={
        'user_offer_info.drivers_seen.key': {'en': 'Drivers seen:'},
        'user_offer_info.drivers_seen.value': {'en': '{count_drivers_seen}'},
    },
    tariff=_TARIFF_TRANSLATIONS,
)
@experiments_utils.get_distance_info_config(
    'ruler',
    'v3/driver/offer/nearest',
    user_guid='9373F48B-C6B4-4812-A2D0-413F3AFBAD5E',
)
async def test_seen_by_drivers_additional_info(web_app_client):
    def get_expected_additional_info(seen_by_count: int):
        return [
            {
                'type': 2,
                'data': {
                    'key': {'text': 'Drivers seen:', 'color': '#000000'},
                    'value': {'text': str(seen_by_count), 'color': '#000000'},
                },
            },
            {'type': 101, 'data': {}},
        ]

    headers = helpers.get_auth_headers(user_id=1234)
    offer_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5K'
    await _create_offer(web_app_client, headers, offer_guid)

    response = await web_app_client.post(
        '/v3/user/offer/info',
        headers=headers,
        json={'offer_guid': offer_guid},
    )
    assert response.status == 200
    additional_info = (await response.json())['data']['offer'][
        'additional_info'
    ]
    assert additional_info == get_expected_additional_info(0)

    for i, driver_user_id in enumerate([5678, 1449]):
        driver_headers = helpers.get_auth_headers(user_id=driver_user_id)
        for _ in range(2):
            response = await web_app_client.post(
                '/v3/driver/offer/info',
                headers=driver_headers,
                json={'offer_guid': offer_guid},
            )
            assert response.status == 200
            response = await web_app_client.post(
                '/v3/user/offer/info',
                headers=headers,
                json={'offer_guid': offer_guid},
            )
            additional_info = (await response.json())['data']['offer'][
                'additional_info'
            ]
            assert additional_info == get_expected_additional_info(i + 1)

import copy
import typing
import urllib

import pytest

from tests_contractor_merch import util


PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'

HEADERS = util.get_headers(
    PARK_ID, DRIVER_ID, {'X-Selection-Id': 'selection_id_1'},
)

MUTABLE = 'by-offer-id'
IMMUTABLE = 'by-immutable-id'
FETCH_BY_IDS = {
    MUTABLE: '/feeds/v1/fetch_by_id',
    IMMUTABLE: '/feeds/v1/fetch_by_package_id',
}
HANDLERS_BY_IDS = {
    MUTABLE: '/driver/v1/contractor-merch/v1/offer/feed-id-1',
    IMMUTABLE: (
        '/driver/v1/contractor-merch/v1/'
        'offer-by-immutable-id/feeds-admin-id-1'
    ),
}

TRANSLATIONS = {
    'list_v1.title': {'en': 'Title'},
    'list_v1.subtitle': {'en': 'Subtitle'},
    'category.tire': {'en': 'Tires and so'},
    'category.washing': {'en': 'Washing and so'},
    'category.washing.slider': {'en': 'WASH-WASH-WASH'},
    **util.ERROR_TRANSLATIONS,
}
CUSTOM_TRANSLATIONS = util.CUSTOM_MESSAGES_TRANSLATIONS

EXPECTED_OFFER: typing.Dict[str, typing.Any] = {
    'category_id': 'tire',
    'category_ids': ['tire', 'food'],
    'immutable_offer_id': 'feeds-admin-id-1',
    'offer_data': {
        'offer_id': 'metric',
        'category': 'tire',
        'categories': ['tire', 'food'],
        'name': 'RRRR',
        'partner': {'name': 'Apple'},
        'price': '200.0000',
        'price_with_currency': {
            'value': '200',
            'currency': 'RUB',
            'formatted': '200 ₽',
        },
        'balance_payment': True,
        'title': 'Title',
        'actions': [
            {
                'type': 'link',
                'text': 'Rick Astley',
                'data': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            },
        ],
        'place_id': 1,
    },
    'offer_id': 'feed-id-1',
    'price': '200.0000',
    'price_with_currency': {
        'value': '200',
        'currency': 'RUB',
        'formatted': '200 ₽',
    },
}
EXPECTED_OK_RESPONSE = {'is_avaliable': True, 'offer': EXPECTED_OFFER}

EXPECTED_OK_RESPONSE_WITH_META: typing.Dict[str, typing.Any] = {
    'is_avaliable': True,
    'offer': {
        **EXPECTED_OFFER,
        'timer_expiration_params': {
            'localized_header': 'Discount available',
            'localized_subheader': 'Offer is limited and will expire soon!',
            'image_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
            'expires_at': '2021-07-09T03:00:15.890537+0000',
        },
        'extra_badge_params': {
            'message': 'Expired',
            'badge_color': '#FFD4E0',
            'text_color': '#D4120F',
        },
    },
}


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3(filename='personalize_offers_experiment.json')
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_selection_id_returned(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_replica,
        mock_parks_activation,
        mock_personal,
        mock_umlaas_contractors,
        offer_id_type,
):
    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200
    assert response.headers['X-Selection-Provider'] == 'ml'
    assert response.headers['X-Driver-Profile-Id'] == DRIVER_ID
    content = response.json()
    assert content == util.get_expected_offer_response(load_json)


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    'has_position, expected_payment_link_template',
    [
        pytest.param(
            True,
            'https://loyka.loyka/?lat=37.5&lon=55.765432&id={payment_id}',
            id='has position',
        ),
        pytest.param(
            False,
            'https://loyka.loyka/?lat=&lon=&id={payment_id}',
            id='has position',
        ),
    ],
)
async def test_payment_link_templates(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        mock_driver_trackstory,
        offer_id_type,
        has_position,
        expected_payment_link_template,
):
    mock_driver_trackstory.set_has_position(has_position)

    mock_feeds.set_response(
        load_json('feeds_response_with_payment_link_template.json'),
    )

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200

    response_json = response.json()
    response_json['offer']['offer_data']['actions'][-1][
        'payment_link_template'
    ] = (
        urllib.parse.unquote_plus(
            response_json['offer']['offer_data']['actions'][-1][
                'payment_link_template'
            ],
        )
    )

    assert response_json['offer']['offer_data']['actions'][-1] == {
        'type': 'payment_link_template',
        'link_caption': 'Loyka',
        'payment_link_template': expected_payment_link_template,
    }

    assert mock_driver_trackstory.position.times_called == 1
    assert mock_driver_trackstory.position.next_call()['request'].json == {
        'driver_id': 'park_id_driver_id',
    }


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.pgsql('contractor_merch', files=['one_available.sql'])
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    'balance', [pytest.param('-100'), pytest.param('0'), pytest.param('100')],
)
async def test_price_zero_voucher_offer(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_tags,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        balance,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        resp = load_json('responses/feeds_response.json')
        resp['feed'][0]['payload']['price'] = '0'
        return resp

    mock_fleet_transactions_api.balance = balance
    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200

    response_json = response.json()
    assert response_json == load_json('price_zero_offer.json')


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_metro_voucher_cannotbuy(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        resp = load_json('responses/feeds_response.json')
        resp['feed'][0]['payload']['meta_info']['metro_price_choice'] = {
            'min_price': 10,
            'max_price': 100,
            'step': 10,
        }
        return resp

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200

    assert response.json() == util.get_expected_offer_response(load_json)


RESPONSE_FROM_DRIVER_PROFILES_BALANCE_LIMIT = {
    'profiles': [
        {
            'data': {'balance_limit': '0'},
            'park_driver_profile_id': 'change this id in mock',
        },
    ],
}

BASE_HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.50',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'Accept-Language': 'en_GB',
}

REQUEST_TO_FLEET_ANTIFRAUD = {
    'park_id': 'park_id',
    'contractor_id': 'some_driver',
    'do_update': 'false',
}


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.now('2021-07-01T14:30:00+00:00')
@pytest.mark.pgsql(
    'contractor_merch', files=['one_voucher.sql', 'feed_payload.sql'],
)
async def test_priority_params_already_bought(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_antifraud,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        assert request.json['channels'] == [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_id',
            'experiment:contractor_merch_offer_matched',
            'tag:bronze',
            'tag:silver',
            'tag:gold',
        ]
        if offer_id_type == MUTABLE:
            assert request.json['feed_id'] == 'feed-id-1'
        else:
            assert request.json['package_ids'] == ['feeds-admin-id-1']
        return load_json('feeds_response_with_meta.json')

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    expected_response_with_block = copy.deepcopy(
        EXPECTED_OK_RESPONSE_WITH_META,
    )
    expected_response_with_block['offer']['timer_expiration_params'] = {
        'expires_at': '2021-07-01T15:00:00+0000',
        'localized_header': 'Go drive!',
    }
    expected_response_with_block['is_avaliable'] = False
    expected_response_with_block['is_available'] = False
    expected_response_with_block['problem_description'] = {
        'code': 'driver_already_has_priority',
        'localized_message': 'driver_already_has_priority',
    }
    assert content == expected_response_with_block


@pytest.mark.translations(
    taximeter_backend_marketplace=TRANSLATIONS,
    taximeter_backend_marketplace_custom_messages=CUSTOM_TRANSLATIONS,
)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.now('2021-07-01T16:30:00+00:00')
@pytest.mark.pgsql(
    'contractor_merch', files=['one_voucher.sql', 'feed_payload.sql'],
)
async def test_priority_params_bought_way_back(
        taxi_contractor_merch,
        mockserver,
        load_json,
        mock_billing_replication,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_fleet_parks,
        mock_driver_tags,
        mock_driver_profiles,
        mock_personal,
        mock_fleet_antifraud,
        offer_id_type,
):
    @mockserver.json_handler(FETCH_BY_IDS[offer_id_type])
    async def _feeds(request):
        assert request.json['channels'] == [
            'country:rus',
            'city:city1',
            'contractor:park_id_driver_id',
            'experiment:contractor_merch_offer_matched',
            'tag:bronze',
            'tag:silver',
            'tag:gold',
        ]
        if offer_id_type == MUTABLE:
            assert request.json['feed_id'] == 'feed-id-1'
        else:
            assert request.json['package_ids'] == ['feeds-admin-id-1']
        return load_json('feeds_response_with_meta.json')

    mock_fleet_transactions_api.balance = '200'

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type], headers=HEADERS,
    )

    assert response.status == 200
    content = response.json()
    expected = copy.deepcopy(EXPECTED_OK_RESPONSE_WITH_META)
    del expected['offer']['timer_expiration_params']
    expected['is_avaliable'] = True
    expected['is_available'] = True
    assert content == expected


@pytest.mark.now('2021-07-01T14:00:00Z')
@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
@pytest.mark.parametrize(
    ['total_balance', 'fleet_antifraud_limit', 'is_enough'],
    [
        pytest.param(
            '199',
            '0',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not enough total_balance with fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '199',
            '0',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not enough total_balance with fleet_antifraud_limit = 0',
        ),
        pytest.param(
            '200',
            '1',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not enough with fleet_antifraud_limit > 0',
        ),
        pytest.param(
            '200',
            '1',
            True,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='enough with fleet_antifraud_limit > 0 '
            'and config_antifraud_check off ',
        ),
        pytest.param(
            '199',
            '-1',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=True,
            ),
            id='not enough with fleet_antifraud_limit < 0',
        ),
        pytest.param(
            '199',
            '-1',
            False,
            marks=pytest.mark.config(
                CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK=False,
            ),
            id='not enough with fleet_antifraud_limit < 0',
        ),
    ],
)
async def test_fleet_antifraud_limit(
        taxi_config,
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
        total_balance,
        fleet_antifraud_limit,
        is_enough,
):
    mock_fleet_transactions_api.balance = total_balance
    mock_fleet_antifraud.fleet_antifraud_limit = fleet_antifraud_limit

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    if (
            taxi_config.get('CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK')
            is not None
            and taxi_config.get('CONTRACTOR_MERCH_ENABLE_ANTIFRAUD_CHECK')
    ):
        assert mock_fleet_antifraud.fleet_antifraud.times_called == 1

        request_query_fleet_antifraud = dict(
            mock_fleet_antifraud.fleet_antifraud.next_call()['request'].query,
        )
        assert request_query_fleet_antifraud == {
            'park_id': 'park_id',
            'contractor_id': 'some_driver',
            'do_update': 'false',
        }

    assert response.status == 200

    expected_offer_response = util.get_expected_offer_response(load_json)
    if not is_enough:
        expected_offer_response = {
            **expected_offer_response,
            'is_available': False,
            'is_avaliable': False,
            'problem_description': {
                'code': 'not_enough_money_on_drivers_balance',
                'localized_message': 'not_enough_money_on_drivers_balance-tr',
            },
        }
    else:
        expected_offer_response = {
            **expected_offer_response,
            'is_available': False,
            'is_avaliable': False,
            'problem_description': {
                'code': 'no_promocodes_left',
                'localized_message': 'no_promocodes_left-tr',
            },
        }

    assert response.json() == expected_offer_response

    assert mock_driver_profiles.driver_profiles.times_called == 1
    assert mock_fleet_transactions_api.balances_list.times_called == 1
    assert (
        mock_fleet_transactions_api.balances_list.next_call()['request'].json
        == {
            'query': {
                'balance': {'accrued_ats': ['2021-07-01T14:00:00+00:00']},
                'park': {
                    'driver_profile': {'ids': ['some_driver']},
                    'id': 'park_id',
                },
            },
        }
    )


@pytest.mark.translations(taximeter_backend_marketplace=TRANSLATIONS)
@pytest.mark.experiments3()
@pytest.mark.parametrize('offer_id_type', [MUTABLE, IMMUTABLE])
async def test_park_without_contract(
        taxi_contractor_merch,
        load_json,
        mockserver,
        mock_billing_replication,
        mock_driver_profiles,
        mock_driver_tags,
        mock_feeds,
        mock_fleet_antifraud,
        mock_fleet_parks,
        mock_fleet_transactions_api,
        mock_parks_activation,
        mock_parks_replica,
        mock_personal,
        offer_id_type,
):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    def _active_contracts(request):
        return mockserver.make_response(
            status=400, json={'code': 'not_found', 'message': 'Not found'},
        )

    response = await taxi_contractor_merch.get(
        HANDLERS_BY_IDS[offer_id_type],
        headers={**HEADERS, 'X-YaTaxi-Driver-Profile-Id': 'some_driver'},
    )

    assert response.status == 200

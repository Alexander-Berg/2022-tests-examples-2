import json

import pytest

from taxi_tests import json_util

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils


def compare_offers(offer, expected_offer, with_decoupling=False):
    assert 'prices' in offer
    assert 'prices' in expected_offer
    prices = sorted(offer['prices'], key=lambda x: x['cls'])
    expected_prices = sorted(expected_offer['prices'], key=lambda x: x['cls'])
    assert prices == expected_prices

    assert offer.get('complements') == expected_offer.get('complements')
    assert offer.get('alternative_type') == expected_offer.get(
        'alternative_type',
    )

    assert 'distance' in offer
    assert 'distance' in expected_offer
    distance = offer['distance']
    expected_distance = expected_offer['distance']
    assert distance == expected_distance

    assert 'time' in offer
    assert 'time' in expected_offer
    time = offer['time']
    expected_time = expected_offer['time']
    assert time == expected_time

    if with_decoupling:
        assert 'extra_data' in offer
        assert 'decoupling' in offer['extra_data']
        decoupling = offer['extra_data']['decoupling']
        assert 'extra_data' in expected_offer
        assert 'decoupling' in expected_offer['extra_data']
        expected_decoupling = expected_offer['extra_data']['decoupling']

        assert 'success' in expected_decoupling
        successful_decoupling = expected_decoupling['success']
        if successful_decoupling:
            assert 'driver' in decoupling
            assert 'prices' in decoupling['driver']
            decoupling['driver']['prices'].sort(key=lambda x: x['cls'])
            assert 'user' in decoupling
            assert 'prices' in decoupling['user']
            decoupling['user']['prices'].sort(key=lambda x: x['cls'])

            assert 'driver' in expected_decoupling
            assert 'prices' in expected_decoupling['driver']
            expected_decoupling['driver']['prices'].sort(
                key=lambda x: x['cls'],
            )
            assert 'user' in expected_decoupling
            assert 'prices' in expected_decoupling['user']
            expected_decoupling['user']['prices'].sort(key=lambda x: x['cls'])
        else:
            assert 'driver' not in decoupling
            assert 'user' not in decoupling

        assert decoupling == expected_decoupling
    elif 'extra_data' in offer:
        assert 'decoupling' not in offer['extra_data']

    if 'discount' in expected_offer:
        assert 'discount' in offer
        discount = offer['discount']
        expected_discount = expected_offer['discount']
        discount['by_classes'].sort(key=lambda x: x['class'])
        expected_discount['by_classes'].sort(key=lambda x: x['class'])
        assert offer['discount'] == expected_offer['discount']
    else:
        assert 'discount' not in offer

    if 'extra_data' in expected_offer:
        assert 'extra_data' in offer
        if 'coupon' in expected_offer['extra_data']:
            assert 'coupon' in offer['extra_data']
            expected_coupon = expected_offer['extra_data']['coupon']
            coupon = offer['extra_data']['coupon']
            assert expected_coupon == coupon
        else:
            assert 'coupon' not in offer['extra_data']
    elif 'extra_data' in offer:
        assert 'coupon' not in offer['extra_data']

    if 'user_tags' in expected_offer:
        assert 'user_tags' in offer
        user_tags = offer['user_tags'].sort()
        expected_user_tags = expected_offer['user_tags'].sort()
        assert user_tags == expected_user_tags
    else:
        assert 'user_tags' not in offer


def compare_required_service_level_item(
        service_level, expected_service_level, item_name,
):
    assert item_name in service_level
    assert item_name in expected_service_level
    item = service_level[item_name]
    expected_item = expected_service_level[item_name]
    if type(expected_item) is str:
        expected_item = expected_item.replace('\\xa0', '\xa0')
    assert item == expected_item


def compare_optional_service_level_item(
        service_level, expected_service_level, item_name,
):
    if item_name in expected_service_level:
        assert item_name in service_level
        item = service_level[item_name]
        expected_item = expected_service_level[item_name]
        if type(expected_item) is str:
            expected_item = expected_item.replace('\\xa0', '\xa0')
        assert item == expected_item
    else:
        assert item_name not in service_level


def check_surge_popup(expected, actual):
    for key, value in expected.items():
        assert key in actual
        assert value == actual[key]


def compare_response_service_levels(
        service_levels,
        expected_service_levels,
        with_fixed_price,
        need_check_surge_popup,
):
    assert len(service_levels) == len(expected_service_levels)

    for expected_service_level in expected_service_levels:
        assert 'class' in expected_service_level
        cls_ = expected_service_level['class']
        filtered_list = list(
            filter(lambda x: x['class'] == cls_, service_levels),
        )
        assert len(filtered_list) == 1
        service_level = filtered_list[0]

        if (
                'tariff_unavailable' in service_level
                and 'tariff_unavailable' in expected_service_level
        ):
            assert (
                service_level['tariff_unavailable']
                == expected_service_level['tariff_unavailable']
            )
            if 'description' not in expected_service_level:
                continue

        compare_required_service_level_item(
            service_level, expected_service_level, 'description',
        )

        compare_optional_service_level_item(
            service_level, expected_service_level, 'pin_description',
        )

        compare_required_service_level_item(
            service_level, expected_service_level, 'price',
        )

        assert 'is_hidden' in service_level
        assert 'is_hidden' in expected_service_level
        is_hidden = service_level['is_hidden']
        expected_is_hidden = expected_service_level['is_hidden']
        assert is_hidden == expected_is_hidden

        if with_fixed_price:
            assert 'is_fixed_price' in service_level
            assert 'is_fixed_price' in expected_service_level
            is_fixed_price = service_level['is_fixed_price']
            assert is_fixed_price
            expected_is_fixed_price = expected_service_level['is_fixed_price']
            assert is_fixed_price == expected_is_fixed_price
        else:
            assert 'is_fixed_price' not in service_level

        # paid supply or surge
        if 'paid_options' in expected_service_level:
            assert 'paid_options' in service_level
            if 'value' in expected_service_level['paid_options']:
                assert 'value' in service_level['paid_options']
                surge_value = service_level['paid_options']['value']
                expected_surge_value = expected_service_level['paid_options'][
                    'value'
                ]
                assert surge_value == expected_surge_value
            else:
                assert 'value' not in service_level['paid_options']
            if (
                    'order_popup_properties'
                    in expected_service_level['paid_options']
            ):
                assert (
                    'order_popup_properties' in service_level['paid_options']
                )
            elif (
                'order_popup_properties'
                not in expected_service_level['paid_options']
            ):
                assert (
                    'order_popup_properties'
                    not in service_level['paid_options']
                )
            elif need_check_surge_popup:
                assert (
                    'order_popup_properties' in service_level['paid_options']
                )
                check_surge_popup(
                    expected_service_level['paid_options'][
                        'order_popup_properties'
                    ],
                    service_level['paid_options']['order_popup_properties'],
                )

        else:
            assert 'paid_options' not in service_level

        # strikeout price
        compare_optional_service_level_item(
            service_level, expected_service_level, 'description_markup',
        )
        compare_optional_service_level_item(
            service_level, expected_service_level, 'original_price',
        )

        compare_optional_service_level_item(
            service_level, expected_service_level, 'discount',
        )

        compare_optional_service_level_item(
            service_level, expected_service_level, 'price_ride',
        )

        compare_optional_service_level_item(
            service_level, expected_service_level, 'brandings',
        )


def compare_responses(
        response,
        expected_response,
        with_alternatives,
        with_fixed_price,
        need_check_surge_popup,
        is_preorder=False,
):
    if 'distance' in expected_response:
        assert 'distance' in response
        distance = response['distance']
        expected_distance = expected_response['distance']
        assert distance == expected_distance
    else:
        assert 'distance' not in response

    assert 'service_levels' in response
    assert 'service_levels' in expected_response
    service_levels = response['service_levels']
    expected_service_levels = expected_response['service_levels']
    compare_response_service_levels(
        service_levels,
        expected_service_levels,
        with_fixed_price,
        need_check_surge_popup,
    )

    if 'alternatives' not in expected_response:
        assert 'alternatives' not in response
        return
    assert 'alternatives' in response

    options_size = 2 if with_alternatives else (0 if is_preorder else 1)

    assert 'options' in expected_response['alternatives']
    expected_options = expected_response['alternatives']['options']
    assert len(expected_options) == options_size

    assert 'options' in response['alternatives']
    options = response['alternatives']['options']
    assert len(options) == options_size

    for expected_option in expected_options:
        assert 'type' in expected_option
        type = expected_option['type']

        filtered_list = list(filter(lambda x: x['type'] == type, options))
        assert len(filtered_list) == 1
        option = filtered_list[0]

        if type == 'altpin':
            assert 'pin_card' in option
            assert 'description' in option['pin_card']
            description = option['pin_card']['description']
            assert 'price_delta' in option['pin_card']
            price_delta = option['pin_card']['price_delta']

            assert 'pin_card' in expected_option
            assert 'description' in expected_option['pin_card']
            expected_description = expected_option['pin_card'][
                'description'
            ].replace('\\xa0', '\xa0')
            assert 'price_delta' in expected_option['pin_card']
            expected_price_delta = expected_option['pin_card'][
                'price_delta'
            ].replace('\\xa0', '\xa0')

            assert description == expected_description
            assert price_delta == expected_price_delta
        elif type == 'multiclass':
            assert 'details' in option
            assert 'price' in option['details']
            price = option['details']['price']
            assert 'details' in expected_option
            assert 'price' in expected_option['details']
            expected_price = expected_option['details']['price'].replace(
                '\\xa0', '\xa0',
            )
            assert price == expected_price
        elif type == 'explicit_antisurge':
            if 'time' in expected_option:
                assert 'time' in option
                assert expected_option['time'] == option['time']
            if 'time_seconds' in expected_option:
                assert 'time_seconds' in option
                assert (
                    expected_option['time_seconds'] == option['time_seconds']
                )
        elif type == 'plus_promo':
            assert 'personal_wallet_withdraw_amount' in option
            assert isinstance(option['personal_wallet_withdraw_amount'], str)
        elif type == 'perfect_chain':
            assert True
        elif type == 'combo_order':
            assert False, 'must be explicit_antisurge instead of combo_order'
        else:
            assert False, 'unknown option_type: %s' % type

        if type != 'multiclass':
            assert 'service_levels' in option
            alt_service_levels = option['service_levels']
            assert 'service_levels' in expected_option
            expected_alt_service_levels = expected_option['service_levels']
            compare_response_service_levels(
                alt_service_levels,
                expected_alt_service_levels,
                with_fixed_price,
                need_check_surge_popup,
            )

        if type != 'explicit_antisurge' and 'distance' in expected_option:
            assert 'distance' in option
            distance = option['distance']
            expected_distance = expected_option['distance']
            assert distance == expected_distance
        else:
            assert 'distance' not in option


def check_toll_roads(request_toll_roads, with_toll_roads, response):
    if request_toll_roads:
        assert 'toll_roads' in response
        assert 'has_tolls' in response['toll_roads']
        assert response['toll_roads']['has_tolls'] == with_toll_roads
    else:
        assert 'toll_roads' not in response


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.user_experiments(
    'fixed_price',
    'explicit_antisurge',
    'no_cars_order_available',
    'multiclass',
    'discount_strike',
    'mastercard_discount',
)
@pytest.mark.experiments3(filename='exp3_plugin_decoupling.json')
@pytest.mark.experiments3(filename='exp3_plugin_preorder.json')
@pytest.mark.experiments3(filename='exp3_plugin_user_tags.json')
@pytest.mark.experiments3(filename='exp3_eta_from_driver_eta.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_can_notify_about_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_use_toll_roads.json')
@pytest.mark.experiments3(filename='exp3_combo_order.json')
@pytest.mark.config(
    # from test_routestats.py::test_call_pricing_data_preparer
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 45, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
    # from test_routestats.py::test_explicit_antisurge
    EXPLICIT_ANTISURGE_SETTINGS={
        '__default__': {
            'MIN_ABS_GAIN': 20,
            'MIN_REL_GAIN': 0.2,
            'MIN_SURGE_B': 0.9,
        },
    },
    EXPLICIT_ANTISURGE_ETA_OFFSET={'__default__': 5},
    EXPLICIT_ANTISURGE_PIN_CARD_ICON='',
    # from test_routestats.py::test_altpin_price_delta_not_zero_fixed_price
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 10,
            'price_gain_absolute_minorder': 0,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
    ALTPIN_MONEY_THRESHOLD_DEST_TIME=1,
    # from test_routestats.py::test_multiclass
    MULTICLASS_ENABLED=True,
    MULTICLASS_TARIFFS_BY_ZONE={'__default__': ['econom', 'business']},
    MULTICLASS_SELECTOR_ICON='',
    ROUTESTATS_FETCH_USER_TAGS=True,
    PERSONAL_WALLET_ENABLED=True,
    PREORDER_PAYMENT_METHODS=['card'],
    PREORDER_CLASSES=['econom', 'business'],
    STORE_COUPONS_IN_ALT_OFFERS_ENABLED=True,
    ROUTESTATS_SURGE_POPUP_TANKER_PREFIX={'rus': 'russia'},
)
# from test_routestats.py::test_multiclass
@pytest.mark.translations(
    client_messages={
        'routestats.tariff_unavailable.multiclass_invalid': {
            'ru': 'Multiclass invalid selection',
        },
        'routestats.tariff_unavailable.multiclass_unavailable': {
            'ru': 'Multiclass unavailable',
        },
        'routestats.tariff_unavailable.unsupported_payment_method': {
            'ru': 'Payment method is not supported',
        },
        'multiclass.min_selected_count.text': {
            'ru': 'Выберите %(min_count)s и более классов',
        },
        'multiclass.popup.text': {'ru': 'Кто быстрей'},
    },
    tariff={
        'routestats.multiclass.name': {'ru': 'Fast'},
        'routestats.multiclass.details.fixed_price': {'ru': 'below %(price)s'},
        'routestats.multiclass.details.not_fixed_price': {
            'ru': 'more than %(price)s',
        },
        'routestats.multiclass.details.description': {
            'ru': 'description of multiclass',
        },
        'routestats.multiclass.search_screen.title': {'ru': 'Searching'},
        'routestats.multiclass.search_screen.subtitle': {'ru': 'fastest car'},
        'routestats.multiclass.details.order_button.text': {
            'ru': 'choose tariffs',
        },
    },
)
@pytest.mark.parametrize(
    'testname, params',
    [
        ('simple', {'with_fixed_price'}),
        ('use_surge_from_pricing', {'with_antisurge', 'with_fixed_price'}),
        ('combo_order', {'with_combo_order', 'with_fixed_price'}),
        (
            # combo order exists but disabled because coupon is used
            'combo_order_coupon',
            {'with_fixed_price', 'with_coupon'},
        ),
        (
            # we expect no alt offer if combo order has higher price
            'combo_order_higher_price',
            {'with_combo_order', 'with_fixed_price'},
        ),
        (
            # we expect to only get antisurge as it has higher priority
            'combo_order_antisurge',
            {'with_combo_order', 'with_antisurge', 'with_fixed_price'},
        ),
        (
            # we expect to only get combo_order as it has higher priority
            'combo_order_altpins',
            {'with_combo_order', 'with_altpins', 'with_fixed_price'},
        ),
        (
            # combo order exists but disabled by corp_decoupling = true
            'combo_order_disabled_decoupling',
            {'with_decoupling', 'with_fixed_price'},
        ),
        (
            # combo order exists but disabled by preorder
            'combo_order_disabled_preorder',
            {'with_fixed_price'},
        ),
        (
            # combo order exists but disabled by fixed_price = false
            'combo_order_disabled_fixed_price',
            {},
        ),
        ('combo_order_disabled_no_client_support', {'with_fixed_price'}),
        ('antisurge', {'with_antisurge', 'with_fixed_price'}),
        ('plus_promo', {'with_plus_promo', 'with_fixed_price'}),
        ('altpins', {'with_altpins', 'with_fixed_price'}),
        ('paid_supply', {'with_paid_supply', 'with_fixed_price'}),
        ('decoupling', {'with_decoupling', 'with_fixed_price'}),
        ('multiclass', {'with_fixed_price'}),
        ('coupon', {'with_fixed_price', 'with_coupon'}),
        pytest.param(
            'coupon_zero_percent',
            {'with_fixed_price', 'with_coupon'},
            marks=pytest.mark.experiments3(
                filename='exp3_allow_zero_coupons.json',
            ),
        ),
        ('without_dst', {}),
        ('long_distance', {}),
        (
            # we expect error code 500 from routestats
            'pdp_timeout_throw_exception',
            {'pdp_timeout'},
        ),
        (
            # one category in pdp response missed
            # expect offer and prices by existing categories
            'missed_category',
            {'with_fixed_price'},
        ),
        ('altpins_fallback', {'with_altpins', 'with_fixed_price'}),
        ('antisurge_fallback', {'with_antisurge', 'with_fixed_price'}),
        ('paid_supply_fallback', {'with_paid_supply', 'with_fixed_price'}),
        ('reset_fixed_price_by_blocked_route', {}),
        (
            'paid_supply_with_coupon',
            {'with_paid_supply', 'with_fixed_price', 'with_coupon'},
        ),
        ('override_discounts', {'with_fixed_price'}),
        ('use_pricing_discounts', {'with_fixed_price'}),
        (
            # response from pdp for altpins has flag fixed_price = false
            # we must skip altpin alternative in that case
            'altpins_not_fixed_fallback',
            {'with_altpins', 'with_fixed_price'},
        ),
        (
            # pdp response has flag corp_decoupling == false
            # it's not normal behaviour
            # we expect new pricing with success == false in decoupling
            'decoupling_pdp_without_decoupling',
            {'with_decoupling', 'with_fixed_price'},
        ),
        (
            # pdp response has flag corp_decoupling == true, but
            # flag decoupling failed for all categories
            # we expect new pricing with success == false in decoupling
            'decoupling_pdp_failed_all_decoupling',
            {'with_decoupling', 'with_fixed_price'},
        ),
        (
            # pdp response has successful decoupling and paid supply
            # we expect new pricing with success == true in decoupling
            # and with paid supply and with paid cancel from old calc
            'decoupling_with_paid_supply',
            {'with_decoupling', 'with_paid_supply', 'with_fixed_price'},
        ),
        (
            # pdp response has successful decoupling and paid supply
            # we expect new pricing with success == true in decoupling
            # and with paid supply and with paid cancel from old calc
            # with flag disable_paid_supply from corp tariffs
            'decoupling_with_disable_paid_supply',
            {'with_decoupling', 'with_paid_supply', 'with_fixed_price'},
        ),
        (
            # failed decoupling in pdp and flag disable_fixed_price = true
            # we expect using new prices with is_fixed_price = false
            'decoupling_disable_fixed_price_and_failed',
            {'with_decoupling'},
        ),
        (
            # success decoupling in pdp and flag disable_fixed_price = true
            # we expect using new prices with is_fixed_price = false
            'decoupling_disable_fixed_price',
            {'with_decoupling'},
        ),
        (
            # success decoupling in pdp by one category
            # failed category must be unavailable
            'decoupling_partial_failed',
            {'with_decoupling', 'with_fixed_price'},
        ),
        (
            # antisurge price for one category and
            # paid supply price for another
            'antisurge_and_paid_supply',
            {'with_antisurge', 'with_paid_supply', 'with_fixed_price'},
        ),
        (
            # antisurge disabled by paid supply: EFFICIENCYDEV-14210
            'antisurge_disabled_by_paid_supply',
            {'with_paid_supply', 'with_fixed_price'},
        ),
        (
            # successful decoupling with fixed_price is false
            # pdp returned zero trip_information
            # but old pricing have flag fixed_price is true
            # we expect price "from x" not "~x"
            'decoupling_and_pdp_router_failed',
            {'with_decoupling'},
        ),
        (
            # pdp returned zero trip information when fixed_price is false
            # we expect price "from x" not "~x"
            'long_distance_and_pdp_router_failed',
            {},
        ),
        (
            # plus user gets cashback instead of discount
            # total price is splitted for order price and cashback price
            # cashback is 100 only by Plus for econom
            # and 560 for business: 200 by Plus and 360(1800*0.2) by discount
            'cashback_for_plus',
            {'with_fixed_price'},
        ),
        (
            # plus user gets cashback instead of discount
            # total price is splitted for order price and cashback price
            # no cashback for econom
            # and cashback on paid supply for business:
            # total 840 from 300 by Plus and 540(2700*0.2) by discount
            'cashback_for_plus_and_paid_supply',
            {'with_paid_supply', 'with_fixed_price'},
        ),
        (
            # plus user gets cashback instead of discount
            # total price is NOT splitted for order price and cashback price
            # cashback is 100 only by Plus for econom
            # and 560 for business: 200 by Plus and 360(1800*0.2) by discount
            'cashback_for_plus_unite_total',
            {'with_fixed_price'},
        ),
        (
            # plus user gets cashback instead of discount
            # total price is NOT splitted for order price and cashback price
            # no cashback for econom
            # and cashback on paid supply for business:
            # total 840 from 300 by Plus and 540(2700*0.2) by discount
            'cashback_for_plus_and_paid_supply_unite_total',
            {'with_paid_supply', 'with_fixed_price'},
        ),
        (
            # route with 2 same points
            # new pricing returned small distance and time
            'route_A_to_A',
            {'with_fixed_price'},
        ),
        (
            # route with 2 same points
            # new pricing returned zero distance and time
            'route_A_to_A_pdp_router_failed',
            {},
        ),
        (
            # expect usual fixed price ride
            'route_A_to_B_to_A',
            {'with_fixed_price'},
        ),
        (
            # expect usual not fixed price ride
            'route_A_to_B_to_A_pdp_router_failed',
            {},
        ),
        (
            # expect has_tolls in routestats response
            'with_toll_roads',
            {'with_fixed_price'},
        ),
        (
            # not expect has_tolls in routestats response
            'without_toll_roads',
            {'with_fixed_price'},
        ),
        ('with_user_tags', {'with_fixed_price'}),
        (
            # antisurge exists but disabled by relative difference
            'antisurge_disabled_rel',
            {'with_fixed_price'},
        ),
        (
            # antisurge exists but disabled by absolute difference
            'antisurge_disabled_abs',
            {'with_fixed_price'},
        ),
        (
            # antisurge exists but disabled by surge at point b
            'antisurge_disabled_surge_b',
            {'with_fixed_price'},
        ),
        (
            # antisurge exists but disabled by fixed_price = false
            'antisurge_disabled_fixed_price',
            {},
        ),
        (
            # antisurge exists but disabled by corp_decoupling = true
            'antisurge_disabled_decoupling',
            {'with_decoupling', 'with_fixed_price'},
        ),
        (
            # antisurge exists but disabled by preorder
            'antisurge_disabled_preorder',
            {'with_fixed_price'},
        ),
        (
            # coupon should be stored in db for antisurge alt offer
            'antisurge_with_coupon',
            {'with_fixed_price', 'with_antisurge', 'with_coupon'},
        ),
        (
            # coupon should be stored in db for plus_promo alt offer
            'plus_promo_with_coupon',
            {'with_fixed_price', 'with_plus_promo', 'with_coupon'},
        ),
        (
            # coupon should be stored in db for altpins alt offer
            'altpins_with_coupon',
            {'with_fixed_price', 'with_altpins', 'with_coupon'},
        ),
        (
            # coupon should be stored in db for alt offers from
            # alt-offer-discount
            'alt_offer_discount_with_coupon',
            {'with_fixed_price', 'with_alt_offer_discount', 'with_coupon'},
        ),
        ('special_surge_tanker_key', {'with_antisurge', 'with_fixed_price'}),
    ],
)
def test_use_new_prices(
        taxi_protocol,
        load_json,
        load_binary,
        mockserver,
        experiments3,
        db,
        testname,
        params,
):
    with_combo_order = 'with_combo_order' in params
    with_antisurge = 'with_antisurge' in params
    with_plus_promo = 'with_plus_promo' in params
    with_altpins = 'with_altpins' in params
    with_alt_offer_discount = 'with_alt_offer_discount' in params
    with_decoupling = 'with_decoupling' in params
    with_paid_supply = 'with_paid_supply' in params
    with_fixed_price = 'with_fixed_price' in params
    with_coupon = 'with_coupon' in params
    pdp_timeout = 'pdp_timeout' in params

    # from conftest.py
    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_pickup_altpoints(request):
        body = json.loads(request.get_data())
        assert body['selected_class'] == 'econom'
        assert len(body['extra']['prices']) == 1
        assert body['surge_value']
        return load_json(testname + '/altpoints.json')

    # from test_routestats.py::test_explicit_antisurge
    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        request_json = json.loads(request.get_data()).get('pin')
        assert 'tariff_zone' in request_json
        if with_antisurge and testname != 'antisurge_fallback':
            assert 'explicit_antisurge_offer_id' in request_json
        else:
            assert 'explicit_antisurge_offer_id' not in request_json
        if with_combo_order and testname not in [
                'combo_order_higher_price',
                'combo_order_antisurge',
        ]:
            assert 'combo_order_offer_id' in request_json
        else:
            assert 'combo_order_offer_id' not in request_json
        if testname == 'use_surge_from_pricing':
            expected = load_json(testname + '/surge_info.json')
            for field_name, value in expected.items():
                assert value == request_json[field_name]

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return False

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        if with_paid_supply:
            return load_json(testname + '/no_cars_order_mlaas.json')
        else:
            return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        if with_paid_supply:
            if 'extended_radius' in req and req['extended_radius']:
                return load_json(testname + '/driver_eta_extended_radius.json')
            else:
                return load_json(testname + '/driver_eta.json')
        else:
            return load_json('driver_eta.json')

    @mockserver.json_handler('/toll_roads/toll-roads/v1/offer')
    def mock_offer_save(request):
        request_json = json.loads(request.get_data())
        assert 'offer_id' in request_json
        return mockserver.make_response('', status=200)

    @mockserver.json_handler('/preorder/4.0/preorder/v1/availability')
    def mock_preorder_availability(request):
        return {
            'preorder_request_id': 'preorder_request_id_1',
            'allowed_time_info': [
                {
                    'class': 'econom',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2015-05-25T11:20:00+0300',
                            'to': '2099-05-25T11:40:00+0300',
                        },
                    ],
                },
                {
                    'class': 'business',
                    'interval_minutes': 15,
                    'allowed_time_ranges': [
                        {
                            'from': '2015-05-25T11:20:00+0300',
                            'to': '2099-05-25T11:40:00+0300',
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler('/personal_wallet/v1/balances')
    def _mock_balances(request):
        return {
            'balances': [
                {
                    'wallet_id': 'wallet_id/some_number_value',
                    'currency': 'RUB',
                    'is_new': True,
                    'balance': '60',
                    'payment_orders': [],
                },
            ],
            'available_deposit_payment_methods': [],
        }

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        if pdp_timeout:
            return mockserver.make_response({}, 500)

        data = json.loads(request.get_data())
        assert 'zone' in data and data['zone']
        assert 'classes_requirements' in data
        assert data['classes_requirements'] == {}
        assert 'waypoints' in data and data['waypoints']
        assert 'user_info' in data and 'user_id' in data['user_info']
        assert 'calc_additional_prices' in data
        assert 'strikeout' in data['calc_additional_prices']
        assert data['calc_additional_prices']['strikeout'] is True

        is_request_for_altpins = with_altpins and data['waypoints'] == [
            [37.60000000111, 55.7380111],
            [37.413673, 55.971204],
        ]

        assert 'antisurge' in data['calc_additional_prices']
        assert 'combo_order' in data['calc_additional_prices']
        expected_combo_order_enabled = all(
            [
                not is_request_for_altpins,
                testname != 'combo_order_disabled_no_client_support',
            ],
        )
        assert (
            data['calc_additional_prices']['combo_order']
            == expected_combo_order_enabled
        )
        assert 'strikeout' in data['calc_additional_prices']
        assert 'plus_promo' in data['calc_additional_prices']

        assert (
            data['calc_additional_prices']['antisurge']
            != is_request_for_altpins
        )

        if is_request_for_altpins:
            if testname == 'altpins_fallback':
                return mockserver.make_response({}, 500)
            else:
                return load_json(testname + '/alt_pdp_response.json')
        else:
            return load_json(testname + '/pdp_response.json')

    @mockserver.json_handler('/pricing_data_preparer/v2/calc_paid_supply')
    def _mock_v2_calc_paid_supply(request):
        if testname == 'paid_supply_fallback':
            return mockserver.make_response({}, 500)

        data = json.loads(request.get_data())
        assert 'point' in data and data['point']
        assert 'zone' in data and data['zone'] == 'moscow'
        assert 'categories' in data and data['categories']

        return load_json(testname + '/paid_supply_response.json')

    if with_altpins:
        experiments3.add_experiments_json(
            load_json('exp3_alt_point_switcher.json'),
        )

    if with_coupon:
        experiments3.add_experiments_json(
            load_json('exp3_plugin_offer_coupon.json'),
        )

    if with_plus_promo:
        experiments3.add_experiments_json(
            load_json('exp3_personal_wallet.json'),
        )
        experiments3.add_experiments_json(load_json('exp3_plus_promo.json'))

    if with_alt_offer_discount:
        experiments3.add_experiments_json(
            load_json('exp3_alt_offer_discount.json'),
        )

    request = load_json(testname + '/request.json')

    is_preorder = 'preorder_request_id' in request

    response = taxi_protocol.post(
        '3.0/routestats',
        request,
        headers={
            'User-Agent': (
                'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
            ),
        },
    )
    if pdp_timeout:
        assert response.status_code == 500
        return
    assert response.status_code == 200

    if pdp_timeout:
        assert _mock_v2_prepare.times_called == 3
    elif with_altpins:
        if testname == 'altpins_fallback':
            assert _mock_v2_prepare.times_called == 4
        elif testname == 'combo_order_altpins':
            assert _mock_v2_prepare.times_called == 1
        else:
            assert _mock_v2_prepare.times_called == 2
    else:
        assert _mock_v2_prepare.times_called == 1

    if with_paid_supply:
        if testname == 'paid_supply_fallback':
            assert _mock_v2_calc_paid_supply.times_called == 3
        else:
            assert _mock_v2_calc_paid_supply.times_called == 1
    else:
        assert _mock_v2_calc_paid_supply.times_called == 0

    assert not mock_surge_get_surge.has_calls

    with_alternatives = any(
        [
            with_antisurge,
            with_altpins,
            with_plus_promo,
            with_combo_order,
            with_alt_offer_discount,
        ],
    )
    if testname in [
            'altpins_fallback',
            'altpins_not_fixed_fallback',
            'antisurge_fallback',
            'combo_order_higher_price',
            'combo_order_disabled_no_client_support',
    ]:
        with_alternatives = False
    need_check_surge_popup = testname == 'special_surge_tanker_key'
    # compare responses
    response = response.json()
    expected_response = load_json(testname + '/response.json')
    compare_responses(
        response,
        expected_response,
        with_alternatives,
        with_fixed_price,
        need_check_surge_popup,
        is_preorder,
    )

    request_toll_roads = testname in ['with_toll_roads', 'without_toll_roads']
    with_toll_roads = testname in ['with_toll_roads']
    assert mock_offer_save.has_calls == request_toll_roads
    check_toll_roads(request_toll_roads, with_toll_roads, response)

    offer_without_fixed_price = testname in [
        'long_distance',
        'decoupling_disable_fixed_price_and_failed',
        'decoupling_disable_fixed_price',
        'antisurge_disabled_fixed_price',
        'combo_order_disabled_fixed_price',
    ]
    if with_fixed_price or offer_without_fixed_price:
        # compare offers
        assert 'offer' in response
        offer_id = response['offer']
        offer = utils.get_offer(offer_id, db)
        assert offer
        expected_offer = load_json(testname + '/offer.json')
        compare_offers(offer, expected_offer, with_decoupling)

        if with_alternatives:
            assert 'alternatives' in response
            assert 'options' in response['alternatives']
            options = response['alternatives']['options']
            assert len(options) == 2

            alt_offer_id = None
            for option in options:
                assert 'offer' in option
                assert 'type' in option
                if option['type'] == 'multiclass':
                    assert option['offer'] == offer_id
                else:
                    alt_offer_id = option['offer']

            assert alt_offer_id
            alt_offer = utils.get_offer(alt_offer_id, db)
            assert alt_offer
            expected_alt_offer = load_json(testname + '/alt_offer.json')
            assert expected_alt_offer

            compare_offers(alt_offer, expected_alt_offer)
        elif (
            'alternatives' in response
            and 'options' in response['alternatives']
        ):
            assert len(response['alternatives']['options']) == (
                0 if is_preorder else 1
            )
    else:
        assert 'offer' not in response
        offer = utils.get_saved_offer(db)
        assert not offer

    mock_pin_storage_create_pin.wait_call()


@pytest.mark.parametrize('locale', [None, 'en-US', 'ru-RU'])
def test_pass_locale(taxi_protocol, load_json, mockserver, locale):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        data = json.loads(request.get_data())
        assert 'zone' in data and data['zone']
        expected = locale[:2] if locale else 'en'
        assert request.headers['Accept-Language'] == expected
        return {}

    request = load_json('simple_request.json')
    headers = {
        'User-Agent': (
            'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
        ),
    }
    if locale:
        headers['Accept-Language'] = locale

    taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert _mock_v2_prepare.has_calls


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.user_experiments(
    'fixed_price', 'explicit_antisurge', 'no_cars_order_available',
)
@pytest.mark.experiments3(filename='exp3_plugin_decoupling.json')
@pytest.mark.experiments3(filename='exp3_eta_from_driver_eta.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_can_notify_about_paid_cancel.json')
@pytest.mark.config(
    # from test_routestats.py::test_call_pricing_data_preparer
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 45, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
)
@pytest.mark.parametrize(
    'paid_supply_paid_cancel_price,'
    'paid_cancel_price,'
    'expected_paid_cancel_in_driving_price',
    [(None, None, None), (321.0, None, 321.0)],
    ids=['no_paid_cancel_in_driving', 'paid_cancel_of_paid_supply'],
)
@ORDER_OFFERS_SAVE_SWITCH
def test_paid_cancel_in_driving(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        mock_order_offers,
        order_offers_save_enabled,
        paid_supply_paid_cancel_price,
        paid_cancel_price,
        expected_paid_cancel_in_driving_price,
):
    # from test_routestats.py::test_explicit_antisurge
    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        pass

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def _mock_surge_get_surge(request):
        res = utils.get_surge_calculator_response(request, 1)
        for class_info in res['classes']:
            if class_info['name'] == 'econom':
                class_info['explicit_antisurge'] = {'value': 0.3}
                class_info['value'] = 0.8
                class_info['base_surge'] = {'value': 1.01}
                class_info['value_smooth_b'] = 1.0
                break
        return res

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        if 'extended_radius' in req and req['extended_radius']:
            return load_json('driver_eta_extended_radius.json')
        else:
            return load_json('driver_eta.json')

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        meta = {}
        if paid_cancel_price:
            meta['paid_cancel_price'] = paid_cancel_price

        variables = {'driver_meta': meta, 'user_meta': meta}
        return load_json(
            'pdp_response.json', object_hook=json_util.VarHook(variables),
        )

    @mockserver.json_handler('/pricing_data_preparer/v2/calc_paid_supply')
    def _mock_v2_calc_paid_supply(request):
        paid_supply_meta = {}
        meta = {}
        if paid_supply_paid_cancel_price:
            paid_supply_meta[
                'paid_supply_paid_cancel_in_driving_price'
            ] = paid_supply_paid_cancel_price
        if paid_cancel_price:
            paid_supply_meta[
                'paid_cancel_in_driving_price'
            ] = paid_cancel_price
            meta['paid_cancel_in_driving_price'] = paid_cancel_price

        variables = {
            'driver_paid_supply_meta': paid_supply_meta,
            'user_paid_supply_meta': paid_supply_meta,
            'driver_meta': meta,
            'user_meta': meta,
        }
        return load_json(
            'paid_supply_response.json',
            object_hook=json_util.VarHook(variables),
        )

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert _mock_v2_prepare.has_calls
    assert _mock_v2_calc_paid_supply.has_calls
    assert response.status_code == 200

    resp = response.json()

    if paid_supply_paid_cancel_price:
        for level in resp['service_levels']:
            assert (
                'paid_options' in level
                and 'order_popup_properties' in level['paid_options']
            )

    assert 'offer' in resp
    offer_id = resp['offer']
    offer = utils.get_offer(
        offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1
    assert offer

    assert 'prices' in offer
    for item in offer['prices']:
        if item['cls'] == 'business':
            if expected_paid_cancel_in_driving_price is None:
                assert 'paid_cancel_in_driving' not in item
                continue
            assert 'paid_cancel_in_driving' in item
            paid_cancel_in_driving = item['paid_cancel_in_driving']
            assert (
                paid_cancel_in_driving['price']
                == expected_paid_cancel_in_driving_price
            )
            assert paid_cancel_in_driving['for_paid_supply'] == (
                paid_supply_paid_cancel_price is not None
            )


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.user_experiments('fixed_price', 'no_cars_order_available')
@pytest.mark.experiments3(filename='exp3_plugin_decoupling.json')
@pytest.mark.experiments3(filename='exp3_eta_from_driver_eta.json')
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_can_notify_about_paid_cancel.json')
@pytest.mark.config(
    NO_CARS_ORDER_MIN_VERSIONS={'android': {'version': [3, 45, 0]}},
    NO_CARS_ORDER_AVAILABLE_BY_ZONES=['moscow'],
)
@pytest.mark.parametrize(
    'paid_supply_paid_cancel_price,'
    'paid_cancel_price,'
    'expected_paid_cancel_in_driving_price',
    [
        (None, None, None),
        ((321.0, 123.0), None, (321.0, 123.0)),
        ((321.0, None), None, (321.0, 0.0)),
        ((321.0, None), (None, 123.0), (321.0, 0.0)),
    ],
    ids=[
        'no_paid_cancel_in_driving',
        'both_paid_cancel_of_paid_supply',
        'only_driver_paid_cancel_of_paid_supply',
        'different_emits',
    ],
)
@ORDER_OFFERS_SAVE_SWITCH
def test_paid_cancel_in_driving_with_decoupling(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        mock_order_offers,
        order_offers_save_enabled,
        paid_supply_paid_cancel_price,
        paid_cancel_price,
        expected_paid_cancel_in_driving_price,
):
    # from test_routestats.py::test_explicit_antisurge
    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        pass

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def _mock_surge_get_surge(request):
        res = utils.get_surge_calculator_response(request, 1)
        for class_info in res['classes']:
            if class_info['name'] == 'econom':
                class_info['explicit_antisurge'] = {'value': 0.3}
                class_info['value'] = 0.8
                class_info['base_surge'] = {'value': 1.01}
                class_info['value_smooth_b'] = 1.0
                break
        return res

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        req = json.loads(request.get_data())
        if 'extended_radius' in req and req['extended_radius']:
            return load_json('driver_eta_extended_radius.json')
        else:
            return load_json('driver_eta.json')

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        driver_idx = 0
        user_idx = 1

        driver_meta = {}
        user_meta = {}
        if paid_cancel_price and paid_cancel_price[driver_idx]:
            driver_meta['paid_cancel_price'] = paid_cancel_price[driver_idx]
        if paid_cancel_price and paid_cancel_price[user_idx]:
            user_meta['paid_cancel_price'] = paid_cancel_price[user_idx]

        variables = {'driver_meta': driver_meta, 'user_meta': user_meta}
        return load_json(
            'pdp_response.json', object_hook=json_util.VarHook(variables),
        )

    @mockserver.json_handler('/pricing_data_preparer/v2/calc_paid_supply')
    def _mock_v2_calc_paid_supply(request):
        driver_idx = 0
        user_idx = 1

        driver_paid_supply_meta = {}
        driver_meta = {}
        user_paid_supply_meta = {}
        user_meta = {}
        if (
                paid_supply_paid_cancel_price
                and paid_supply_paid_cancel_price[driver_idx]
        ):
            driver_paid_supply_meta[
                'paid_supply_paid_cancel_in_driving_price'
            ] = paid_supply_paid_cancel_price[driver_idx]
        if (
                paid_supply_paid_cancel_price
                and paid_supply_paid_cancel_price[user_idx]
        ):
            user_paid_supply_meta[
                'paid_supply_paid_cancel_in_driving_price'
            ] = paid_supply_paid_cancel_price[user_idx]
        if paid_cancel_price and paid_cancel_price[driver_idx]:
            driver_paid_supply_meta[
                'paid_cancel_in_driving_price'
            ] = paid_cancel_price[driver_idx]
            driver_meta['paid_cancel_in_driving_price'] = paid_cancel_price[
                driver_idx
            ]
        if paid_cancel_price and paid_cancel_price[user_idx]:
            user_paid_supply_meta[
                'paid_cancel_in_driving_price'
            ] = paid_cancel_price[user_idx]
            user_meta['paid_cancel_in_driving_price'] = paid_cancel_price[
                user_idx
            ]

        variables = {
            'driver_paid_supply_meta': driver_paid_supply_meta,
            'user_paid_supply_meta': user_paid_supply_meta,
            'driver_meta': driver_meta,
            'user_meta': user_meta,
        }
        return load_json(
            'paid_supply_response.json',
            object_hook=json_util.VarHook(variables),
        )

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert _mock_v2_prepare.has_calls
    assert _mock_v2_calc_paid_supply.has_calls
    assert response.status_code == 200

    resp = response.json()
    assert 'offer' in resp
    offer_id = resp['offer']
    offer = utils.get_offer(
        offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1
    assert offer

    assert 'extra_data' in offer
    assert 'decoupling' in offer['extra_data']
    decoupling = offer['extra_data']['decoupling']
    assert 'success' in decoupling and decoupling['success']
    assert 'driver' in decoupling and 'user' in decoupling

    driver_idx = 0
    user_idx = 1

    for subject in ('driver', 'user'):
        assert 'prices' in decoupling[subject]
        idx = driver_idx if subject == 'driver' else user_idx
        for item in decoupling[subject]['prices']:
            if item['cls'] == 'business':
                if expected_paid_cancel_in_driving_price is None or (
                        expected_paid_cancel_in_driving_price[idx] is None
                ):
                    assert 'paid_cancel_in_driving' not in item
                    continue
                assert 'paid_cancel_in_driving' in item
                paid_cancel_in_driving = item['paid_cancel_in_driving']
                assert (
                    paid_cancel_in_driving['price']
                    == expected_paid_cancel_in_driving_price[idx]
                )
                assert paid_cancel_in_driving['for_paid_supply'] == (
                    (paid_supply_paid_cancel_price is not None)
                    and (paid_supply_paid_cancel_price[driver_idx] is not None)
                )


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.user_experiments('fixed_price')
@pytest.mark.experiments3(filename='exp3_plugin_offer_coupon.json')
@pytest.mark.parametrize('valid_coupon', [True, False])
@ORDER_OFFERS_SAVE_SWITCH
def test_valid_coupon(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        mock_order_offers,
        order_offers_save_enabled,
        valid_coupon,
):
    # from test_routestats.py::test_explicit_antisurge
    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        pass

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def _mock_surge_get_surge(request):
        res = utils.get_surge_calculator_response(request, 1)
        for class_info in res['classes']:
            if class_info['name'] == 'econom':
                class_info['explicit_antisurge'] = {'value': 0.3}
                class_info['value'] = 0.8
                class_info['base_surge'] = {'value': 1.01}
                class_info['value_smooth_b'] = 1.0
                break
        return res

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta.json')

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        req = json.loads(request.get_data())
        assert 'user_info' in req and 'payment_info' in req['user_info']
        payment_info = req['user_info']['payment_info']
        assert 'coupon' in payment_info and payment_info['coupon']
        variables = {'valid_coupon': valid_coupon}
        return load_json(
            'pdp_response.json', object_hook=json_util.VarHook(variables),
        )

    request = load_json('request.json')
    headers = {
        'User-Agent': (
            'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
        ),
    }

    response = taxi_protocol.post('3.0/routestats', request, headers=headers)
    assert _mock_v2_prepare.has_calls
    assert response.status_code == 200

    resp = response.json()
    assert 'coupon' in resp
    coupon = resp['coupon']
    assert 'valid' in coupon and coupon['valid'] == valid_coupon

    assert 'offer' in resp
    offer_id = resp['offer']
    offer = utils.get_offer(
        offer_id, db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1

    assert offer and 'extra_data' in offer
    assert 'coupon' in offer['extra_data']
    coupon = offer['extra_data']['coupon']
    assert 'valid' in coupon and coupon['valid'] == valid_coupon


@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.config(
    DEFAULT_URGENCY=600,
    ALL_CATEGORIES=['econom', 'drive', 'business'],
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom', 'drive', 'business'],
    },
    TARIFF_CATEGORIES_ORDER_FLOW={'drive': {'order_flow': 'drive'}},
    FLOWS_WITHOUT_DECOUPLING_RESTRICTIONS=['drive'],
)
@pytest.mark.experiments3(filename='exp3_plugin_decoupling.json')
@pytest.mark.filldb(tariffs='with_drive', tariff_settings='with_drive')
def test_drive_is_active(
        taxi_protocol,
        load_json,
        mockserver,
        db,
        pricing_data_preparer,
        now,
        config,
):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1.0)

    @mockserver.json_handler('/surger/create_pin')
    def mock_surge_create_pin(request):
        pass

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        return load_json('driver_eta.json')

    pricing_data_preparer.set_fixed_price(enable=True)
    pricing_data_preparer.set_driver_surge(1.0)
    pricing_data_preparer.set_corp_decoupling(enable=True)
    pricing_data_preparer.set_decoupling(enable=True, category='econom')
    pricing_data_preparer.set_decoupling(enable=False, category='comfort')
    pricing_data_preparer.set_decoupling(enable=False, category='drive')
    pricing_data_preparer.set_user_category_prices_id(
        category_prices_id='d/585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11/'
        + '5f40b7f324414f51a1f9549c65211ea5',
        category_id='5f40b7f324414f51a1f9549c65211ea5',
        tariff_id='585a6f47201dd1b2017a0eab-'
        '507000939f17427e951df9791573ac7e-'
        '7fc5b2d1115d4341b7be206875c40e11',
    )

    pricing_data_preparer.set_driver_category_prices_id(
        category_prices_id='c/b7c4d5f6aa3b40a3807bb74b3bc042af',
        category_id='b7c4d5f6aa3b40a3807bb74b3bc042af',
    )
    request = load_json('drive_is_active/request.json')
    response = taxi_protocol.post('3.0/routestats', request)
    response_json = response.json()
    drive_tariff = next(
        (
            service_level
            for service_level in response_json['service_levels']
            if service_level['class'] == 'drive'
        ),
        None,
    )
    assert 'tariff_unavailable' not in drive_tariff

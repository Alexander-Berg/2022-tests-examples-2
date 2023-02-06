# pylint: disable=too-many-lines

import copy
import json

import pytest

from tests_plugins import json_util

from tests_ridehistory import common


CHECK_VIEWS = pytest.mark.parametrize(
    'need_item_view, req_need_item_view',
    [(False, None), (False, False), (True, True)],
    ids=[
        'item_view_unspecified',
        'item_view_not_requested',
        'item_view_requested',
    ],
)


def add_view(request, req_need_item_view):
    result = copy.deepcopy(request)

    if req_need_item_view is None:
        return result

    if 'settings' not in result:
        result['settings'] = {}

    result['settings']['need_item_view'] = req_need_item_view

    return result


def check_headers(headers):
    assert 'X-Yandex-UID' in headers
    assert 'X-Request-Language' in headers
    assert 'X-YaTaxi-PhoneId' in headers
    uid = headers['X-Yandex-UID']
    phone_id = headers['X-YaTaxi-PhoneId']
    locale = headers['X-Request-Language']
    assert uid == '12345'
    assert phone_id == '777777777777777777777777'
    assert locale == 'ru'


def get_yamaps_vars(request, load_json):
    translations = load_json('localizeaddress_config.json')
    rtranslations = translations[request.args['lang']]
    yamaps_vars = None
    if 'uri' in request.args:
        yamaps_vars = rtranslations['uri'][request.args['uri']]
    elif 'll' in request.args and 'text' in request.args:
        if request.args['text'] == request.args['ll']:
            for item in rtranslations['point']:
                if item['ll'] == request.args['ll']:
                    yamaps_vars = item
                    break
        else:
            yamaps_vars = rtranslations['text'][request.args['text']]
    elif 'business_oid' in request.args:
        yamaps_vars = rtranslations['oid'][request.args['business_oid']]
    else:
        assert None, 'Bad request'
    assert yamaps_vars
    return yamaps_vars


async def make_request(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_cardstorage,
        mock_unique_drivers,
        mock_driver_ratings,
        check_pg_queries,
        need_item_view,
        req_need_item_view,
        is_sdc_phone_substitution_enabled,
        check_pg_tp_times_called,
):
    override_tariff = (
        'selfdriving' if is_sdc_phone_substitution_enabled else None
    )
    yt_mock = mock_yt_queries(
        'expected_yt_request_simple', override_tariff=override_tariff,
    )
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple',
        need_item_view,
        override_tariff=override_tariff,
    )
    transactions_mock = mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])
    driver_profiles_mock = mock_driver_profiles('driver_profiles.json')
    parks_replica_mock = mock_parks_replica('parks.json', need_item_view)
    personal_phones_mock = mock_personal_phones('personal_phones.json')
    tps = check_pg_queries('expected_pg_queries_simple.json')
    mock_territories(True)

    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    if need_item_view:
        cardstorage_mock = mock_cardstorage(
            '12345', 'card-x666', 'cardstorage_resp_simple.json',
        )
        unique_drivers_mock = mock_unique_drivers(
            'parkid_driver_uuid',
            {
                'uniques': [
                    {
                        'park_driver_profile_id': 'parkid_driver_uuid',
                        'data': {'unique_driver_id': 'unique_driver_id'},
                    },
                ],
            },
        )
        driver_ratings_mock = mock_driver_ratings(
            'unique_driver_id', '777.000',
        )

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    if need_item_view:
        assert cardstorage_mock.times_called == 1
        assert unique_drivers_mock.times_called == 2
        assert driver_ratings_mock.times_called == 2

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 1
    assert transactions_mock.times_called == 1
    assert taxi_tariffs_mock.times_called == 2
    assert driver_profiles_mock.times_called == 1
    assert parks_replica_mock.times_called == 1
    assert (
        personal_phones_mock.times_called == 0
        if is_sdc_phone_substitution_enabled
        else 1
    )
    check_pg_tp_times_called(tps)

    return override_tariff, response


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.translations(
    client_messages={
        'orderhistory.charged': {'ru': '%(CARD_NUMBER)s'},
        'orderhistory.paid_by_cash': {'ru': 'Наличные'},
    },
)
@pytest.mark.parametrize(
    'is_sdc_phone_substitution_enabled',
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='experiments3_self_driving_settings.json',
            ),
        ),
    ],
    ids=['no_sub_sdc_phone', 'sub_sdc_phone'],
)
@CHECK_VIEWS
async def test_simple(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_cardstorage,
        mock_unique_drivers,
        mock_driver_ratings,
        check_pg_queries,
        check_pg_tp_times_called,
        need_item_view,
        req_need_item_view,
        check_response,
        is_sdc_phone_substitution_enabled,
):

    override_tariff, response = await make_request(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_cardstorage,
        mock_unique_drivers,
        mock_driver_ratings,
        check_pg_queries,
        need_item_view,
        req_need_item_view,
        is_sdc_phone_substitution_enabled,
        check_pg_tp_times_called,
    )

    assert response.status == 200

    def get_expected_response(fname):
        expected_response = load_json(fname)
        if is_sdc_phone_substitution_enabled:
            exp = load_json('experiments3_self_driving_settings.json')[
                'configs'
            ][0]
            for order in expected_response['orders']:
                order[
                    'tariff_class'
                ] = override_tariff  # TODO fix localization
                order['tariff_internal_name'] = override_tariff
                order['driver']['call_mode'] = 'direct'
                if order['order_id'] == '77777777777777777777777777777777':
                    order['driver']['phone'] = next(
                        filter(
                            lambda c: c['title'] == 'bishkek', exp['clauses'],
                        ),
                    )['value']['phone']
                else:
                    order['driver']['phone'] = exp['default_value']['phone']
        return expected_response

    expected_response_1 = get_expected_response('expected_resp_simple.json')
    check_response(response, expected_response_1, need_item_view)
    if need_item_view:
        expected_response_2 = get_expected_response(
            'expected_resp_simple_item.json',
        )
        assert response.json() == expected_response_2


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.translations(
    client_messages={
        'orderhistory.charged': {'ru': '%(CARD_NUMBER)s'},
        'orderhistory.paid_by_cash': {'ru': 'Наличные'},
    },
)
@pytest.mark.parametrize(
    'hide_driver_details',
    [
        {
            'enabled': False,
            'hide_phone_zones': ['moscow', 'bishkek', 'saratov'],
        },
        pytest.param(
            {
                'enabled': True,
                'hide_phone_zones': ['moscow', 'bishkek', 'saratov'],
            },
            marks=pytest.mark.experiments3(
                filename='experiments3_selfdriving_hide_driver_details.json',
            ),
        ),
        pytest.param(
            {
                'enabled': True,
                'hide_phone_zones': ['moscow', 'bishkek', 'saratov'],
            },
            marks=[
                pytest.mark.experiments3(
                    filename='experiments3_selfdriving_hide_driver_details.json',  # noqa: E501
                ),
                pytest.mark.experiments3(
                    filename='experiments3_self_driving_settings.json',
                ),
            ],
        ),
    ],
    ids=['sdc_show_driver', 'sdc_hide_driver', 'sdc_hide_driver_and_phone'],
)
@CHECK_VIEWS
async def test_hide_driver(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_cardstorage,
        mock_unique_drivers,
        mock_driver_ratings,
        check_pg_queries,
        check_pg_tp_times_called,
        need_item_view,
        req_need_item_view,
        check_response,
        hide_driver_details,
):
    override_tariff, response = await make_request(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        mock_cardstorage,
        mock_unique_drivers,
        mock_driver_ratings,
        check_pg_queries,
        need_item_view,
        req_need_item_view,
        hide_driver_details['enabled'],
        check_pg_tp_times_called,
    )

    assert response.status == 200

    def get_expected_response(fname):
        expected_response = load_json(fname)
        if hide_driver_details['enabled']:
            for order in expected_response['orders']:
                order[
                    'tariff_class'
                ] = override_tariff  # TODO fix localization
                order['tariff_internal_name'] = override_tariff
                rating = order['driver'].get('rating')
                if hide_driver_details['hide_phone_zones'] == [
                        'moscow',
                        'bishkek',
                        'saratov',
                ]:
                    order['driver'] = {'call_mode': 'no_call'}
                else:
                    exp = load_json('experiments3_self_driving_settings.json')[
                        'configs'
                    ][0]
                    order['driver'] = {'call_mode': 'direct'}
                    if order['order_id'] == '77777777777777777777777777777777':
                        order['driver']['phone'] = next(
                            filter(
                                lambda c: c['title'] == 'bishkek',
                                exp['clauses'],
                            ),
                        )['value']['phone']
                    else:
                        order['driver']['phone'] = exp['default_value'][
                            'phone'
                        ]
                if rating:
                    order['driver']['rating'] = rating
        return expected_response

    expected_response_1 = get_expected_response('expected_resp_simple.json')
    check_response(response, expected_response_1, need_item_view)
    if need_item_view:
        expected_response_2 = get_expected_response(
            'expected_resp_simple_item.json',
        )
        assert response.json() == expected_response_2


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_localize_route_points_safe(
        taxi_ridehistory,
        mockserver,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_zones_v2_empty,
        need_item_view,
        req_need_item_view,
        check_response,
):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_geosearch(request):
        return mockserver.make_response(status=500)

    mock_yt_queries('expected_yt_request_simple')
    mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple_with_org',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_lrp_safe.json', need_item_view)

    assert mock_geosearch.times_called > 0


@pytest.mark.parametrize('method', ['uri', 'full_text', 'point'])
@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_simple_yamaps_only(
        taxi_ridehistory,
        mockserver,
        load_json,
        yamaps,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_zones_v2_empty,
        method,
        need_item_view,
        req_need_item_view,
        check_response,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        yamaps_vars = get_yamaps_vars(request, load_json)
        if 'uri' in request.args and method != 'uri':
            yamaps_vars['point'] = [0.0, 0.0]
        elif 'll' in request.args and 'text' in request.args:
            by_full_text = request.args['text'] != request.args['ll']
            if by_full_text and method == 'point':
                yamaps_vars['point'] = [0.0, 0.0]
        elif 'business_id' in request.args and method != 'uri':
            yamaps_vars['point'] = [0.0, 0.0]
        return [
            load_json(
                'yamaps_response_default.json',
                object_hook=json_util.VarHook(yamaps_vars),
            ),
        ]

    yt_mock = mock_yt_queries('expected_yt_request_simple')
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple_with_org',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(
        response, 'expected_resp_simple_yamaps.json', need_item_view,
    )

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 1
    assert transactions_mock.times_called == 1
    assert taxi_tariffs_mock.times_called == 2


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_simple_with_pp(
        taxi_ridehistory,
        mockserver,
        load_json,
        mock_yamaps_default,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        yamaps,
        need_item_view,
        req_need_item_view,
        check_response,
):
    @mockserver.json_handler('/special-zones/special-zones/v1/localize')
    def _mock_zones_localize(request):
        check_headers(request.headers)
        response = {}
        data = json.loads(request.get_data())
        if data['uris'][0] == 'ytpp://ZoneName_2/PointName_2':
            response['results'] = [
                {
                    'zone_name': 'SVO',
                    'zone_type': 'airport',
                    'point_name': 'Pillar 11',
                    'choice_name': 'Terminal E',
                },
            ]
        elif data['uris'][0] == 'ytpp://ZoneName_1/PointName_1':
            response['results'] = [
                {
                    'zone_name': 'Luzhniki',
                    'zone_type': 'fan_zone',
                    'point_name': 'Entrance 5',
                },
            ]
        else:
            assert False, 'Bad request'
        return response

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones_v2(request):
        check_headers(request.headers)
        point = json.loads(request.get_data())['geopoint']
        if point == [37.64264064473475, 55.73587651244158]:
            return load_json('response_zones_v2_destination.json')
        if point == [37.64295455983948, 55.73485044101388]:
            return load_json('response_zones_v2_source.json')
        assert False, f'Bad request: {point}'
        return {}

    yt_mock = mock_yt_queries('expected_yt_request_simple_with_pp')
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple_with_pp',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(
        response, 'expected_resp_simple_with_pp.json', need_item_view,
    )

    assert _mock_zones_localize.times_called == 2
    assert _mock_zones_v2.times_called == 2
    assert yamaps.times_called() == 4
    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 1
    assert transactions_mock.times_called == 1
    assert taxi_tariffs_mock.times_called == 2


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_hidden_orders.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_hidden_orders(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        need_item_view,
        req_need_item_view,
        check_response,
):
    driver_profiles_mock = mock_driver_profiles('driver_profiles.json')
    yt_mock = mock_yt_queries('expected_yt_request_hidden_orders')
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_hidden_orders',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        ['77777777777777777777777777777777'],
        'transactions_resp_hidden_orders',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view({}, req_need_item_view),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'en',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(
        response, 'expected_resp_hidden_orders.json', need_item_view,
    )

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 1
    assert transactions_mock.times_called == 1
    assert taxi_tariffs_mock.times_called == 1
    assert driver_profiles_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_hidden_orders_pt.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'include_hidden_orders, order_core_times_called, '
    'transactions_times_called, expected_yt_request, expected_resp',
    [
        pytest.param(
            False,
            1,
            1,
            'expected_yt_request_hidden_orders_pt',
            'expected_resp_hidden_orders_pt.json',
        ),
        pytest.param(
            True,
            2,
            2,
            'expected_yt_request_hidden_orders_pt_off',
            'expected_resp_hidden_orders_pt_off.json',
        ),
    ],
)
@CHECK_VIEWS
async def test_hidden_orders_payment_tech(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        include_hidden_orders,
        order_core_times_called,
        transactions_times_called,
        expected_yt_request,
        expected_resp,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries(expected_yt_request)
    order_core_mock = mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'order_core_resp_hidden_orders',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_hidden_orders',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'payment_tech': {
                    'payment_tech_type': 'coop_account',
                    'payment_method_id': 'family-666',
                },
                'settings': {'include_hidden_orders': include_hidden_orders},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'en',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, expected_resp, need_item_view)

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == order_core_times_called
    assert transactions_mock.times_called == transactions_times_called
    assert taxi_tariffs_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_order_archived.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_order_archived(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries('expected_yt_request_order_archived')
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_order_archived',
        need_item_view,
    )
    mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_order_archived',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['saratov', 'bishkek'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view({}, req_need_item_view),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(
        response, 'expected_resp_order_archived.json', need_item_view,
    )

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 2
    assert taxi_tariffs_mock.times_called == 2


@pytest.mark.now('2017-09-10T00:00:00+0300')
@pytest.mark.pgsql(
    'ridehistory', files=['ridehistory_phone_id_expiration.sql'],
)
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_PHONE_ID_EXPIRATION_TIMEOUT_DAYS=1,
)
@CHECK_VIEWS
async def test_phone_id_expiration(
        taxi_ridehistory,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_yt_queries,
        need_item_view,
        req_need_item_view,
):
    yt_mock = mock_yt_queries('expected_yt_request_phone_id_expiration')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json() == {'orders': []}

    assert yt_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_user_uid.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_YANDEX_UID_SEARCH_ENABLED=True,
)
@CHECK_VIEWS
async def test_user_uid(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        check_pg_queries,
        check_pg_tp_times_called,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries('expected_yt_request_user_uid')
    order_core_mock = mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777766',
        ],
        'order_core_resp_user_uid',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777766',
        ],
        'transactions_resp_user_uid',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek'])
    tps = check_pg_queries('expected_pg_queries_user_uid.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_user_uid.json', need_item_view)

    assert yt_mock.times_called == 2
    assert order_core_mock.times_called == 2
    assert transactions_mock.times_called == 2
    assert taxi_tariffs_mock.times_called == 1
    check_pg_tp_times_called(tps)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_no_localizeaddress.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'request_locale, expected_routes, la_times_called',
    [
        ('en', {'source': 'Nachalo pg', 'destination': 'Konec pg'}, 1),
        (
            'ru',
            {
                'source': 'source wo localization',
                'destination': 'destination wo localization',
            },
            0,
        ),
    ],
)
@CHECK_VIEWS
async def test_no_localizeaddress(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        mock_yt_queries_empty,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        request_locale,
        expected_routes,
        la_times_called,
        need_item_view,
        req_need_item_view,
):
    mock_order_core_query(
        ['77777777777777777777777777776666'],
        'order_core_resp_no_localizeaddress',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777776666'],
        'transactions_resp_no_localizeaddress',
    )
    mock_taxi_tariffs_query(['bishkek'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': request_locale,
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    data = response.json()
    order = data['orders'][0]
    if need_item_view:
        order = common.item_view_to_list_view(order)

    assert order['route'] == expected_routes


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql(
    'ridehistory', files=['ridehistory_partial_localizeaddress.sql'],
)
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_partial_localizeaddress(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        mock_yt_queries_empty,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        yamaps,
        need_item_view,
        req_need_item_view,
):
    order_ids = [
        '77777777777777777777777777776666',
        '77777777777777777777777777775555',
        '77777777777777777777777777774444',
        '77777777777777777777777777773333',
        '77777777777777777777777777772222',
    ]
    mock_order_core_query(
        order_ids, 'order_core_resp_partial_localizeaddress', need_item_view,
    )
    mock_transactions_query(
        order_ids, 'transactions_resp_partial_localizeaddress',
    )
    mock_taxi_tariffs_query(['bishkek'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'en',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    data = response.json()
    orders = data['orders']
    if need_item_view:
        orders = [common.item_view_to_list_view(o) for o in orders]

    assert [o['order_id'] for o in orders] == order_ids
    assert [o['route'] for o in orders] == [
        {
            'source': 'source wo localization 6',
            'destination': 'fullname destination wo localization 6',
        },
        {
            'source': 'source wo localization 5',
            'destination': 'destination wo localization 5',
        },
        {'source': 'Another nachalo 4', 'destination': 'Another konec 4'},
        {
            'source': 'source wo localization 3',
            'destination': 'destination wo localization 3',
        },
        {'source': 'Another nachalo 2', 'destination': 'Another konec 2'},
    ]
    assert yamaps.times_called() == 12


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory')
@pytest.mark.config(APPLICATION_MAP_BRAND={})
async def test_no_apps_for_user(taxi_ridehistory):
    response = await taxi_ridehistory.post(
        'v2/list',
        json={
            'include_service_metadata': True,
            'image_tags': {'skin_version': '17'},
        },
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'en',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 500
    assert (
        response.json()['message']
        == 'Failed to fetch fresh data: No apps for 1 brands'
    )


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_bound_uids.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi', 'callcenter': 'yataxi'},
    RIDEHISTORY_YANDEX_UID_SEARCH_ENABLED=True,
)
@pytest.mark.parametrize(
    'bound_uids, order_ids',
    [
        (False, {'77777777777777777777777777777777'}),
        (
            True,
            {
                '77777777777777777777777777777777',
                '77777777777777777777777777777766',
                '77777777777777777777777777777755',
            },
        ),
    ],
)
@CHECK_VIEWS
async def test_bound_uids(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        bound_uids,
        order_ids,
        need_item_view,
        req_need_item_view,
):
    yt_suffix = 'on' if bound_uids else 'off'
    mock_yt_queries(f'expected_yt_request_bound_uids_{yt_suffix}')
    mock_order_core_query(
        order_ids, 'order_core_resp_bound_uids', need_item_view,
    )
    mock_transactions_query(order_ids, 'transactions_resp_bound_uids')
    mock_taxi_tariffs_query(['bishkek'])

    request_headers = {
        'X-Yandex-UID': '1',
        'X-Request-Language': 'en',
        'X-Request-Application': 'app_name=android,app_brand=yataxi',
        'X-YaTaxi-PhoneId': '777777777777777777777777',
    }

    if bound_uids:
        request_headers['X-YaTaxi-Bound-Uids'] = '2,3'

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
                'range': {'results': 10},
            },
            req_need_item_view,
        ),
        headers=request_headers,
    )

    assert response.status == 200

    data = response.json()
    assert {o['order_id'] for o in data['orders']} == order_ids


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_payment.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_payment(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        load_json,
        mock_yt_queries_empty,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        need_item_view,
        req_need_item_view,
        check_response,
):
    order_ids = [
        'finished_cash',
        'paid_cancelled_card',
        'free_cancelled_card',
        'free_cancelled_cash',
        'finished_card',
        'paid_cancelled_cash',
    ]

    mock_order_core_query(order_ids, 'order_core_resp_payment', need_item_view)
    mock_transactions_query(order_ids, 'transactions_resp_payment')
    mock_taxi_tariffs_query(['moscow'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view({'range': {'results': 10}}, req_need_item_view),
        headers={
            'X-Yandex-UID': '1',
            'X-Request-Language': 'en',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_payment.json', need_item_view)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'include_sm, expected_pg_queries',
    [
        (True, 'expected_pg_queries_simple.json'),
        (False, 'expected_pg_queries_older_than.json'),
    ],
)
@pytest.mark.parametrize(
    'yt_empty, pg_empty',
    [
        pytest.param(
            True,
            False,
            marks=pytest.mark.pgsql(
                'ridehistory', files=['ridehistory_pagination.sql'],
            ),
        ),
        pytest.param(False, True, marks=pytest.mark.pgsql('ridehistory')),
        pytest.param(
            False,
            False,
            marks=pytest.mark.pgsql(
                'ridehistory', files=['ridehistory_pagination.sql'],
            ),
        ),
    ],
)
@CHECK_VIEWS
async def test_pagination(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        include_sm,
        yt_empty,
        pg_empty,
        expected_pg_queries,
        check_pg_queries,
        check_pg_tp_times_called,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_empty_suffix = 'empty' if yt_empty else 'full'

    all_order_ids = {
        '77777777777777777777777777777777',
        '77777777777777777777777777777776',
        '77777777777777777777777777777775',
        '77777777777777777777777777777774',
    }

    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek'])
    order_core_mock = mock_order_core_query(
        all_order_ids, 'order_core_resp_pagination', need_item_view,
    )
    transactions_mock = mock_transactions_query(
        all_order_ids, 'transactions_resp_pagination',
    )

    curr_order_ids = {
        '77777777777777777777777777777777',
        '77777777777777777777777777777775',
    }

    yt_mock = mock_yt_queries(
        f'expected_yt_request_pagination_1_{yt_empty_suffix}',
    )

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {'include_service_metadata': include_sm, 'range': {'results': 2}},
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    data = response.json()

    if include_sm:
        assert (
            data['service_metadata']['last_order_id']
            == '77777777777777777777777777777777'
        )

    assert {o['order_id'] for o in data['orders']} == curr_order_ids
    assert yt_mock.times_called == 1

    if pg_empty:
        assert order_core_mock.times_called == 0
        assert transactions_mock.times_called == 0
    else:
        assert order_core_mock.times_called == 4
        assert transactions_mock.times_called == 4

    assert taxi_tariffs_mock.times_called == 1

    curr_order_ids = {
        '77777777777777777777777777777776',
        '77777777777777777777777777777774',
    }

    yt_suffix = 'sm' if include_sm else 'wo_sm'
    yt_mock = mock_yt_queries(
        f'expected_yt_request_pagination_2_{yt_empty_suffix}_{yt_suffix}',
    )

    assert data['cursor'] == {
        'created_at': 1504742400,
        'order_id': '77777777777777777777777777777775',
    }

    tps = check_pg_queries(expected_pg_queries)

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': include_sm,
                'range': {'results': 777, 'older_than': data['cursor']},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    data = response.json()

    if include_sm:
        assert (
            data['service_metadata']['last_order_id']
            == '77777777777777777777777777777777'
        )
        assert yt_mock.times_called == 2
    else:
        assert yt_mock.times_called == 1

    if pg_empty:
        assert order_core_mock.times_called == 0
        assert transactions_mock.times_called == 0
    else:
        if include_sm:
            assert order_core_mock.times_called == 8
            assert transactions_mock.times_called == 8
        else:
            assert order_core_mock.times_called == 6
            assert transactions_mock.times_called == 6

    assert {o['order_id'] for o in data['orders']} == curr_order_ids
    assert taxi_tariffs_mock.times_called == 1  # lru cache
    check_pg_tp_times_called(tps)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory')
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_PHONE_ID_SEARCH_ENABLED=False,
)
async def test_no_user_predicate(taxi_ridehistory):
    response = await taxi_ridehistory.post(
        'v2/list',
        json={},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 500
    assert response.json()['message'] == (
        'Failed to fetch pg hidden orders: Neither '
        'phone_id nor user_uid search enabled'
    )


@pytest.mark.now('2017-09-20T00:00:00+0300')
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'second_from_pg, order_ids, suffix',
    [
        pytest.param(
            True,
            ['second', 'fourth', 'fifth'],
            'second',
            marks=pytest.mark.pgsql(
                'ridehistory', files=['ridehistory_merge_second.sql'],
            ),
            id='order_id=second extracted from pg (but exists in yt)',
        ),
        pytest.param(
            False,
            ['fourth', 'fifth'],
            'wo_second',
            marks=pytest.mark.pgsql(
                'ridehistory', files=['ridehistory_merge_wo_second.sql'],
            ),
            id='order_id=second extracted from yt (as is not present in pg)',
        ),
    ],
)
@CHECK_VIEWS
async def test_merge(
        mock_yamaps_default,
        mock_zones_v2_empty,
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        second_from_pg,
        order_ids,
        suffix,
        need_item_view,
        req_need_item_view,
        check_response,
):
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek'])
    order_core_mock = mock_order_core_query(
        order_ids, 'order_core_resp_merge', need_item_view,
    )
    transactions_mock = mock_transactions_query(
        order_ids, 'transactions_resp_merge',
    )
    yt_mock = mock_yt_queries('expected_yt_request_merge')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {'include_service_metadata': True, 'range': {'results': 4}},
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    check_response(
        response, f'expected_resp_merge_{suffix}.json', need_item_view,
    )

    assert yt_mock.times_called == 1

    if second_from_pg:
        assert order_core_mock.times_called == 3
        assert transactions_mock.times_called == 3
    else:
        assert order_core_mock.times_called == 2
        assert transactions_mock.times_called == 2

    assert taxi_tariffs_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_payment_tech.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_payment_tech(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        check_pg_queries,
        check_pg_tp_times_called,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries('expected_yt_request_payment_tech')
    order_core_mock = mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'order_core_resp_simple',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])
    tps = check_pg_queries('expected_pg_queries_payment_tech.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'payment_tech': {
                    'payment_tech_type': 'coop_account',
                    'payment_method_id': 'family-666',
                },
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_payment_tech.json', need_item_view)

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 2
    assert transactions_mock.times_called == 2
    assert taxi_tariffs_mock.times_called == 2
    check_pg_tp_times_called(tps)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_personal_down(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries('expected_yt_request_simple')
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])
    driver_profiles_mock = mock_driver_profiles('driver_profiles.json')
    parks_replica_mock = mock_parks_replica('parks.json', need_item_view)

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(
        response, 'expected_resp_personal_down.json', need_item_view,
    )

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 1
    assert transactions_mock.times_called == 1
    assert taxi_tariffs_mock.times_called == 2
    assert driver_profiles_mock.times_called == 1
    assert parks_replica_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'drivers_config, parks_config, expected_driver',
    [
        (
            'driver_profiles.json',
            'parks.json',
            [
                {
                    'call_mode': 'on_demand',
                    'phone': '+666',
                    'name': 'Александров Борис Юрьевич',
                },
                {
                    'call_mode': 'direct',
                    'phone': '+777',
                    'name': 'Александров Борис Юрьевич',
                },
            ],
        ),
        (
            'driver_profiles.json',
            'empty_list.json',
            [
                {
                    'call_mode': 'on_demand',
                    'name': 'Александров Борис Юрьевич',
                },
                {
                    'call_mode': 'direct',
                    'phone': '+777',
                    'name': 'Александров Борис Юрьевич',
                },
            ],
        ),
        (
            'empty_list.json',
            'parks.json',
            [
                {'call_mode': 'on_demand', 'phone': '+666'},
                {'call_mode': 'direct', 'phone': '+666'},
            ],
        ),
        (
            'empty_list.json',
            'empty_list.json',
            [{'call_mode': 'on_demand'}, {'call_mode': 'no_call'}],
        ),
    ],
)
@CHECK_VIEWS
async def test_no_park_driver(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        drivers_config,
        parks_config,
        expected_driver,
        need_item_view,
        req_need_item_view,
        check_response,
):
    mock_yt_queries('expected_yt_request_simple')
    mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles(drivers_config)
    mock_parks_replica(parks_config, need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    expected_response = load_json('expected_resp_no_park_driver.json')
    for order, driver in zip(expected_response['orders'], expected_driver):
        order['driver'] = driver

    check_response(response, expected_response, need_item_view)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_no_car_info(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries('expected_yt_request_no_car_info')
    order_core_mock = mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_no_car_info',
        need_item_view,
    )
    transactions_mock = mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek', 'saratov'])
    driver_profiles_mock = mock_driver_profiles('driver_profiles.json')
    parks_replica_mock = mock_parks_replica('parks.json', need_item_view)
    personal_phones_mock = mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_no_car_info.json', need_item_view)

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 1
    assert transactions_mock.times_called == 1
    assert taxi_tariffs_mock.times_called == 2
    assert driver_profiles_mock.times_called == 1
    assert parks_replica_mock.times_called == 1
    assert personal_phones_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_call_mode.sql'])
@pytest.mark.config(
    APPLICATION_MAP_BRAND={'android': 'yataxi'},
    RIDEHISTORY_CALL_MODE_ON_DEMAND_IN_COUNTRIES=['rus'],
    RIDEHISTORY_HIDE_PHONE_FOR_CANCELLED_IN_COUNTRIES=['kgz'],
    RIDEHISTORY_HIDE_PHONE_IN_COUNTRIES=['mda'],
)
@CHECK_VIEWS
async def test_call_mode(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries('expected_yt_request_call_mode')
    request_order_ids = [
        f'7777777777777777777777777777777{i}' for i in range(2, 8)
    ]
    order_core_mock = mock_order_core_query(
        request_order_ids, 'order_core_resp_call_mode', need_item_view,
    )
    transactions_mock = mock_transactions_query(
        request_order_ids, 'transactions_resp_call_mode',
    )
    taxi_tariffs_mock = mock_taxi_tariffs_query(
        ['bishkek', 'saratov', 'comrat'],
    )
    driver_profiles_mock = mock_driver_profiles('driver_profiles.json')
    parks_replica_mock = mock_parks_replica('parks.json', need_item_view)
    personal_phones_mock = mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_call_mode.json', need_item_view)

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 6
    assert transactions_mock.times_called == 6
    assert taxi_tariffs_mock.times_called == 3
    assert driver_profiles_mock.times_called == 1
    assert parks_replica_mock.times_called == 1
    assert personal_phones_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_payment_tech.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'filter_by_apps, expected_yt_request, expected_resp',
    [
        (
            True,
            'expected_yt_request_apps_filter',
            'expected_resp_apps_filter.json',
        ),
        (
            False,
            'expected_yt_request_no_apps_filter',
            'expected_resp_no_apps_filter.json',
        ),
    ],
)
@CHECK_VIEWS
async def test_filter_by_apps(
        mock_yamaps_default,
        mock_zones_v2_empty,
        load_json,
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_taxi_tariffs_query,
        filter_by_apps,
        expected_yt_request,
        expected_resp,
        need_item_view,
        req_need_item_view,
        check_response,
):
    request_order_ids = [
        '77777777777777777777777777777777',
        '77777777777777777777777777777776',
    ]

    taxi_tariffs_mock = mock_taxi_tariffs_query(['bishkek'])
    order_core_mock = mock_order_core_query(
        request_order_ids, 'order_core_resp_no_apps_filter', need_item_view,
    )
    transactions_mock = mock_transactions_query(
        request_order_ids, 'transactions_resp_simple',
    )

    yt_mock = mock_yt_queries(expected_yt_request)

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'payment_tech': {
                    'payment_tech_type': 'coop_account',
                    'payment_method_id': 'family-666',
                },
                'settings': {'filter_by_apps': filter_by_apps},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, expected_resp, need_item_view)

    assert yt_mock.times_called == 1
    assert order_core_mock.times_called == 2
    assert transactions_mock.times_called == 2
    assert taxi_tariffs_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_format_currency(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        need_item_view,
        req_need_item_view,
        check_response,
):
    mock_yt_queries('expected_yt_request_simple')
    mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
                'settings': {'format_currency': False},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(
        response, 'expected_resp_format_currency.json', need_item_view,
    )


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'expected_resp',
    [
        pytest.param(
            'expected_resp_show_current_ride.json',
            marks=pytest.mark.config(RIDEHISTORY_SHOW_CURRENT_RIDE=True),
        ),
        pytest.param(
            'expected_resp_empty.json',
            marks=pytest.mark.config(RIDEHISTORY_SHOW_CURRENT_RIDE=False),
        ),
    ],
)
@CHECK_VIEWS
async def test_show_current_ride(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        expected_resp,
        need_item_view,
        req_need_item_view,
        check_response,
):
    mock_yt_queries('expected_yt_request_show_current_ride')
    mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_show_current_ride',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, expected_resp, need_item_view)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_cashback.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_cashback(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        need_item_view,
        req_need_item_view,
        check_response,
):
    mock_yt_queries('expected_yt_request_cashback')
    mock_order_core_query(
        ['77777777777777777777777777777776'],
        'order_core_resp_simple',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777777776'], 'transactions_resp_cashback',
    )
    mock_taxi_tariffs_query(['saratov', 'bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view({}, req_need_item_view),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_cashback.json', need_item_view)


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'admin_images_fname, request_json, expected_image_tag',
    [
        (
            'admin_images_list_simple.json',
            {'image_tags': {'skin_version': '17', 'size_hint': 123}},
            'class_econom_icon_17_bid',
        ),
        ('admin_images_list_simple.json', {}, 'class_econom_icon_5'),
        ('admin_images_list_wo_skin_version.json', {}, 'class_econom_icon'),
        ('admin_images_list_size_hint.json', {}, 'class_placeholder_icon'),
        (
            'admin_images_list_size_hint.json',
            {'image_tags': {'size_hint': 40}},
            'class_econom_icon',
        ),
        ('admin_images_list_empty.json', {}, None),
    ],
)
@CHECK_VIEWS
async def test_image_tags(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_admin_images_custom,
        admin_images_fname,
        request_json,
        expected_image_tag,
        need_item_view,
        req_need_item_view,
):
    mock_admin_images_custom(admin_images_fname)
    await taxi_ridehistory.invalidate_caches()

    mock_yt_queries('expected_yt_request_simple_empty')
    mock_order_core_query(
        ['77777777777777777777777777777777'],
        'order_core_resp_simple',
        need_item_view,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(request_json, req_need_item_view),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    order = response.json()['orders'][0]

    if expected_image_tag:
        assert order['image_tag'] == expected_image_tag
    else:
        assert 'image_tag' not in order


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_no_destinations.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_no_destination(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        need_item_view,
        req_need_item_view,
):
    mock_yt_queries('expected_yt_request_simple_empty')
    mock_order_core_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'order_core_resp_no_destinations',
        need_item_view,
    )
    mock_transactions_query(
        [
            '77777777777777777777777777777777',
            '77777777777777777777777777777776',
        ],
        'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view({}, req_need_item_view),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    orders = response.json()['orders']
    assert {order['order_id'] for order in orders} == {
        '77777777777777777777777777777777',
        '77777777777777777777777777777776',
    }
    for order in orders:
        if need_item_view:
            order = common.item_view_to_list_view(order)

        assert order['route'] == {'source': 'Начало pg'}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_charity_tips.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_charity_tips(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_persey_payments,
        need_item_view,
        req_need_item_view,
        check_response,
):
    pg_orders = [
        'charity_no_tips_transactions',
        'no_charity_tips_transactions',
        'charity_tips_transactions',
        'charity_no_tips_corp',
        'no_charity_tips_corp',
        'charity_tips_corp',
    ]

    mock_yt_queries('expected_yt_request_charity_tips')
    mock_order_core_query(
        pg_orders, 'order_core_resp_charity_tips', need_item_view,
    )
    mock_transactions_query(pg_orders, 'transactions_resp_charity_tips')
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    persey_payments_mock = mock_persey_payments(
        pg_orders, 'persey_payments_resp_charity_tips.json',
    )

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(
            {
                'include_service_metadata': True,
                'image_tags': {'skin_version': '17'},
            },
            req_need_item_view,
        ),
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    check_response(response, 'expected_resp_charity_tips.json', need_item_view)

    assert persey_payments_mock.times_called == 1


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.experiments3(filename='exp3_lucky_query_enabled.json')
@pytest.mark.parametrize(
    [
        'request_json',
        'expected_yt_request',
        'expected_resp',
        'expected_yt_times_called',
    ],
    [
        (
            {'range': {'results': 1}},
            'expected_yt_request_lucky',
            'expected_resp_lucky.json',
            3,
        ),
        (
            {'range': {'results': 1}},
            'expected_yt_request_lucky_empty',
            'expected_resp_empty.json',
            2,
        ),
        (
            {
                'range': {
                    'results': 1,
                    'older_than': {'created_at': 777, 'order_id': '1234'},
                },
            },
            'expected_yt_request_lucky_older_than',
            'expected_resp_lucky.json',
            3,
        ),
        (
            {'range': {'results': 1}},
            'expected_yt_request_lucky_fallback',
            'expected_resp_lucky_fallback.json',
            5,
        ),
        pytest.param(
            {'range': {'results': 1}},
            'expected_yt_request_lucky_hidden_orders',
            'expected_resp_lucky.json',
            3,
            marks=pytest.mark.pgsql(
                'ridehistory', files=['ridehistory_lucky_hidden_orders.sql'],
            ),
        ),
    ],
)
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@CHECK_VIEWS
async def test_lucky_query(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        request_json,
        expected_yt_request,
        expected_resp,
        expected_yt_times_called,
        need_item_view,
        req_need_item_view,
        check_response,
):
    yt_mock = mock_yt_queries(expected_yt_request)
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', need_item_view)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json=add_view(request_json, req_need_item_view),
        headers={
            'X-Yandex-UID': 'uid2',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
            'X-YaTaxi-Bound-Uids': 'uid4',
        },
    )

    assert response.status == 200
    check_response(response, expected_resp, need_item_view)

    assert yt_mock.times_called == expected_yt_times_called


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_move_to_cash.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
async def test_move_to_cash(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
):
    mock_yt_queries('expected_yt_request_simple_empty')
    mock_order_core_query(
        ['77777777777777777777777777777776'],
        'order_core_resp_move_to_cash',
        False,
    )
    mock_transactions_query(
        ['77777777777777777777777777777776'], 'transactions_resp_move_to_cash',
    )
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', False)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json={},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    orders = response.json()['orders']
    assert len(orders) == 1
    assert orders[0]['payment'] == {
        'final_cost': '123\u2006$SIGN$$CURRENCY$',
        'cost': 123.0,
        'currency_code': 'KGS',
    }


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_cargo.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
async def test_filter_cargo(
        taxi_ridehistory,
        load_json,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
):
    mock_yt_queries('expected_yt_request_simple_empty')
    mock_order_core_query(
        ['77777777777777777777777777777777'], 'order_core_resp_cargo', False,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', False)
    mock_personal_phones('personal_phones.json')

    response = await taxi_ridehistory.post(
        'v2/list',
        json={'include_service_metadata': True},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200
    assert response.json() == {'orders': []}


@pytest.mark.now('2017-09-09T00:00:00+0300')
@pytest.mark.pgsql('ridehistory', files=['ridehistory_simple.sql'])
@pytest.mark.config(APPLICATION_MAP_BRAND={'android': 'yataxi'})
@pytest.mark.parametrize(
    'exp_yt_request, order_core_resp, exp_payments',
    [
        (
            'expected_yt_request_user_ride_display_price',
            'order_core_resp_user_ride_display_price',
            {
                '77777777777777777777777777777777': {
                    'cost': 34.5,
                    'currency_code': 'KGS',
                    'final_cost': '34,5 $SIGN$$CURRENCY$',
                },
                '13386de2bb47265d852774a128db6255': {
                    'cost': 231,
                    'currency_code': 'RUB',
                    'final_cost': '231 $SIGN$$CURRENCY$',
                },
            },
        ),
    ],
)
async def test_user_ride_display_price(
        taxi_ridehistory,
        mock_yt_queries,
        mock_order_core_query,
        mock_transactions_query,
        mock_yamaps_default,
        mock_zones_v2_empty,
        mock_taxi_tariffs_query,
        mock_driver_profiles,
        mock_parks_replica,
        mock_personal_phones,
        mock_territories,
        exp_yt_request,
        order_core_resp,
        exp_payments,
):
    mock_yt_queries(exp_yt_request)
    mock_order_core_query(
        ['77777777777777777777777777777777'], order_core_resp, False,
    )
    mock_transactions_query(
        ['77777777777777777777777777777777'], 'transactions_resp_simple',
    )
    mock_taxi_tariffs_query(['bishkek', 'saratov'])
    mock_driver_profiles('driver_profiles.json')
    mock_parks_replica('parks.json', False)
    mock_personal_phones('personal_phones.json')
    mock_territories(True)
    await taxi_ridehistory.invalidate_caches(cache_names=['countries-cache'])

    response = await taxi_ridehistory.post(
        'v2/list',
        json={},
        headers={
            'X-Yandex-UID': '12345',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android,app_brand=yataxi',
            'X-YaTaxi-PhoneId': '777777777777777777777777',
        },
    )

    assert response.status == 200

    response_orders = response.json()['orders']
    assert len(response_orders) == 2
    for order in response_orders:
        assert order['payment'] == exp_payments[order['order_id']]

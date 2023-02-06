# pylint: disable = import-error
from pricing_extended import mocking_base
import pytest

MATCH_DISCOUNTS_DESCRIBE_RESPONSE = {
    'items': [
        {
            'discount_id': '2403',
            'discount_name': 'google_pay_discount_100_rus_1',
            'is_given': False,
            'message': 'Condition payment_method does not match',
        },
        {
            'discount_id': '2405',
            'discount_name': 'korolev_3',
            'is_given': True,
        },
    ],
}

YT_PATCH = {
    'fallbacks': [
        {'service': 'phone', 'status': 'not_used'},
        {'service': 'user', 'status': 'fail'},
        {'service': 'corp_tariffs', 'status': 'not_used'},
        {'service': 'route_with_jams', 'status': 'success'},
        {'service': 'route_without_jams', 'status': 'not_used'},
        {'service': 'surge', 'status': 'success'},
        {'service': 'tags', 'status': 'success'},
        {'service': 'coupons', 'status': 'not_used'},
        {'service': 'discounts', 'status': 'fail'},
    ],
}

TANKER_CONFIG = {
    'patterns': [r'req:(.*)'],
    'tanker': {
        'keyset': 'backend.pricing-admin.detalization_labels',
        'key_prefix': 'prefix.',
    },
}


class DiscountsAdminContext(mocking_base.BasicMock):
    def __init__(self):
        super().__init__()
        self.response = MATCH_DISCOUNTS_DESCRIBE_RESPONSE
        self._expected_request = None

    def set_expected_request(self, request):
        self._expected_request = request

    def check_request(self, request):
        assert self._expected_request == request.json


@pytest.fixture(name='discounts_admin')
def _discounts_admin():
    return DiscountsAdminContext()


@pytest.fixture(name='discounts_admin_mock')
def _discounts_admin_mock(mockserver, discounts_admin):
    class Context:
        @staticmethod
        @mockserver.json_handler('discounts-admin/v1/match-discounts/describe')
        async def match_discounts_describe(request):
            discounts_admin.check_request(request)
            return discounts_admin.process(mockserver)

    return Context()


@pytest.mark.parametrize(
    'order_id, expected_response',
    [
        ('00000000000000000000000000000000', 'expected_response_0.json'),
        ('00000000000000000000000000000003', 'expected_response_3.json'),
        ('00000000000000000000000000000033', 'expected_response_3.json'),
        ('00000000000000000000000000000004', 'expected_response_4.json'),
        ('00000000000000000000000000000005', 'expected_response_5.json'),
        ('00000000000000000000000000000006', 'expected_response_6.json'),
        ('00000000000000000000000000000007', 'expected_response_7.json'),
        ('00000000000000000000000000000008', 'expected_response_8.json'),
        ('00000000000000000000000000000009', 'expected_response_9.json'),
        ('00000000000000000000000000000010', 'expected_response_10.json'),
        ('00000000000000000000000000000011', 'expected_response_11.json'),
        ('00000000000000000000000000000012', 'expected_response_8.json'),
        ('00000000000000000000000000000013', 'expected_response_13.json'),
    ],
    ids=[
        'unexistent_order',  # 0
        'old_antisurge',  # 3
        'new_antisurge',  # 3
        'no_fixed_price',  # 4
        'order_not_in_yt',  # 5
        'paid_supply_without_performer',  # 6
        'canceled_paid_supply',  # 7
        'regular_order_uuid_flow',  # 8
        'paid_supply_uuid_flow',  # 9
        'with_order',  # 10
        'with_two_orders',  # 11
        'regular_But_like_delayed',  # 12
        'with_antifraud',  # 13
    ],
)
@pytest.mark.yt(
    schemas=[
        'yt_v2_prepare_common_schema.yaml',
        'yt_v2_calc_paid_supply_category_schema.yaml',
        'yt_v2_prepare_route_schema.yaml',
        'yt_v2_prepare_category_info_schema.yaml',
        'yt_order_verification_result_schema.yaml',
        'yt_taximeter_order_details_schema.yaml',
        'yt_backend_variables_schema.yaml',
    ],
    dyn_table_data=[
        'yt_v2_prepare_common.yaml',
        'yt_v2_calc_paid_supply_category.yaml',
        'yt_v2_prepare_route.yaml',
        'yt_v2_prepare_category_info.yaml',
        'yt_taximeter_order_details.yaml',
        'yt_order_verification_result.yaml',
        'yt_backend_variables.yaml',
    ],
)
@pytest.mark.config(PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=False)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.now('2020-04-22 12:00:00.0000+03')
async def test_v2_order_calc_ytdata(
        taxi_pricing_admin,
        order_id,
        expected_response,
        load_json,
        order_archive_mock,
        yt_apply_force,
        testpoint,
        mockserver,
):
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    expected_json = load_json(expected_response)

    has_orders = [
        '00000000000000000000000000000010',
        '00000000000000000000000000000011',
        '00000000000000000000000000000013',
    ]

    @testpoint('async_begin')
    async def async_begin(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['async_begin']

    @testpoint('async_running')
    async def _async_reading(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['running']

    @testpoint('common_mid')
    async def _reading_common_mid(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['common_mid']

    @testpoint('reading_common_finished')
    async def reading_common_finished(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['common_full']

    @testpoint('reading_route_begin')
    async def _reading_route_begin(data):
        await reading_common_finished.wait_call()

    @testpoint('route_mid')
    async def _reading_route_mid(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['route_mid']

    @testpoint('reading_route_finished')
    async def reading_route_finished(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['route_full']

    @testpoint('loading_order_finished')
    async def loading_order_finished(data):
        pass

    @testpoint('loading_order_begin')
    async def _loading_order_begin(data):
        if order_id in has_orders:
            await reading_route_finished.wait_call()

    @testpoint('reading_category_begin')
    async def _reading_category_begin(data):
        if order_id in has_orders:
            await loading_order_finished.wait_call()
        else:
            await reading_route_finished.wait_call()

    @testpoint('async_finished')
    async def async_finished(data):
        tp_response = await taxi_pricing_admin.get(
            'v2/order-calc/ytdata',
            headers={'Accept-Language': 'EN'},
            params={'order_id': order_id},
        )
        assert tp_response.status_code == 200
        assert tp_response.json() == expected_json['ready']

    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_yql_run(request):
        return {'id': 'wrong_id'}

    @mockserver.json_handler('/yql/api/v2/operations/wrong_id/share_id')
    def _mock_share_id(request):
        return 'share_id'

    @mockserver.json_handler('/yql/api/v2/operations/wrong_id/results')
    def _mock_yql_res(request):
        return {
            'data': [],
            'errors': [],
            'id': '6048d8cad2b70c8fc3392b72',
            'issues': [],
            'status': 'COMPLETED',
            'updatedAt': '2021-03-10T14:47:27.852Z',
            'version': 1000000,
        }

    # request without reading YT
    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id},
    )
    assert response.status_code == 200
    assert response.json() == expected_json['not_started']

    # main request starting reading YT
    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id, 'query_policy': 'CHECK_CACHE'},
    )
    assert response.status_code == 200
    assert response.json() == expected_json['just_started']

    # waiting while asyncs finished
    if expected_json['not_started']['status'] != 'NOT_AVAILABLE':
        await async_begin.wait_call()
        await async_finished.wait_call()


@pytest.mark.config(PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=True)
async def test_v2_order_calc_ytdata_block(taxi_pricing_admin):
    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': '00000', 'query_policy': 'CHECK_CACHE'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'data_loading_available': {'dynamic': False, 'static': False},
        'offer': {'user': {}, 'driver': {}},
        'orders': [],
        'progress': 0,
        'status': 'NOT_AVAILABLE',
        'error_flags': {
            'common': False,
            'driver_category_info': False,
            'driver_paid_supply': False,
            'driver_route': False,
            'router_parameters_mismatch': False,
            'user_category_info': False,
            'user_paid_supply': False,
            'user_route': False,
            'yt_mongo_data_mismatch': False,
            'user_backend_variables': False,
            'driver_backend_variables': False,
        },
    }


def get_data(pgsql, order_id):
    with pgsql['pricing_data_preparer'].cursor() as cursor:
        fields = (
            'offer_yql_id',
            'order_yql_id',
            'offer_share_link',
            'order_share_link',
        )
        cursor.execute(
            f'SELECT {", ".join(fields)}'
            f' FROM ONLY cache.offers WHERE '
            f'order_id=%s',
            (order_id,),
        )
        db_result = cursor.fetchall()
        return {field: value for field, value in zip(fields, db_result[0])}


@pytest.mark.yt(
    schemas=[
        'yt_v2_prepare_common_schema.yaml',
        'yt_v2_calc_paid_supply_category_schema.yaml',
        'yt_v2_prepare_route_schema.yaml',
        'yt_v2_prepare_category_info_schema.yaml',
        'yt_order_verification_result_schema.yaml',
        'yt_taximeter_order_details_schema.yaml',
        'yt_backend_variables_schema.yaml',
    ],
    dyn_table_data=[
        'yt_v2_prepare_common.yaml',
        'yt_v2_calc_paid_supply_category.yaml',
        'yt_v2_prepare_route.yaml',
        'yt_v2_prepare_category_info.yaml',
        'yt_taximeter_order_details.yaml',
        'yt_order_verification_result.yaml',
        'yt_backend_variables.yaml',
    ],
)
@pytest.mark.parametrize(
    'truncated', [False, True], ids=['normal', 'truncated'],
)
@pytest.mark.config(PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=False)
async def test_v2_order_calc_ytdata_static(
        taxi_pricing_admin,
        load_json,
        order_archive_mock,
        yt_apply,
        mockserver,
        testpoint,
        pgsql,
        truncated,
):
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))
    order_id = '00000000000000000000000000000011'

    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_yql_run(request):
        data = request.json
        if 'common' in data['content']:
            assert (
                data['content'].replace('\n', '')
                == 'PRAGMA yt.TmpFolder="//home/taxi/testsuite/tmp/pricing-ad'
                'min"; PRAGMA yson.DisableStrict;$category = '
                '\'child_tariff\';'
                '$caller_link = \'02000000000000000000000000000011\''
                ';$link = \'f'
                '0000000000000000000000000000011\';$full_common = SELECT * F'
                'ROM hahn.`home/testsuite/pricing-data-preparer-yandex-tax'
                'i-v2-prepare-common-json-log/1d/2020-04-19`WHERE caller_l'
                'ink = $caller_link AND (link = $link OR $link IS NULL);SE'
                'LECT * FROM $full_common;$common = SELECT extra FROM $ful'
                'l_common;$driver_routes = $common.uuids.driver_routes[$ca'
                'tegory];$user_routes = $common.uuids.user_routes[$categor'
                'y];$jams = $common.uuids.route_jams;$no_jams = $common.uu'
                'ids.route_no_jams;SELECT *    FROM hahn.`home/testsuite/p'
                'ricing-data-preparer-yandex-taxi-v2-prepare-route-json-l'
                'og/1d/2020-04-19`     WHERE caller_link = $caller_link   '
                '  AND     (        (`uuid` IN (Yson::ConvertToString($dri'
                'ver_routes),Yson::ConvertToString($user_routes))        A'
                'ND ($driver_routes IS NOT NULL OR $user_routes IS NOT NUL'
                'L) )         OR (`uuid` IN (Yson::ConvertToString($jams), '
                'Yson::ConvertToString($no_jams))        AND ($jams IS NOT '
                'NULL OR $no_jams IS NOT NULL) )        OR($jams IS NULL AN'
                'D $no_jams IS NULL AND $driver_routes IS NULL AND $user_r'
                'outes IS NULL)    );$driver_cat = $common.uuids.driver_ca'
                'tegory[$category];$user_cat = $common.uuids.user_category'
                '[$category];SELECT *FROM hahn.`home/testsuite/pricing-dat'
                'a-preparer-yandex-taxi-v2-prepare-category-info-json-log/'
                '1d/2020'
                '-04-19` WHERE caller_link = $caller_link AND (    (`uuid`'
                ' IN (Yson::ConvertToString($driver_cat), Yson::ConvertToS'
                'tring($user_cat))    AND $driver_cat IS NOT NULL AND $use'
                'r_cat IS NOT NULL)    OR ($driver_cat IS NULL AND $user_c'
                'at IS NULL AND category_name=$category));'
                '$paid_supply = FALSE;'
                'SELECT *FROM hahn.`home/testsuite/pricing-data-preparer'
                '-yandex-taxi-v2-calc-paid-supply-category-json-log/1d/20'
                '20-04-19` WHERE $paid_supply AND caller_link = $caller_'
                'link   AND category_name=$category;'
            )
            return {'id': 'common_yql_id'}
        if 'taximeter' in data['content']:
            assert (
                data['content']
                == 'PRAGMA yt.TmpFolder="//home/taxi/testsuite/tmp/'
                'pricing-admin"; '
                '$order_id=\'00000000000000000000000000000011\';\n'
                'SELECT * FROM hahn.`home/testsuite/pricing-'
                'data-preparer-taximeter-order-details-json-log/1d/2020'
                '-04-19` WHERE order_id=$order_id;\n'
                'SELECT * FROM hahn.`home/testsuite/pricing-'
                'data-preparer-order-verification-result-json-log/1d/2020'
                '-04-19` WHERE order_id=$order_id;\n'
            )
            return {'id': 'taximeter_data_yql_id'}
        return {'id': 'wrong_id'}

    @mockserver.json_handler('/yql/api/v2/operations/common_yql_id/share_id')
    def _mock_common_share_id(request):
        return 'offer_share_id'

    @mockserver.json_handler(
        '/yql/api/v2/operations/taximeter_data_yql_id/share_id',
    )
    def _mock_taximeter_share_id(request):
        return 'order_share_id'

    @testpoint('async_finished')
    async def async_finished(data):
        pass

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id, 'query_policy': 'CHECK_CACHE'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'common': {
            'backend_variables': {
                'user': {
                    'category': '',
                    'category_data': {
                        'corp_decoupling': False,
                        'decoupling': False,
                        'fixed_price': False,
                        'min_paid_supply_price_for_paid_cancel': 0.0,
                        'paid_cancel_waiting_time_limit': 600.0,
                    },
                    'country_code2': '',
                    'exps': {},
                    'payment_type': 'cash',
                    'requirements': {'select': {}, 'simple': []},
                    'rounding_factor': 1.0,
                    'surge_params': {
                        'surcharge': 0.0,
                        'surcharge_alpha': 0.0,
                        'surcharge_beta': 1.0,
                        'value': 1.0,
                        'value_raw': 0.66,
                        'value_smooth': 0.935748815536499,
                    },
                    'tariff': {
                        'boarding_price': 3000.0,
                        'minimum_price': 0.0,
                        'requirement_prices': {
                            'conditioner': 2000.0,
                            'waiting_in_transit': 400.0,
                        },
                        'waiting_price': {
                            'free_waiting_time': 180,
                            'price_per_minute': 400.0,
                        },
                    },
                    'user_data': {
                        'has_cashback_plus': False,
                        'has_yaplus': False,
                    },
                    'user_tags': [],
                    'waypoints_count': 2,
                    'zone': '',
                },
            },
            'category': 'astrakhan : child_tariff',
            'currency': {'precision': 0, 'symbol': '₽'},
            'tariff': {
                'user': {
                    'boarding_price': 89.0,
                    'rides': [
                        {
                            'dist_price_intervals': [
                                {'begin': 2.0, 'price': 6.0},
                            ],
                            'time_price_intervals': [
                                {'begin': 4.0, 'price': 4.0},
                            ],
                            'zone': 'astrakhan',
                        },
                        {
                            'dist_price_intervals': [
                                {'begin': 2.0, 'price': 18.0},
                            ],
                            'time_price_intervals': [
                                {'begin': 4.0, 'price': 4.0},
                            ],
                            'zone': 'suburb',
                        },
                    ],
                },
            },
            'waypoints': [
                {'lat': 46.350519, 'lon': 48.044372},
                {'lat': 46.339191, 'lon': 48.070869},
            ],
        },
        'data_loading_available': {'dynamic': False, 'static': True},
        'offer': {
            'driver': {
                'fixed_price': False,
                'fixed_price_discard_reason': 'NO_POINT_B',
                'metadata': {},
                'total_price': 3000.0,
                'trip_details': {'distance': 0.0, 'time': 0.0},
            },
            'user': {
                'base_price': {
                    'boarding': 3000.0,
                    'distance': 0.0,
                    'time': 0.0,
                    'total': 3000.0,
                },
                'fixed_price': False,
                'fixed_price_discard_reason': 'NO_POINT_B',
                'metadata': {},
                'total_price': 3000.0,
                'trip_details': {'distance': 0.0, 'time': 0.0},
            },
        },
        'flow': 'normal',
        'orders': [
            {
                'driver': {'fixed_price': True, 'total_price': -1.0},
                'user': {
                    'total_price': 886.0,
                    'trip_details': {
                        'total_distance': 24024.0,
                        'total_time': 3796,
                        'user_options': {},
                        'waiting_in_destination_time': -1,
                        'waiting_in_transit_time': -1,
                        'waiting_time': -1,
                    },
                },
            },
        ],
        'progress': 0,
        'status': 'RUNNING',
        'error_flags': {
            'common': False,
            'driver_category_info': False,
            'driver_paid_supply': False,
            'driver_route': False,
            'router_parameters_mismatch': False,
            'user_category_info': False,
            'user_paid_supply': False,
            'user_route': False,
            'yt_mongo_data_mismatch': False,
            'user_backend_variables': False,
            'driver_backend_variables': False,
        },
    }
    await async_finished.wait_call()

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id, 'query_policy': 'LOAD_STATIC'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'common': {
            'backend_variables': {
                'user': {
                    'category': '',
                    'category_data': {
                        'corp_decoupling': False,
                        'decoupling': False,
                        'fixed_price': False,
                        'min_paid_supply_price_for_paid_cancel': 0.0,
                        'paid_cancel_waiting_time_limit': 600.0,
                    },
                    'country_code2': '',
                    'exps': {},
                    'payment_type': 'cash',
                    'requirements': {'select': {}, 'simple': []},
                    'rounding_factor': 1.0,
                    'surge_params': {
                        'surcharge': 0.0,
                        'surcharge_alpha': 0.0,
                        'surcharge_beta': 1.0,
                        'value': 1.0,
                        'value_raw': 0.66,
                        'value_smooth': 0.935748815536499,
                    },
                    'tariff': {
                        'boarding_price': 3000.0,
                        'minimum_price': 0.0,
                        'requirement_prices': {
                            'conditioner': 2000.0,
                            'waiting_in_transit': 400.0,
                        },
                        'waiting_price': {
                            'free_waiting_time': 180,
                            'price_per_minute': 400.0,
                        },
                    },
                    'user_data': {
                        'has_cashback_plus': False,
                        'has_yaplus': False,
                    },
                    'user_tags': [],
                    'waypoints_count': 2,
                    'zone': '',
                },
            },
            'category': 'astrakhan : child_tariff',
            'currency': {'precision': 0, 'symbol': '₽'},
            'tariff': {
                'user': {
                    'boarding_price': 89.0,
                    'rides': [
                        {
                            'dist_price_intervals': [
                                {'begin': 2.0, 'price': 6.0},
                            ],
                            'time_price_intervals': [
                                {'begin': 4.0, 'price': 4.0},
                            ],
                            'zone': 'astrakhan',
                        },
                        {
                            'dist_price_intervals': [
                                {'begin': 2.0, 'price': 18.0},
                            ],
                            'time_price_intervals': [
                                {'begin': 4.0, 'price': 4.0},
                            ],
                            'zone': 'suburb',
                        },
                    ],
                },
            },
            'waypoints': [
                {'lat': 46.350519, 'lon': 48.044372},
                {'lat': 46.339191, 'lon': 48.070869},
            ],
        },
        'data_loading_available': {'dynamic': False, 'static': True},
        'offer': {
            'driver': {
                'fixed_price': False,
                'fixed_price_discard_reason': 'NO_POINT_B',
                'metadata': {},
                'total_price': 3000.0,
                'trip_details': {'distance': 0.0, 'time': 0.0},
            },
            'user': {
                'base_price': {
                    'boarding': 3000.0,
                    'distance': 0.0,
                    'time': 0.0,
                    'total': 3000.0,
                },
                'fixed_price': False,
                'fixed_price_discard_reason': 'NO_POINT_B',
                'metadata': {},
                'total_price': 3000.0,
                'trip_details': {'distance': 0.0, 'time': 0.0},
            },
        },
        'flow': 'normal',
        'orders': [
            {
                'driver': {'fixed_price': True, 'total_price': -1.0},
                'user': {
                    'total_price': 886.0,
                    'trip_details': {
                        'total_distance': 24024.0,
                        'total_time': 3796,
                        'user_options': {},
                        'waiting_in_destination_time': -1,
                        'waiting_in_transit_time': -1,
                        'waiting_time': -1,
                    },
                },
            },
        ],
        'progress': 0,
        'status': 'RUNNING_STATIC',
        'error_flags': {
            'common': False,
            'driver_category_info': False,
            'driver_paid_supply': False,
            'driver_route': False,
            'router_parameters_mismatch': False,
            'user_category_info': False,
            'user_paid_supply': False,
            'user_route': False,
            'yt_mongo_data_mismatch': False,
            'user_backend_variables': False,
            'driver_backend_variables': False,
        },
        'source_info': {
            'offer_link': 'offer_share_id',
            'order_link': 'order_share_id',
        },
    }

    db = get_data(pgsql, order_id)
    assert db['offer_yql_id'] == 'common_yql_id'
    assert db['order_yql_id'] == 'taximeter_data_yql_id'
    assert db['offer_share_link'] == 'offer_share_id'
    assert db['order_share_link'] == 'order_share_id'

    postfix = '_truncated' if truncated else ''

    @mockserver.json_handler('/yql/api/v2/operations/common_yql_id/results')
    def _mock_common_yql_get(request):
        return load_json('full_common_yql{}.json'.format(postfix))

    @mockserver.json_handler(
        '/yql/api/v2/operations/taximeter_data_yql_id/results',
    )
    def _mock_taximeter_yql_get(request):
        return load_json('taximeter_data_yql{}.json'.format(postfix))

    @mockserver.json_handler('/yql/api/v2/table_data')
    def _mock_table_data_yql_get(request):
        data = request.query
        assert data['cluster'] == 'hahn'
        if 'offer' in data['path']:
            return load_json('offer_category_trunc_1.json')
        if 'order' in data['path']:
            return load_json('order_trunc_1.json')
        assert True
        return ''

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id},
    )

    assert response.status_code == 200
    result = response.json()
    for order in result['orders']:
        order['driver']['lighted_metadata'] = sorted(
            order['driver']['lighted_metadata'],
        )
        order['user']['lighted_metadata'] = sorted(
            order['user']['lighted_metadata'],
        )
    assert result == load_json('response_with_static.json')


@pytest.mark.yt(
    schemas=[
        'yt_v2_prepare_common_schema.yaml',
        'yt_v2_calc_paid_supply_category_schema.yaml',
        'yt_v2_prepare_route_schema.yaml',
        'yt_v2_prepare_category_info_schema.yaml',
        'yt_order_verification_result_schema.yaml',
        'yt_taximeter_order_details_schema.yaml',
        'yt_backend_variables_schema.yaml',
    ],
    dyn_table_data=[
        'yt_v2_prepare_common.yaml',
        'yt_v2_calc_paid_supply_category.yaml',
        'yt_v2_prepare_route.yaml',
        'yt_v2_prepare_category_info.yaml',
        'yt_taximeter_order_details.yaml',
        'yt_order_verification_result.yaml',
        'yt_backend_variables.yaml',
    ],
)
@pytest.mark.parametrize(
    'condition',
    [
        'without_discount',
        'regular_order',
        'delayed_order',
        'has_discount_offer_created_at',
        'handler_timed_out',
        'handler_error',
    ],
)
@pytest.mark.config(PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=False)
async def test_v2_order_calc_ytdata_match_discounts_describe(
        taxi_pricing_admin,
        load_json,
        order_archive_mock,
        testpoint,
        discounts_admin,
        discounts_admin_mock,
        condition,
):
    order_proc = load_json('db_order_proc.json')
    order_id = '00000000000000000000000000000001'

    expected_request = {
        'discount_offer_id': '_my_discount_offer_id_',
        'tariff': 'child_tariff',
        'timestamp': '2020-04-20T00:18:53.612+00:00',
    }

    order_doc = next(doc for doc in order_proc if doc['_id'] == order_id)
    discount_data = order_doc['order']['pricing_data'].get('discount_data', {})
    if condition == 'without_discount':
        discount_data.pop('discount_offer_id')
    elif condition == 'regular_order':
        order_doc['order']['request'].pop('due')
        expected_request['timestamp'] = '2020-04-19T23:54:12.576+00:00'
    elif condition == 'has_discount_offer_created_at':
        discount_data[
            'discount_offer_created_at'
        ] = '2020-01-01T12:00:01+00:00'
        expected_request['timestamp'] = '2020-01-01T12:00:01+00:00'
    elif condition == 'delayed_order':
        order_doc['order']['request']['is_delayed'] = True
    elif condition == 'handler_timed_out':
        discounts_admin.must_timeout(always=True)
        expected_request['timestamp'] = '2020-04-19T23:54:12.576+00:00'
    elif condition == 'handler_error':
        discounts_admin.must_crack(always=True)
        expected_request['timestamp'] = '2020-04-19T23:54:12.576+00:00'
    else:
        assert False and 'Not all conditions are processed'

    order_archive_mock.set_order_proc(order_proc)

    discounts_admin.set_expected_request(expected_request)

    @testpoint('async_finished')
    async def _async_finished(data):
        pass

    @testpoint('async_match_discounts_describe_finished')
    async def _async_match_discounts_describe_finished(data):
        pass

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id, 'query_policy': 'CHECK_CACHE'},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'RUNNING'
    assert 'match_discounts_describe' not in data

    await _async_finished.wait_call()
    if condition != 'without_discount':
        await _async_match_discounts_describe_finished.wait_call()

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'READY'
    assert discounts_admin_mock.match_discounts_describe.has_calls == (
        condition != 'without_discount'
    )

    if condition == 'without_discount':
        assert 'match_discounts_describe' not in data.get('error_flags', {})
    elif condition in ('regular_order', 'delayed_order'):
        assert (
            data.get('match_discounts_describe')
            == MATCH_DISCOUNTS_DESCRIBE_RESPONSE
        )
        assert (
            data.get('error_flags', {}).get('match_discounts_describe')
            is False
        )
    elif condition in ('handler_timed_out', 'handler_error'):
        assert 'match_discounts_describe' not in data
        assert (
            data.get('error_flags', {}).get('match_discounts_describe') is True
        )


@pytest.mark.parametrize(
    'is_anonymized', [False, True], ids=['not_anonymized', 'anonymized'],
)
@pytest.mark.yt(
    schemas=[
        'yt_v2_prepare_common_schema.yaml',
        'yt_v2_calc_paid_supply_category_schema.yaml',
        'yt_v2_prepare_route_schema.yaml',
        'yt_v2_prepare_category_info_schema.yaml',
        'yt_order_verification_result_schema.yaml',
        'yt_taximeter_order_details_schema.yaml',
        'yt_backend_variables_schema.yaml',
    ],
    dyn_table_data=[
        'yt_v2_prepare_common.yaml',
        'yt_v2_calc_paid_supply_category.yaml',
        'yt_v2_prepare_route.yaml',
        'yt_v2_prepare_category_info.yaml',
        'yt_taximeter_order_details.yaml',
        'yt_order_verification_result.yaml',
        'yt_backend_variables.yaml',
    ],
)
@pytest.mark.config(PRICING_DATA_PREPARER_BLOCK_V2_OFFER_YTDATA=False)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v2_order_calc_ytdata_anonymized_order(
        taxi_pricing_admin,
        is_anonymized,
        load_json,
        discounts_admin,
        discounts_admin_mock,
        order_archive_mock,
        testpoint,
):
    @testpoint('async_finished')
    async def _async_finished(data):
        pass

    @testpoint('anonymize_response')
    def _anonymize_response(data):
        pass

    order_proc = load_json('db_order_proc.json')
    order_id = '00000000000000000000000000000001'

    order_doc = next(doc for doc in order_proc if doc['_id'] == order_id)
    if is_anonymized:
        order_doc.update({'takeout': {'status': 'anonymized'}})

    order_archive_mock.set_order_proc(order_proc)

    discounts_admin.set_expected_request(
        {
            'discount_offer_id': '_my_discount_offer_id_',
            'tariff': 'child_tariff',
            'timestamp': '2020-04-19T23:54:12.576+00:00',
        },
    )

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id, 'query_policy': 'CHECK_CACHE'},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'RUNNING'
    assert _anonymize_response.has_calls is is_anonymized

    await _async_finished.wait_call()

    response = await taxi_pricing_admin.get(
        'v2/order-calc/ytdata',
        headers={'Accept-Language': 'EN'},
        params={'order_id': order_id},
    )
    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'READY'

    assert _anonymize_response.has_calls == is_anonymized

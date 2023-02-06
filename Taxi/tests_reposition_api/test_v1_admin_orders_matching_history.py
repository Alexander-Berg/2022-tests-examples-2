# pylint: disable=C5521, W0621
import datetime
import json

import pytest
import pytz

from . import yql_services_fixture
from .conftest import USER_AGENT
from .utils import select_named
from .yql_services_fixture import local_yql_services  # noqa: F401


NOW = datetime.datetime(
    2020, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('Europe/Moscow'),
)

MATCH_ORDERS_DIR = 'taxi-test-reposition-matcher-match-orders-drivers-json-log'

MATCH_ORDERS_PATH_HOUR = f'//home/logfeller/logs/{MATCH_ORDERS_DIR}/1h'
MATCH_ORDERS_PATH_DAY = f'//home/logfeller/logs/{MATCH_ORDERS_DIR}/1d'

ORDERS_MATCHING_HISTORY_TABLE = (
    '//home/taxi/testing/features'
    '/reposition/orders_matching_history/tablename'
)

OAUTH = 'OAuth taxi-robot-token'

TEST_SHARED_ID = 'XL15AAlSshlfAw44s4E1lUtwCkmt2cKTumKON1zwgqQ='


QUERY_DAY = """
USE chyt.hahn/robot-reposition-alias;

CREATE TABLE
`//home/taxi/testing/features/reposition/orders_matching_history/order_id_0::2019-12-29T00:00:00::2019-12-30T00:00:00`
engine = YtTable('{expiration_time="2019-12-31T22:30:00"}')
AS

SELECT
    timestamp_check,
    driver_id,
    order_id,
    order_category,
    session_id,
    mode,
    submode,
    formula_type,
    en_route,
    request_kind,

    YPathDouble(order_a, '/lon') AS order_a_lon,
    YPathDouble(order_a, '/lat') AS order_a_lat,
    YPathDouble(order_b, '/lon') AS order_b_lon,
    YPathDouble(order_b, '/lat') AS order_b_lat,
    YPathDouble(driver_position, '/lon') AS driver_position_lon,
    YPathDouble(driver_position, '/lat') AS driver_position_lat,
    YPathDouble(reposition_start_point, '/lon') AS reposition_start_point_lon,
    YPathDouble(reposition_start_point, '/lat') AS reposition_start_point_lat,
    YPathDouble(reposition_point, '/lon') AS reposition_point_lon,
    YPathDouble(reposition_point, '/lat') AS reposition_point_lat,

    da_distance_ratio,
    da_time_ratio,
    home_cancel_prob,
    home_distance_ratio,
    home_time_ratio,
    min_home_distance_ratio,
    min_home_time_ratio,
    min_order_distance,
    min_order_time,
    min_b_surge,
    min_surge_gradient,
    min_b_lrsp_time,
    max_bh_air_dist,
    max_bh_time,

    ab_dist,
    ah_dist,
    bh_dist,
    dh_dist,
    da_dist,
    cda_dist,
    ab_time,
    ah_time,
    bh_time,
    dh_time,
    da_time,
    cda_time,
    blrsp_time,
    b_surge,
    d_surge,
    YPathDouble(area_center, '/lon') AS area_center_lon,
    YPathDouble(area_center, '/lat') AS area_center_lat,
    area_radius,
    ca_air_dist,
    cb_air_dist,
    bh_air_dist,
    dh_time_cmp_coeff,
    sla_a,
    sla_b,
    sla_c,
    sla_d,
    sla_max_coef,
    sla_start_timestamp,
    sla_start_router_time,
    sla_discount_raw,
    sla_discount,
    sla_ride_time,
    sla_left,
    sla_right,
    sla_satisfied,
    score_alpha,
    score
FROM
    concatYtTablesRange(
        '//home/logfeller/logs/taxi-test-reposition-matcher-match-orders-drivers-json-log/1d',
        '2019-12-29',
        '2019-12-30'
    )
WHERE
    order_id = 'order_id_0'
ORDER BY
    timestamp_check ASC
"""

QUERY_HOUR = """
USE chyt.hahn/robot-reposition-alias;

CREATE TABLE
`//home/taxi/testing/features/reposition/orders_matching_history/order_id_0::2019-12-31T19:00:00::2019-12-31T22:00:00`
engine = YtTable('{expiration_time="2019-12-31T22:30:00"}')
AS

SELECT
    timestamp_check,
    driver_id,
    order_id,
    order_category,
    session_id,
    mode,
    submode,
    formula_type,
    en_route,
    request_kind,

    YPathDouble(order_a, '/lon') AS order_a_lon,
    YPathDouble(order_a, '/lat') AS order_a_lat,
    YPathDouble(order_b, '/lon') AS order_b_lon,
    YPathDouble(order_b, '/lat') AS order_b_lat,
    YPathDouble(driver_position, '/lon') AS driver_position_lon,
    YPathDouble(driver_position, '/lat') AS driver_position_lat,
    YPathDouble(reposition_start_point, '/lon') AS reposition_start_point_lon,
    YPathDouble(reposition_start_point, '/lat') AS reposition_start_point_lat,
    YPathDouble(reposition_point, '/lon') AS reposition_point_lon,
    YPathDouble(reposition_point, '/lat') AS reposition_point_lat,

    da_distance_ratio,
    da_time_ratio,
    home_cancel_prob,
    home_distance_ratio,
    home_time_ratio,
    min_home_distance_ratio,
    min_home_time_ratio,
    min_order_distance,
    min_order_time,
    min_b_surge,
    min_surge_gradient,
    min_b_lrsp_time,
    max_bh_air_dist,
    max_bh_time,

    ab_dist,
    ah_dist,
    bh_dist,
    dh_dist,
    da_dist,
    cda_dist,
    ab_time,
    ah_time,
    bh_time,
    dh_time,
    da_time,
    cda_time,
    blrsp_time,
    b_surge,
    d_surge,
    YPathDouble(area_center, '/lon') AS area_center_lon,
    YPathDouble(area_center, '/lat') AS area_center_lat,
    area_radius,
    ca_air_dist,
    cb_air_dist,
    bh_air_dist,
    dh_time_cmp_coeff,
    sla_a,
    sla_b,
    sla_c,
    sla_d,
    sla_max_coef,
    sla_start_timestamp,
    sla_start_router_time,
    sla_discount_raw,
    sla_discount,
    sla_ride_time,
    sla_left,
    sla_right,
    sla_satisfied,
    score_alpha,
    score
FROM
    concatYtTablesRange(
        '//home/logfeller/logs/taxi-test-reposition-matcher-match-orders-drivers-json-log/1h',
        '2019-12-31T19:00:00',
        '2019-12-31T22:00:00'
    )
WHERE
    order_id = 'order_id_0'
ORDER BY
    timestamp_check ASC
"""


YT_DATA = [
    {
        'timestamp_check': NOW.isoformat(),
        'driver_id': 'dbid_uuid0',
        'order_id': 'order_id_0',
        'order_category': 'econom',
        'session_id': 'session_id_0',
        'mode': 'mode_0',
        'submode': 'submode_0',
        'formula_type': 'regular_mode',
        'en_route': False,
        'request_kind': 'buffer-dispatch',
        'order_a_lon': 30.1,
        'order_a_lat': 60.1,
        'order_b_lon': 30.2,
        'order_b_lat': 60.2,
        'driver_position_lon': 30.3,
        'driver_position_lat': 60.3,
        'reposition_start_point_lon': 30.4,
        'reposition_start_point_lat': 60.4,
        'reposition_point_lon': 30.5,
        'reposition_point_lat': 60.5,
        'da_distance_ratio': 1.0,
        'da_time_ratio': 1.0,
        'home_cancel_prob': 0.5,
        'home_distance_ratio': 1.0,
        'home_time_ratio': 1.0,
        'min_home_distance_ratio': 0.0,
        'min_home_time_ratio': 0.0,
        'min_order_distance': 0,
        'min_order_time': 0,
        'min_b_surge': 0.0,
        'min_surge_gradient': 0.0,
        'min_b_lrsp_time': 0.0,
        'max_bh_air_dist': 1024.0,
        'max_bh_time': 256.0,
        'ab_dist': 512.0,
        'ah_dist': 512.0,
        'bh_dist': 512.0,
        'dh_dist': 512.0,
        'da_dist': 512.0,
        'cda_dist': 512.0,
        'ab_time': 128.0,
        'ah_time': 128.0,
        'bh_time': 128.0,
        'dh_time': 128.0,
        'da_time': 128.0,
        'cda_time': 128.0,
        'blrsp_time': 64.0,
        'b_surge': 1.5,
        'd_surge': 1.5,
        'area_center_lon': 30.6,
        'area_center_lat': 60.6,
        'area_radius': 2048.0,
        'ca_air_dist': 1024.0,
        'cb_air_dist': 1024.0,
        'bh_air_dist': 1024.0,
        'dh_time_cmp_coeff': 1.4,
        'sla_a': 1.0,
        'sla_b': 1.0,
        'sla_c': 1.0,
        'sla_d': 1.0,
        'sla_max_coef': 1.0,
        'sla_start_timestamp': NOW.isoformat(),
        'sla_start_router_time': 60.0,
        'sla_discount_raw': 1.0,
        'sla_discount': 1.0,
        'sla_ride_time': 1.0,
        'sla_left': 1.0,
        'sla_right': 1.0,
        'sla_satisfied': False,
        'score_alpha': 1.0,
        'score': 1.0,
    },
]


@pytest.mark.yt(
    schemas=[
        {
            'path': ORDERS_MATCHING_HISTORY_TABLE,
            'attributes': {
                'schema': [
                    {'name': 'timestamp_check', 'type': 'string'},
                    {'name': 'driver_id', 'type': 'string'},
                    {'name': 'order_id', 'type': 'string'},
                    {'name': 'order_category', 'type': 'string'},
                    {'name': 'session_id', 'type': 'string'},
                    {'name': 'mode', 'type': 'string'},
                    {'name': 'submode', 'type': 'string'},
                    {'name': 'formula_type', 'type': 'string'},
                    {'name': 'en_route', 'type': 'boolean'},
                    {'name': 'request_kind', 'type': 'string'},
                    {'name': 'order_a_lon', 'type': 'double'},
                    {'name': 'order_a_lat', 'type': 'double'},
                    {'name': 'order_b_lon', 'type': 'double'},
                    {'name': 'order_b_lat', 'type': 'double'},
                    {'name': 'driver_position_lon', 'type': 'double'},
                    {'name': 'driver_position_lat', 'type': 'double'},
                    {'name': 'reposition_start_point_lon', 'type': 'double'},
                    {'name': 'reposition_start_point_lat', 'type': 'double'},
                    {'name': 'reposition_point_lon', 'type': 'double'},
                    {'name': 'reposition_point_lat', 'type': 'double'},
                    {'name': 'da_distance_ratio', 'type': 'double'},
                    {'name': 'da_time_ratio', 'type': 'double'},
                    {'name': 'home_cancel_prob', 'type': 'double'},
                    {'name': 'home_distance_ratio', 'type': 'double'},
                    {'name': 'home_time_ratio', 'type': 'double'},
                    {'name': 'min_home_distance_ratio', 'type': 'double'},
                    {'name': 'min_home_time_ratio', 'type': 'double'},
                    {'name': 'min_order_distance', 'type': 'uint64'},
                    {'name': 'min_order_time', 'type': 'uint64'},
                    {'name': 'min_b_surge', 'type': 'double'},
                    {'name': 'min_surge_gradient', 'type': 'double'},
                    {'name': 'min_b_lrsp_time', 'type': 'double'},
                    {'name': 'max_bh_air_dist', 'type': 'double'},
                    {'name': 'max_bh_time', 'type': 'double'},
                    {'name': 'ab_dist', 'type': 'double'},
                    {'name': 'ah_dist', 'type': 'double'},
                    {'name': 'bh_dist', 'type': 'double'},
                    {'name': 'dh_dist', 'type': 'double'},
                    {'name': 'da_dist', 'type': 'double'},
                    {'name': 'cda_dist', 'type': 'double'},
                    {'name': 'ab_time', 'type': 'double'},
                    {'name': 'ah_time', 'type': 'double'},
                    {'name': 'bh_time', 'type': 'double'},
                    {'name': 'dh_time', 'type': 'double'},
                    {'name': 'da_time', 'type': 'double'},
                    {'name': 'cda_time', 'type': 'double'},
                    {'name': 'blrsp_time', 'type': 'double'},
                    {'name': 'b_surge', 'type': 'double'},
                    {'name': 'd_surge', 'type': 'double'},
                    {'name': 'area_center_lon', 'type': 'double'},
                    {'name': 'area_center_lat', 'type': 'double'},
                    {'name': 'area_radius', 'type': 'double'},
                    {'name': 'ca_air_dist', 'type': 'double'},
                    {'name': 'cb_air_dist', 'type': 'double'},
                    {'name': 'bh_air_dist', 'type': 'double'},
                    {'name': 'dh_time_cmp_coeff', 'type': 'double'},
                    {'name': 'sla_a', 'type': 'double'},
                    {'name': 'sla_b', 'type': 'double'},
                    {'name': 'sla_c', 'type': 'double'},
                    {'name': 'sla_d', 'type': 'double'},
                    {'name': 'sla_max_coef', 'type': 'double'},
                    {'name': 'sla_start_timestamp', 'type': 'string'},
                    {'name': 'sla_start_router_time', 'type': 'double'},
                    {'name': 'sla_discount_raw', 'type': 'double'},
                    {'name': 'sla_discount', 'type': 'double'},
                    {'name': 'sla_ride_time', 'type': 'double'},
                    {'name': 'sla_left', 'type': 'double'},
                    {'name': 'sla_right', 'type': 'double'},
                    {'name': 'sla_satisfied', 'type': 'boolean'},
                    {'name': 'score_alpha', 'type': 'double'},
                    {'name': 'score', 'type': 'double'},
                ],
            },
        },
    ],
    static_table_data=[
        {'path': ORDERS_MATCHING_HISTORY_TABLE, 'values': YT_DATA},
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql('reposition', files=['matching_history_operations.sql'])
@pytest.mark.parametrize(
    'failed',
    (
        pytest.param(True, id='should fail'),
        pytest.param(False, id='should not fail'),
    ),
)
async def test_get(
        taxi_reposition_api,
        yt_client,
        local_yql_services,  # noqa: F811
        failed,
        pgsql,
        yt_apply_force,
        mockserver,
):
    @mockserver.json_handler('/yql/api/v2/operations/operation_id/results')
    def _operation_status(request):
        return {'id': 'operation_id', 'errors': [{'message': 'Bad operation'}]}

    status = 'COMPLETED' if not failed else 'ERROR'

    local_yql_services.add_status_response(status)
    local_yql_services.add_results_response(
        {
            'id': yql_services_fixture.OPERATION_ID,
            'status': status,
            'data': [{'Write': [{}]}],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        },
    )

    operation_id = yql_services_fixture.OPERATION_ID
    response = await taxi_reposition_api.get(
        f'/v1/admin/orders/matching?operation_id={operation_id}',
    )

    assert local_yql_services.times_called['status'] == 1
    assert local_yql_services.times_called['results'] == 0
    assert local_yql_services.times_called['results_data'] == 0

    if failed:
        assert response.status_code == 500
        assert response.json()['message'].startswith(
            'Bad YQL Operation operation_id',
        )
        return

    assert response.status_code == 200

    expected_response = {
        'matchings': [
            {
                'timestamp': '2019-12-31T21:30:00+00:00',
                'request_kind': 'buffer-dispatch',
                'driver_id': 'dbid_uuid0',
                'order_id': 'order_id_0',
                'order_category': 'econom',
                'session_id': 'session_id_0',
                'mode': 'mode_0',
                'submode': 'submode_0',
                'coordinates': {
                    'driver_position': [30.3, 60.3],
                    'order_a': [30.1, 60.1],
                    'order_b': [30.2, 60.2],
                    'reposition_point': [30.5, 60.5],
                    'reposition_start_point': [30.4, 60.4],
                },
                'formula': {
                    'formula_type': 'regular',
                    'config': {
                        'da_distance_ratio': 1.0,
                        'da_time_ratio': 1.0,
                        'home_cancel_prob': 0.5,
                        'home_distance_ratio': 1.0,
                        'home_time_ratio': 1.0,
                        'min_home_distance_ratio': 0.0,
                        'min_home_time_ratio': 0.0,
                        'min_order_distance': 0,
                        'min_order_time': 0,
                    },
                    'values': {
                        'ab_dist': 512.0,
                        'ab_time': 128.0,
                        'ah_dist': 512.0,
                        'ah_time': 128.0,
                        'bh_dist': 512.0,
                        'bh_time': 128.0,
                        'cda_dist': 512.0,
                        'cda_time': 128.0,
                        'da_dist': 512.0,
                        'da_time': 128.0,
                        'dh_dist': 512.0,
                        'dh_time': 128.0,
                    },
                    'sla': {
                        'data_ride_time': 1.0,
                        'data_start_router_time': 60.0,
                        'data_start_timestamp': '2019-12-31T21:30:00+00:00',
                        'param_a': 1.0,
                        'param_b': 1.0,
                        'param_c': 1.0,
                        'param_d': 1.0,
                        'param_max_coef': 1.0,
                        'result_discount': 1.0,
                        'result_discount_raw': 1.0,
                        'result_is_satisfied': False,
                        'result_left': 1.0,
                        'result_right': 1.0,
                    },
                },
                'score': {'param_alpha': 1.0, 'result_score': 1.0},
                'en_route': False,
            },
        ],
    }

    response_json = response.json()

    assert expected_response == response_json


@pytest.mark.nofilldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'order_datetime,path,query',
    [
        (
            NOW - datetime.timedelta(days=3),
            '//home/taxi/testing/features/reposition/orders_matching_history/order_id_0::2019-12-29T00:00:00::2019-12-30T00:00:00',  # noqa: E501
            QUERY_DAY.replace('\n', '').replace(' ', ''),
        ),
        (
            NOW - datetime.timedelta(hours=3),
            '//home/taxi/testing/features/reposition/orders_matching_history/order_id_0::2019-12-31T19:00:00::2019-12-31T22:00:00',  # noqa: E501
            QUERY_HOUR.replace('\n', '').replace(' ', ''),
        ),
    ],
)
@pytest.mark.yt(
    schemas=[
        {'path': f'{MATCH_ORDERS_PATH_DAY}/2019-12-29', 'attributes': {}},
        {
            'path': f'{MATCH_ORDERS_PATH_HOUR}/2019-12-31T19:00:00',
            'attributes': {},
        },
    ],
)
async def test_retrieve(
        taxi_reposition_api,
        yt_client,
        order_datetime,
        path,
        query,
        mockserver,
        pgsql,
        load_json,
):
    @mockserver.json_handler('/yql/api/v2/operations/operation_id_0/share_id')
    def _share_id_mock(request):
        assert request.headers['Authorization'] == OAUTH
        assert request.headers['User-Agent'] == USER_AGENT

        # add quotes
        return mockserver.make_response(f'"{TEST_SHARED_ID}"', 200)

    @mockserver.json_handler('/yql/api/v2/operations')
    def operations_mock(request):
        assert request.headers['User-Agent'] == USER_AGENT
        assert request.headers['Authorization'] == OAUTH

        requested_data = json.loads(request.get_data())
        requested_data['content'] = (
            requested_data['content'].replace('\n', '').replace(' ', '')
        )

        assert requested_data == {
            'action': 'RUN',
            'content': query,
            'type': 'CLICKHOUSE',
        }

        mock_response = json.dumps(
            {
                'id': f'operation_id_{operations_mock.times_called}',
                'status': 'RUNNING',
            },
        )

        return mockserver.make_response(mock_response, 200)

    data = {
        'order_id': 'order_id_0',
        'order_datetime': order_datetime.isoformat(),
    }

    response = await taxi_reposition_api.post(
        '/v1/admin/orders/matching/request', data,
    )

    assert response.status_code == 200

    response = response.json()
    operation_id = response['operation_id']
    assert operation_id == 'operation_id_0'

    rows = select_named(
        """
        SELECT
            operation_id,
            shared_id,
            path
        FROM
            state.matching_history_operations
        """,
        pgsql['reposition'],
    )

    assert rows == [
        {
            'operation_id': 'operation_id_0',
            'shared_id': TEST_SHARED_ID,
            'path': path,
        },
    ]


@pytest.mark.nofilldb()
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data',
    [({'order_id': 'random', 'order_datetime': 'not timestamp'},), ({})],
)
async def test_admin_bad_history_search_bad_requests(
        taxi_reposition_api, pgsql, data,
):
    response = await taxi_reposition_api.post(
        '/v1/admin/orders/matching/request', data,
    )

    assert response.status_code == 400

    rows = select_named(
        """
            SELECT
                operation_id,
                path,
                valid_until
            FROM
                state.matching_history_operations
        """,
        pgsql['reposition'],
    )

    assert not rows


@pytest.mark.nofilldb()
@pytest.mark.now(NOW.isoformat())
async def test_retrieve_no_tables(taxi_reposition_api, yt_client, mockserver):
    local_from = NOW - datetime.timedelta(days=10)

    data = {'order_id': 'order-id', 'order_datetime': local_from.isoformat()}

    response = await taxi_reposition_api.post(
        '/v1/admin/orders/matching/request', data,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'No tables found at date: 2019-12-22T00:00:00',
    }

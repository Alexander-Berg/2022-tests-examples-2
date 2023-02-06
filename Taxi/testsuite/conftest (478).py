import re
from typing import List
from typing import Optional

import pytest

import maas_types


# root conftest for service maas
pytest_plugins = ['maas_plugins.pytest_plugins']


def _get_pgsql_cursor(pgsql):
    return pgsql['maas'].cursor()


def _get_sub_pgsql_cursor(pgsql, where: str, with_time_fields: bool = False):
    cursor = _get_pgsql_cursor(pgsql)
    if with_time_fields:
        time_fields = ', created_at, expired_at'
    else:
        time_fields = ''
    cursor.execute(
        f'SELECT tariff_info, '
        f'maas_sub_id, status, maas_user_id, phone_id, coupon_id,'
        f'coupon_series_id, status_history, bought_through_go {time_fields} '
        f'FROM maas.subscriptions WHERE {where};',
    )
    return cursor


def _get_order_pgsql_cursor(pgsql, where: str):
    cursor = _get_pgsql_cursor(pgsql)
    cursor.execute(
        f'SELECT order_id, external_order_id, maas_user_id, phone_id, '
        f'maas_sub_id, is_maas_order, maas_trip_id, created_at, updated_at '
        f'FROM maas.orders WHERE {where};',
    )
    return cursor


def _parse_sub_row(row) -> Optional[maas_types.Subscription]:
    try:
        row = list(row)
        row[0] = maas_types.TariffInfo(*row[0][1:-1].split(sep=','))
        status_history = re.findall(r'"\((.*?)\)"', row[7])

        for i, update_status in enumerate(status_history):
            updated_at, new_status, reason = update_status.split(sep=',')
            updated_at = updated_at.strip('\\"')
            reason = reason.strip('\\"')
            status_history[i] = maas_types.StatusHistory(
                updated_at, new_status, reason,
            )
        sub_args = (*row[:7], status_history, *row[8:])
        return maas_types.Subscription(*sub_args)
    except Exception:  # pylint: disable=broad-except
        return None


def _parse_order_row(row) -> Optional[maas_types.Order]:
    try:
        row = list(row)
        return maas_types.Order(*row)
    except Exception:  # pylint: disable=broad-except
        return None


@pytest.fixture(name='get_subscriptions')
def sub_by_status_fixture(pgsql):
    def get_subscriptions_(
            where: str, with_time_fields: bool = False,
    ) -> List[maas_types.Subscription]:
        cursor = _get_sub_pgsql_cursor(pgsql, where, with_time_fields)
        rows = cursor.fetchall()
        subscriptions = []
        for row in rows:
            sub = _parse_sub_row(row)
            if sub:
                subscriptions.append(sub)
        return subscriptions

    return get_subscriptions_


@pytest.fixture(name='get_subscription_by_id')
def sub_by_id_fixture(pgsql):
    def get_subscription_by_id_(
            sub_id: str, with_time_fields: bool = False,
    ) -> Optional[maas_types.Subscription]:
        cursor = _get_sub_pgsql_cursor(
            pgsql, f'maas_sub_id=\'{sub_id}\'', with_time_fields,
        )
        return _parse_sub_row(cursor.fetchone())

    return get_subscription_by_id_


@pytest.fixture(name='get_order_by_id')
def order_by_id_fixture(pgsql):
    def get_order_by_id_(order_id: str) -> Optional[maas_types.Order]:
        cursor = _get_order_pgsql_cursor(pgsql, f'order_id=\'{order_id}\'')
        return _parse_order_row(cursor.fetchone())

    return get_order_by_id_


@pytest.fixture(name='coupon_state_mock')
def _mock_coupon_state(mockserver):
    def _setup_mock(
            phone_id: str,
            trips_count: Optional[int] = 5,
            error_code: Optional[str] = None,
            coupon_id: str = 'coupon_id',
            yandex_uid: str = 'yandex_uid',
    ):
        @mockserver.json_handler('/coupons/internal/coupon/state')
        def _mock(request):
            body = request.json
            assert body['coupon_code'] == coupon_id
            assert body['phone_id'] == phone_id
            assert body['yandex_uid'] == yandex_uid

            if error_code is not None:
                return mockserver.make_response(
                    status=error_code, json={'message': 'error message'},
                )

            response_body = {
                'orders_left': trips_count,
                'total_orders': 10,
                'expire_at': '2021-08-02T01:00:00Z',
            }

            return mockserver.make_response(json=response_body)

    return _setup_mock


@pytest.fixture(name='setup_geo_settings', autouse=True)
async def _setup_geo_settings(taxi_config, load_json):
    taxi_config.set(
        MAAS_GEO_HELPER_SETTINGS={
            'geo_client_qos': {
                'update-metro-geo-points-cache': {
                    'timeout-ms': 50,
                    'attempts': 1,
                },
            },
            'route_validation_settings': {
                'enable_geo_checks': True,
                'ignore_geo_errors': False,
            },
            'geo_settings': load_json('geo_settings.json'),
        },
    )


@pytest.fixture(name='setup_stops_nearby_response', autouse=True)
async def _setup_stops_nearby_response(mockserver, load_json):
    @mockserver.json_handler('/persuggest/internal/persuggest/v2/stops_nearby')
    def _stops_nearby(request):
        # response_file = 'stops_nearby_empty_response.json'
        return mockserver.make_response(
            json={}, status=500,
        )  # load_json(response_file))

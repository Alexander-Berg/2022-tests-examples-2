# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=too-many-lines
import datetime
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pytest
import pytz

from eats_performer_subventions_plugins import *  # noqa: F403 F401

from tests_eats_performer_subventions import utils

Order = Dict[str, Any]


@pytest.fixture(name='taxi-tariffs', autouse=True)
def _mock_tariffs(mockserver):
    @mockserver.handler('/taxi-tariffs/v1/tariff_zones')
    def _bulk_retrieve(request):
        zone_response = {
            'zones': [
                {
                    'name': 'moscow',
                    'time_zone': 'Europe/Moscow',
                    'country': 'rus',
                    'translation': 'moscow',
                    'currency': 'RUB',
                },
                {
                    'name': 'perm',
                    'time_zone': 'Asia/Yekaterinburg',
                    'country': 'rus',
                    'translation': 'perm',
                    'currency': 'RUB',
                },
                {
                    'name': 'testsuite_zone',
                    'time_zone': 'EST',
                    'country': 'rus',
                    'translation': 'testsuite_zone',
                    'currency': 'RUB',
                },
                {
                    'name': 'testsuite_zone_1',
                    'time_zone': 'Europe/Moscow',
                    'country': 'rus',
                    'translation': 'testsuite_zone',
                    'currency': 'EUR',
                },
            ],
        }
        return mockserver.make_response(json.dumps(zone_response), 200)


@pytest.fixture(name='now_utc')
def _now_utc(mocked_time):
    return mocked_time.now().replace(tzinfo=pytz.utc)


@pytest.fixture(name='db_get_cursor')
def _db_get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_performer_subventions'].dict_cursor()

    return create_cursor


def _make_timepoint(
        timepoint: Optional[Union[str, datetime.datetime]],
) -> Optional[datetime.datetime]:
    if isinstance(timepoint, str):
        timepoint = utils.parse_datetime(timepoint)
    return timepoint


@pytest.fixture()
def db_select_orders(db_get_cursor):
    def select_orders() -> List[Order]:

        cursor = db_get_cursor()
        query = """SELECT * FROM eats_performer_subventions.orders_info
            ORDER BY eats_id ASC"""
        cursor.execute(query)

        return list(map(dict, cursor.fetchall()))

    return select_orders


@pytest.fixture()
def db_select_goals(db_get_cursor):
    def select_goals() -> List[Order]:

        cursor = db_get_cursor()
        query = """SELECT * FROM eats_performer_subventions.performer_subvention_order_goals
            ORDER BY performer_id ASC"""
        cursor.execute(query)

        return list(map(dict, cursor.fetchall()))

    return select_goals


@pytest.fixture()
def db_select_orders_notifications(db_get_cursor):
    def select_orders_notifications() -> List[Order]:

        cursor = db_get_cursor()
        query = """SELECT * FROM eats_performer_subventions.orders_notifications
            ORDER BY eats_id ASC"""
        cursor.execute(query)

        return list(map(dict, cursor.fetchall()))

    return select_orders_notifications


@pytest.fixture()
def db_select_orders_billing_id(db_get_cursor):
    def select_orders_billing_id() -> List[Order]:

        cursor = db_get_cursor()
        query = """SELECT eats_id, billing_client_id
            FROM eats_performer_subventions.orders_info"""
        cursor.execute(query)

        return list(map(dict, cursor.fetchall()))

    return select_orders_billing_id


@pytest.fixture(name='make_order')
def _make_order(db_get_cursor):
    def make_order(**kwargs):
        order = {
            'eats_id': 'order_nr',
            'order_status': 'created',
            'claim_id': None,
            'corp_client_type': None,
            'event_at': None,
            'clid': None,
            'park_driver_profile_id': None,
            'place_id': None,
            'park_id': None,
            'unique_driver_id': None,
            'driver_id': None,
            'eats_profile_id': None,
            'billing_at': None,
            'region_id': None,
            'city_id': None,
            'geo_hierarchy': None,
            'payment_type': None,
            'time_zone': None,
            'zone_name': None,
            'update_finished': False,
            'billing_client_id': None,
            'claim_attempt': None,
            'oebs_mvp_id': None,
            'taxi_alias_id': None,
        }
        for key in kwargs:
            assert key in order
        order.update(kwargs)
        cursor = db_get_cursor()
        query = (
            """INSERT INTO eats_performer_subventions.orders_info
                ({}) VALUES ({})""".format(
                ', '.join(order.keys()),
                ', '.join('%s' for _ in range(len(order))),
            )
        )
        cursor.execute(query, list(order.values()))

    return make_order

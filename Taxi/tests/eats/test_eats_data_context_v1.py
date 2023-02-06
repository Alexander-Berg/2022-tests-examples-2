# coding: utf-8

import datetime

import pytest
from nile.api.v1 import clusters

from projects.eats.data_context.v1 import OrdersCubeContext
from projects.eats.data_context.v1 import CryptaContext

pytestmark = [pytest.mark.filterwarnings('ignore::DeprecationWarning')]


def create_simple_orders_cube_context(dwh_layer):
    job = clusters.MockCluster().job()
    return OrdersCubeContext(
        job=job,
        begin_dttm=datetime.datetime(2019, 6, 1),
        end_dttm=datetime.datetime(2019, 6, 22),
        dwh_layer=dwh_layer,
    )


def create_simple_crypta_context(segments, profile, id):
    job = clusters.MockCluster().job()
    return CryptaContext(
        job=job,
        calc_user_id_crypta_segments=segments,
        calc_user_id_crypta_profile=profile,
        calc_user_id_crypta_id=id,
    )


def test_orders_cube_api_raw():
    create_simple_orders_cube_context('raw').get_orders_cube(
        order_fields=None,
        carts=True,
        cart_fields=None,
        orders_finance_info=True,
        order_finance_info_fields=None,
        places=True,
        place_fields=None,
        carts_items=True,
        catalog_device_id=True,
    )


def test_orders_cube_api_ods():
    create_simple_orders_cube_context('ods').get_orders_cube(
        order_fields=None,
        carts=False,
        cart_fields=None,
        orders_finance_info=True,
        order_finance_info_fields=None,
        places=True,
        place_fields=None,
        carts_items=False,
        catalog_device_id=True,
    )


def test_crypta_api_1():
    context = create_simple_crypta_context(
        segments=True, profile=True, id=True,
    )

    context.get_user_id_crypta_segments()
    context.get_user_id_crypta_profile()
    context.get_user_id_crypta_id()

    context.get_user_id_crypta_segments(calc_mode=True)
    context.get_user_id_crypta_profile(calc_mode=True)
    context.get_user_id_crypta_id(calc_mode=True)


def test_crypta_api_2():
    context = create_simple_crypta_context(
        segments=True, profile=True, id=False,
    )

    context.get_user_id_crypta_segments()
    context.get_user_id_crypta_profile()
    context.get_user_id_crypta_id()

    context.get_user_id_crypta_segments(calc_mode=True)
    context.get_user_id_crypta_profile(calc_mode=True)
    context.get_user_id_crypta_id(calc_mode=True)

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_picking_time_estimator_plugins import *  # noqa: F403 F401

from tests_eats_picking_time_estimator import utils


@pytest.fixture()
def load_order(load_json):
    def do_load_order(filename):
        return utils.fill_order(load_json(filename))

    return do_load_order


@pytest.fixture()
def load_orders(load_json):
    def do_load_orders(filename):
        data = load_json(filename)
        for order in data['orders']:
            utils.fill_order(order)
        return data

    return do_load_orders

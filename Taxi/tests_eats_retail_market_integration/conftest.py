import datetime as dt
from typing import Optional

import pytest
import pytz

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_retail_market_integration_plugins import *  # noqa: F403 F401

from tests_eats_retail_market_integration import common


@pytest.fixture(name='to_utc_datetime')
def _to_utc_datetime():
    def do_to_utc_datetime(stamp):
        if not isinstance(stamp, dt.datetime):
            stamp = dt.datetime.fromisoformat(stamp)
        if stamp.tzinfo is not None:
            stamp = stamp.astimezone(pytz.UTC)
        return stamp

    return do_to_utc_datetime


@pytest.fixture(name='verify_periodic_metrics')
def _verify_periodic_metrics(
        taxi_eats_retail_market_integration,
        taxi_eats_retail_market_integration_monitor,
        testpoint,
):
    async def _verify(periodic_name, is_distlock):
        periodic_runner = (
            taxi_eats_retail_market_integration.run_distlock_task
            if is_distlock
            else taxi_eats_retail_market_integration.run_periodic_task
        )
        periodic_short_name = (
            periodic_name
            if is_distlock
            else periodic_name[len('eats_retail_market_integration-') :]
        )

        should_fail = False

        @testpoint(
            f'eats-retail-market-integration_{periodic_short_name}::fail',
        )
        def _fail(param):
            return {'inject_failure': should_fail}

        @testpoint(
            f'eats-retail-market-integration_periodic-data::use-current-epoch',
        )
        def _use_current_epoch(param):
            return {'use_current_epoch': True}

        await taxi_eats_retail_market_integration.tests_control(
            reset_metrics=True,
        )

        await periodic_runner(periodic_name)
        # assert _fail.has_calls

        metrics = (
            await taxi_eats_retail_market_integration_monitor.get_metrics()
        )
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 1
        assert data['oks'] == 1
        assert data['fails'] == 0
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

        should_fail = True
        try:
            await periodic_runner(periodic_name)
        except taxi_eats_retail_market_integration.PeriodicTaskFailed:
            pass
        # assert _fail.has_calls

        metrics = (
            await taxi_eats_retail_market_integration_monitor.get_metrics()
        )
        data = metrics['periodic-data'][periodic_short_name]
        assert data['starts'] == 2
        assert data['oks'] == 1
        assert data['fails'] == 1
        assert data['execution-time']['min'] >= 0
        assert data['execution-time']['max'] >= 0
        assert data['execution-time']['avg'] >= 0

    return _verify


class NmnMockContext:
    _v1_products_info = None
    _v1_place_products_info = None
    _last_v1_products_info_request = None
    _last_v1_place_products_info_request = None

    _should_validate_mock_request = True

    _place: Optional[common.NmnPlace] = None

    def handle_v1_products_info(self, request):
        self._last_v1_products_info_request = request
        if self._should_validate_mock_request:
            j = request.json
            assert set(j['product_ids']) == set(
                self._place.product_public_id_to_data.keys(),
            )

        return {
            'products': [
                {
                    'adult': product.adult,
                    'barcodes': [],
                    'description': {'general': product.description},
                    'id': product.public_id,
                    'images': [
                        {'url': url, 'sort_order': sort_order}
                        for url, sort_order in product.images
                    ],
                    'is_catch_weight': product.is_catch_weight,
                    'quantum': product.quantum if product.quantum else None,
                    'is_choosable': product.is_choosable,
                    'is_sku': product.is_sku,
                    'measure': (
                        {
                            'value': product.measure[0],
                            'unit': product.measure[1],
                        }
                        if product.measure
                        else None
                    ),
                    'volume': (
                        {'value': product.volume[0], 'unit': product.volume[1]}
                        if product.volume
                        else None
                    ),
                    'name': product.name,
                    'origin_id': product.origin_id,
                    'place_brand_id': str(self._place.brand_id),
                    'shipping_type': product.shipping_type,
                }
                for product in self._place.product_public_id_to_data.values()
            ],
        }

    def handle_v1_place_products_info(self, request):
        self._last_v1_place_products_info_request = request
        if self._should_validate_mock_request:
            j = request.json
            assert request.query['place_id'] == str(self._place.place_id)
            assert set(j['product_ids']) == set(
                self._place.product_public_id_to_data.keys(),
            )

        return {
            'products': [
                {
                    'id': product.public_id,
                    'in_stock': product.in_stock,
                    'is_available': product.is_available,
                    'origin_id': product.origin_id,
                    'parent_category_ids': [],
                    'price': product.price,
                    'old_price': product.old_price,
                }
                for product in self._place.product_public_id_to_data.values()
            ],
        }

    def set_mock_handlers(self, v1_products_info, v1_place_products_info):
        self._v1_products_info = v1_products_info
        self._v1_place_products_info = v1_place_products_info

    def set_mock_req_validation_state(self, enable=True):
        self._should_validate_mock_request = enable

    def set_place(self, place: common.NmnPlace):
        self._place = place

    def mock_times_called(self):
        return {
            'v1_products_info': self._v1_products_info.times_called,
            'v1_place_products_info': (
                self._v1_place_products_info.times_called
            ),
        }

    def mock_last_requests(self):
        return {
            'v1_products_info': self._last_v1_products_info_request,
            'v1_place_products_info': (
                self._last_v1_place_products_info_request
            ),
        }


@pytest.fixture(name='mock_nomenclature')
def _mock_nomenclature(mockserver):
    context = NmnMockContext()

    @mockserver.json_handler('eats-nomenclature/v1/products/info')
    def _mock_products(request):
        return context.handle_v1_products_info(request)

    @mockserver.json_handler('eats-nomenclature/v1/place/products/info')
    def _mock_place_products(request):
        return context.handle_v1_place_products_info(request)

    context.set_mock_handlers(_mock_products, _mock_place_products)

    return context

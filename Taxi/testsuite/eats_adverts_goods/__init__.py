import enum
from typing import List
from typing import Optional

import pytest

from . import types


_DEFAULT_RETAIL_TABLE_SCHEMA = [
    {'name': 'public_id', 'type': 'string'},
    {'name': 'brand_id', 'type': 'int64'},
    {'name': 'place_id', 'type': 'int64'},
    {'name': 'core_item_id', 'type': 'int64'},
    {'name': 'suitable_categories', 'type': 'any'},
    {'name': 'non_suitable_categories', 'type': 'any'},
]

_DEFAULT_RESTAURANTS_TABLE_SCHEMA = [
    {'name': 'brand_id', 'type': 'int64'},
    {'name': 'place_id', 'type': 'int64'},
    {'name': 'core_item_id', 'type': 'int64'},
]


class _SchemaType(str, enum.Enum):
    Retail = 'retail'
    Restaurants = 'restaurants'


class _Table:
    def __init__(
            self,
            schema_type: _SchemaType,
            promotion: str,
            products: Optional[List[types.Product]] = None,
            dishes: Optional[List[types.Dish]] = None,
    ):
        self.schema_type = schema_type
        self.promotion = promotion
        self.products = products or []
        self.dishes = dishes or []

    def get_path(self) -> str:
        schema_type = str(self.schema_type)
        promotion = str(self.promotion)
        return f'//testsuite/lib-eats-adverts-goods/{schema_type}/{promotion}'

    def get_config_record(self) -> dict:
        return {
            'path': self.get_path(),
            'schema_type': self.schema_type,
            'promotion': self.promotion,
        }

    def get_attributes(self) -> dict:
        schema = _DEFAULT_RETAIL_TABLE_SCHEMA
        if self.schema_type == _SchemaType.Restaurants:
            schema = _DEFAULT_RESTAURANTS_TABLE_SCHEMA

        return {
            'replication_factor': 1,
            'dynamic': 'false',
            'optimize_for': 'lookup',
            'schema': schema,
        }

    def get_data(self) -> list:
        if self.schema_type == _SchemaType.Retail:
            return self.serialize_products()
        return self.serialize_dishes()

    def serialize_products(self) -> list:
        result = []
        for product in self.products:
            result.append(
                {
                    'public_id': product.product_id,
                    'place_id': product.place.place_id,
                    'brand_id': product.place.brand_id,
                    'core_item_id': product.core_id,
                    'suitable_categories': {
                        'categories': product.suitable_categories,
                    },
                    'non_suitable_categories': {
                        'categories': product.non_suitable_categories,
                    },
                },
            )

        return result

    def serialize_dishes(self) -> list:
        result = []
        for dish in self.dishes:
            result.append(
                {
                    'brand_id': dish.place.brand_id,
                    'place_id': dish.place.place_id,
                    'core_item_id': dish.core_id,
                },
            )

        return result


class Cache:
    def __init__(self, taxi_config, yt_client):
        self.taxi_config = taxi_config
        self.yt_client = yt_client
        self.tables = []

    def add_table_from_marker(self, marker):
        if not marker.kwargs:
            return

        product_tables = marker.kwargs.get('product_tables', [])
        for product_table in product_tables:
            self.add_products_table(product_table)

        dish_tables = marker.kwargs.get('dish_tables', [])
        for dish_table in dish_tables:
            self.add_dishes_table(dish_table)

        self.write_tables()
        self.update_config()

    def add_products_table(self, table: types.ProductsTable):
        self.tables.append(
            _Table(
                _SchemaType.Retail,
                promotion=table.promotion,
                products=table.products,
            ),
        )

    def add_dishes_table(self, table: types.DishesTable):
        self.tables.append(
            _Table(
                _SchemaType.Restaurants,
                promotion=table.promotion,
                dishes=table.dishes,
            ),
        )

    def write_tables(self):
        for table in self.tables:
            table_path: str = table.get_path()
            table_exists = self.yt_client.exists(table_path)
            if not table_exists:
                self.yt_client.create(
                    'table',
                    table_path,
                    recursive=True,
                    attributes=table.get_attributes(),
                )

            self.yt_client.write_table(
                table.get_path(), table.get_data(), format=None,
            )

    def update_config(self):
        tables = []
        for table in self.tables:
            tables.append(table.get_config_record())

        self.taxi_config.set_values(
            {
                'EATS_ADVERTS_GOODS_ADVERTS_CACHE_SETTINGS': {
                    'enabled': True,
                    'cluster': 'yt-local',
                    'batch_size': 1000,
                    'tables': tables,
                },
            },
        )


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_adverts_goods_cache: per-test configuration of '
        'lib-eats-adverts-goods cache',
    )


@pytest.fixture(name='eats_adverts_goods_cache', autouse=True)
def eats_adverts_goods_cache(request, taxi_config, yt_client):
    cache = Cache(taxi_config, yt_client)

    for marker in request.node.iter_markers('eats_adverts_goods_cache'):
        cache.add_table_from_marker(marker)

    return cache

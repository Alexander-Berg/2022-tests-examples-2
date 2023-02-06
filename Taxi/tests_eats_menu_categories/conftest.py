import json
import typing

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_menu_categories_plugins import *  # noqa: F403 F401

from tests_eats_menu_categories import models
from tests_eats_menu_categories import sql
from tests_eats_menu_categories import utils


YANDEX_LOGIN = '@testsuite'


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'menu_items: [menu_items] fixture for inserting items',
    )
    config.addinivalue_line(
        'markers', 'rules: [rules] fixture for inserting rules',
    )
    config.addinivalue_line(
        'markers', 'categories: [categories] fixture for inserting categories',
    )
    config.addinivalue_line(
        'markers', 'mappings: [mappings] fixture for inserting mappings',
    )


@pytest.fixture(name='database')
def db(pgsql):
    return pgsql['eats_menu_categories']


def setup_items_marker(request, database):
    marker = request.node.get_closest_marker('menu_items')
    if marker:
        for item in marker.args:
            if not isinstance(item, models.MenuItem):
                raise Exception(
                    f'invalid marker.menu_items argument type {type(item)}',
                )
            sql.insert_item(database, item)


def setup_rules_marker(request, database):
    marker = request.node.get_closest_marker('rules')
    if marker:
        for item in marker.args:
            if not isinstance(item, models.Rule):
                raise Exception(
                    f'invalid marker.rules argument type {type(item)}',
                )
            sql.insert_rule(database, item)


def setup_categories_marker(request, database):
    marker = request.node.get_closest_marker('categories')
    if marker:
        for item in marker.args:
            if not isinstance(item, models.Category):
                raise Exception(
                    f'invalid marker.categories argument type {type(item)}',
                )
            sql.insert_category(database, item)


def setup_mappings_marker(request, database):
    marker = request.node.get_closest_marker('mappings')
    if marker:
        for item in marker.args:
            if not isinstance(item, models.Mapping):
                raise Exception(
                    f'invalid marker.mappings argument type {type(item)}',
                )
            sql.insert_mapping(database, item)


@pytest.fixture(autouse=True)
def setup_markers(request, database):
    # Регистрируем маркеры в одной фикстуре для того, чтобы
    # гарантировать строгий порядок записи сущностей в postrgresql

    setup_items_marker(request, database)
    setup_categories_marker(request, database)
    setup_rules_marker(request, database)
    setup_mappings_marker(request, database)


@pytest.fixture(name='categories')
def categories(taxi_eats_menu_categories):
    class Context:
        async def __get(
                self, request: dict,
        ) -> typing.Optional[models.Category]:
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/categories/get',
                headers={'x-yandex-login': YANDEX_LOGIN},
                json=request,
            )
            assert response.status in [200, 404]
            if response.status == 200:
                return utils.category_from_response(response.json())
            return None

        async def get_by_id(
                self, category_id: str,
        ) -> typing.Optional[models.Category]:
            return await self.__get({'id': category_id})

        async def get_by_slug(
                self, category_slug: str,
        ) -> typing.Optional[models.Category]:
            return await self.__get({'slug': category_slug})

        async def list(
                self,
                status_filter: typing.List[models.CategoryStatus] = None,
                slug_filter: typing.Optional[str] = None,
                name_filter: typing.Optional[str] = None,
                cursor: typing.Optional[str] = None,
                limit: typing.Optional[int] = None,
        ) -> typing.List[models.Category]:
            request: typing.Dict[str, typing.Any] = {
                **(
                    {
                        'filter_by_statuses': [
                            status.value for status in status_filter
                        ],
                    }
                    if status_filter
                    else {}
                ),
                **({'filter_by_name': name_filter} if name_filter else {}),
                **({'filter_by_slug': slug_filter} if slug_filter else {}),
                **({'cursor': cursor} if cursor else {}),
                **({'limit': limit} if limit else {}),
            }
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/categories/list',
                headers={'x-yandex-login': YANDEX_LOGIN},
                json=request,
            )
            assert response.status == 200
            return utils.categories_from_response(response.json())

        async def insert(
                self, slug: str, name: str, status: models.CategoryStatus,
        ) -> models.Category:
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/categories/post',
                headers={'x-yandex-login': YANDEX_LOGIN},
                json={'slug': slug, 'name': name, 'status': status.value},
            )
            assert response.status == 200
            return utils.category_from_response(response.json())

        async def update(self, category: models.Category) -> None:
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/categories/update',
                headers={'x-yandex-login': YANDEX_LOGIN},
                json={
                    'id': category.category_id,
                    'slug': category.slug,
                    'name': category.name,
                    'status': category.status.value,
                },
            )
            assert response.status == 200

        async def delete(self, category_id: str) -> models.Category:
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/categories/delete',
                headers={'x-yandex-login': YANDEX_LOGIN},
                json={'id': category_id},
            )
            assert response.status == 200
            return utils.category_from_response(response.json())

    return Context()


@pytest.fixture(name='items_mappings')
def items_mappings(taxi_eats_menu_categories):
    class Context:
        async def get_place_items_categories(
                self, place_id: str, category_ids: typing.List[str],
        ) -> typing.List[models.ItemWithCategories]:
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/place-category-items',
                json={'place_id': place_id, 'categories': category_ids},
            )
            assert response.status_code == 200
            return utils.item_mappings_from_response(response.json())

        async def get_items_categories(
                self, menu_items: typing.List[str],
        ) -> typing.List[models.ItemWithCategories]:
            response = await taxi_eats_menu_categories.post(
                '/internal/eats-menu-categories/v1/items-categories',
                json={'items': menu_items},
            )
            assert response.status_code == 200
            return utils.item_mappings_from_response(response.json())

    return Context()


CONSUMER = 'menu-items'
TOPIC = '/eda/processing/testing/eats-menu-categories/menu-items'


@pytest.fixture(name='menu_items_consumer_one_shot')
def menu_items_consumer_one_shot(taxi_eats_menu_categories):
    async def one_shot():
        await taxi_eats_menu_categories.run_task(CONSUMER + '-lb_consumer')

    return one_shot


@pytest.fixture(name='menu_items_logbroker_topic')
def menu_items_logbroker_topic(taxi_eats_menu_categories, testpoint):
    class Context:
        def __init__(self):
            self.cookie = 'menu_items_cookie'

        async def send_message(self, message: models.MenuItemMessage):
            post_message = await taxi_eats_menu_categories.post(
                'tests/logbroker/messages',
                data=json.dumps(
                    {
                        'consumer': CONSUMER,
                        'topic': TOPIC,
                        'cookie': ctx.cookie,
                        'data': message.as_json(),
                    },
                ),
            )
            assert post_message.status_code == 200

        async def wait_read(self):
            await commit.wait_call()

    ctx = Context()

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert ctx.cookie == cookie

    return ctx

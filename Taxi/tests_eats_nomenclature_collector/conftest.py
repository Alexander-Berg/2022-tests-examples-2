# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import uuid

import pytest

from eats_nomenclature_collector_plugins import *  # noqa: F403 F401


def create_brand(brand_id, slug='', is_enabled=True):
    return brand_id, slug, is_enabled


def create_place_group(
        place_group_id,
        parser_days_of_week,
        parser_hours,
        price_parser_hours='',
        stop_list_enabled=True,
        is_vendor=False,
        is_enabled=True,
):
    return (
        place_group_id,
        parser_days_of_week,
        parser_hours,
        price_parser_hours,
        stop_list_enabled,
        is_vendor,
        is_enabled,
    )


def create_brand_place_group(brand_id, place_group_id, is_enabled=True):
    return brand_id, place_group_id, is_enabled


def create_place(
        place_id,
        brand_id,
        place_group_id,
        is_enabled=True,
        is_parser_enabled=True,
        stop_list_enabled=True,
):
    return (
        place_id,
        brand_id,
        place_group_id,
        is_enabled,
        is_parser_enabled,
        stop_list_enabled,
    )


def create_nomenclature_brand_task(task_id, brand_id, status, created_at):
    return task_id, brand_id, status, created_at


def create_nomenclature_place_task(
        place_id, nomenclature_brand_task_id, status, created_at, task_id=None,
):
    return (
        task_id or uuid.uuid4().hex,
        place_id,
        nomenclature_brand_task_id,
        status,
        created_at,
    )


def create_price_task(place_id, status, created_at, task_id=None):
    return task_id or uuid.uuid4().hex, place_id, status, created_at


def create_stock_task(place_id, status, created_at):
    return uuid.uuid4().hex, place_id, status, created_at


def create_availability_task(place_id, status, created_at):
    return uuid.uuid4().hex, place_id, status, created_at


def create_task_creation_attempt(
        place_id,
        last_creation_attempt_at,
        attempts_count,
        last_attempt_was_successful,
):
    return (
        place_id,
        last_creation_attempt_at,
        attempts_count,
        last_attempt_was_successful,
    )


def insert_brand(pg_cursor, brand):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.brands(
            id, slug, is_enabled
        )
        values (%s, %s, %s);
        """,
        brand,
    )


def insert_place_group(pg_cursor, place_group):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.place_groups(
            id,
            name,
            parser_days_of_week,
            parser_hours,
            price_parser_hours,
            stop_list_enabled,
            is_vendor,
            is_enabled
        )
        values (%s, '', %s, %s, %s, %s, %s, %s);
        """,
        place_group,
    )


def insert_brand_place_group(pg_cursor, brand_place_group):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.brands_place_groups(
            brand_id,
            place_group_id,
            is_enabled
        )
        values (%s, %s, %s);
        """,
        brand_place_group,
    )


def insert_place(pg_cursor, place):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.places(
            id,
            slug,
            brand_id,
            place_group_id,
            is_enabled,
            is_parser_enabled,
            stop_list_enabled
        )
        values (%s, '', %s, %s, %s, %s, %s);
        """,
        place,
    )


def insert_nomenclature_brand_task(pg_cursor, task):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.nomenclature_brand_tasks(
            id,
            brand_id,
            status,
            created_at
        )
        values (%s, %s, %s, %s);
        """,
        task,
    )


def insert_nomenclature_place_task(pg_cursor, task):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.nomenclature_place_tasks(
            id,
            place_id,
            nomenclature_brand_task_id,
            status,
            created_at
        )
        values (%s, %s, %s, %s, %s);
        """,
        task,
    )


def insert_price_task(pg_cursor, task):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.price_tasks(
            id,
            place_id,
            status,
            created_at
        )
        values (%s, %s, %s, %s);
        """,
        task,
    )


def insert_stock_task(pg_cursor, task):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.stock_tasks(
            id,
            place_id,
            status,
            created_at
        )
        values (%s, %s, %s, %s);
        """,
        task,
    )


def insert_availability_task(pg_cursor, task):
    pg_cursor.execute(
        """
        insert into eats_nomenclature_collector.availability_tasks(
            id,
            place_id,
            status,
            created_at
        )
        values (%s, %s, %s, %s);
        """,
        task,
    )


def insert_task_creation_attempt(pg_cursor, table_name, attempt):
    pg_cursor.execute(
        f"""
        insert into eats_nomenclature_collector.{table_name}(
            place_id,
            last_creation_attempt_at,
            attempts_count,
            last_attempt_was_successful
        )
        values (%s, %s, %s, %s);
        """,
        attempt,
    )


@pytest.fixture
def fill_db(pg_cursor):
    def _fill_db(
            brands,
            place_groups,
            brands_place_groups,
            places,
            *,
            place_task_creation_attempts=[],
            price_task_creation_attempts=[],
            nomenclature_brand_tasks=None,
            nomenclature_place_tasks=None,
            price_tasks=None,
            stock_tasks=None,
            availability_tasks=None,
    ):
        for brand in brands:
            insert_brand(pg_cursor, brand)
        for place_group in place_groups:
            insert_place_group(pg_cursor, place_group)
        for brand_place_group in brands_place_groups:
            insert_brand_place_group(pg_cursor, brand_place_group)
        for place in places:
            insert_place(pg_cursor, place)
        for attempt in place_task_creation_attempts:
            insert_task_creation_attempt(
                pg_cursor,
                'nomenclature_place_task_creation_attempts',
                attempt,
            )
        for attempt in price_task_creation_attempts:
            insert_task_creation_attempt(
                pg_cursor, 'price_task_creation_attempts', attempt,
            )
        for task in nomenclature_brand_tasks or ():
            insert_nomenclature_brand_task(pg_cursor, task)
        for task in nomenclature_place_tasks or ():
            insert_nomenclature_place_task(pg_cursor, task)
        for task in price_tasks or ():
            insert_price_task(pg_cursor, task)
        for task in stock_tasks or ():
            insert_stock_task(pg_cursor, task)
        for task in availability_tasks or ():
            insert_availability_task(pg_cursor, task)

    return _fill_db


@pytest.fixture
def mock_integrations(mockserver):
    def _mock_integrations(
            core_integrations_status,
            expected_task_types,
            failed_task=False,
            reason=None,
    ):
        @mockserver.json_handler(
            '/eats-core-integrations/integrations/nomenclature-collector/v1/'
            'tasks',
        )
        def eats_core_retail(request):
            assert request.json['type'] in expected_task_types
            if failed_task:
                return {
                    'id': request.json['id'],
                    'type': request.json['type'],
                    'place_id': request.json['place_id'],
                    'status': 'failed',
                    'data_file_url': '',
                    'data_file_version': '',
                    'reason': reason,
                }
            if core_integrations_status == 400:
                return mockserver.make_response(
                    json={
                        'errors': [
                            {'code': 'BAD_REQUEST', 'message': 'bad request'},
                        ],
                    },
                    status=400,
                )
            if core_integrations_status == 401:
                return mockserver.make_response(
                    json={
                        'errors': [
                            {
                                'code': 'UNAUTHOURIZED',
                                'message': 'unauthorized',
                            },
                        ],
                    },
                    status=401,
                )
            if core_integrations_status == 403:
                return mockserver.make_response(
                    json={
                        'errors': [
                            {'code': 'FORBIDDEN', 'message': 'forbidden'},
                        ],
                    },
                    status=403,
                )
            if core_integrations_status == 404:
                return mockserver.make_response(
                    json={
                        'errors': [
                            {
                                'code': 'PLACE_IS_NOT_FOUND',
                                'message': 'place is not found',
                            },
                        ],
                    },
                    status=404,
                )
            if core_integrations_status == 409:
                return mockserver.make_response(
                    json={
                        'id': '1',
                        'type': request.json['type'],
                        'place_id': request.json['place_id'],
                        'status': 'created',
                    },
                    status=409,
                )
            if core_integrations_status == 500:
                return mockserver.make_response(
                    json={
                        'errors': [
                            {
                                'code': 'INTERNAL_SERVER_ERROR',
                                'message': 'internal server error',
                            },
                        ],
                    },
                    status=500,
                )
            return {
                'id': request.json['id'],
                'type': request.json['type'],
                'place_id': request.json['place_id'],
                'status': 'created',
                'data_file_url': '',
                'data_file_version': '',
                'reason': None,
            }

        return eats_core_retail

    return _mock_integrations


@pytest.fixture(name='sql_get_place_tasks_last_status')
def _sql_get_place_tasks_last_status(to_utc_datetime):
    def do_smth(cursor, place_id, task_type):
        cursor.execute(
            f"""
            select
                status,
                task_error,
                task_warnings,
                status_or_text_changed_at
            from eats_nomenclature_collector.place_tasks_last_status
            where place_id = '{place_id}'
              and task_type = '{task_type}'
            """,
        )
        result = cursor.fetchone()
        result['status_or_text_changed_at'] = to_utc_datetime(
            result['status_or_text_changed_at'],
        )
        return result

    return do_smth


@pytest.fixture(name='sql_get_place_tasks_last_status_history')
def _sql_get_place_tasks_last_status_history(to_utc_datetime):
    def do_smth(cursor, place_id, task_type):
        cursor.execute(
            f"""
            select
                status,
                task_error,
                task_warnings,
                status_or_text_changed_at
            from eats_nomenclature_collector.place_tasks_last_status_history
            where place_id = '{place_id}'
              and task_type = '{task_type}'
            order by updated_at asc
            """,
        )
        result = cursor.fetchall()
        for row in result:
            row['status_or_text_changed_at'] = to_utc_datetime(
                row['status_or_text_changed_at'],
            )
        return result

    return do_smth

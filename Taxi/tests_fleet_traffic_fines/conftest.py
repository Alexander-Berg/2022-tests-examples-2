# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from fleet_traffic_fines_plugins import *  # noqa: F403 F401

import mock_api_impl


@pytest.fixture
def mock_api(mockserver, load_json):
    context = {
        'fines_response': load_json('fines_response.json'),
        'fleet_vehicles_response': load_json('fleet_vehicles_response.json'),
        'contractors': load_json('contractors.json'),
    }
    return mock_api_impl.setup(context, mockserver)


@pytest.fixture
def pg_dump(pgsql):
    def execute():
        with pgsql['fleet_traffic_fines'].cursor() as cursor:
            return pg_dump_all(cursor)

    return execute


def pg_dump_park_cars(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.park_cars
        """,
    )
    return {
        (row[0], row[1], row[2], row[3]): row[4:] for row in cursor.fetchall()
    }


def pg_dump_cars(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.cars_sync
        """,
    )
    return {(row[0], row[1]): row[2:] for row in cursor.fetchall()}


def pg_dump_fines(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.fines
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_park_fines(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.park_fines
        """,
    )
    return {(row[0], row[1], row[2]): row[3:] for row in cursor.fetchall()}


def pg_dump_task_completions(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.task_completions
        """,
    )
    return {(row[0], row[1]): row[2:] for row in cursor.fetchall()}


def pg_dump_park_bank_accounts(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.park_bank_accounts
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_load_operations(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.load_bank_client_operations
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_contractors(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_traffic_fines.fines_contractors
        """,
    )
    return {(row[1], row[2], row[3]): row[4:] for row in cursor.fetchall()}


def pg_dump_all(cursor):
    return {
        'park_cars': pg_dump_park_cars(cursor),
        'cars': pg_dump_cars(cursor),
        'fines': pg_dump_fines(cursor),
        'park_fines': pg_dump_park_fines(cursor),
        'task_completions': pg_dump_task_completions(cursor),
        'park_bank_accounts': pg_dump_park_bank_accounts(cursor),
        'load_operations': pg_dump_load_operations(cursor),
        'contractors': pg_dump_contractors(cursor),
    }

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from fleet_communications_plugins import *  # noqa: F403 F401

import mock_api_impl


@pytest.fixture
def mock_api(load_yaml, mockserver):
    return mock_api_impl.setup(load_yaml, mockserver)


@pytest.fixture
def pg_dump(pgsql):
    def execute():
        with pgsql['fleet_communications'].cursor() as cursor:
            return pg_dump_all(cursor)

    return execute


def pg_dump_templates(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_communications.mailing_templates
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_mailings(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_communications.mailings
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_mailing_contractors(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            fleet_communications.mailing_contractors
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_all(cursor):
    return {
        'mailing_templates': pg_dump_templates(cursor),
        'mailings': pg_dump_mailings(cursor),
        'mailing_contractors': pg_dump_mailing_contractors(cursor),
    }

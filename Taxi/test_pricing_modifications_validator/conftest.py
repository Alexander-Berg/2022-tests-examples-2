# pylint: disable=redefined-outer-name,no-name-in-module
import pytest

import pricing_modifications_validator.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = [
    'pricing_modifications_validator.generated.service.pytest_plugins',
]


@pytest.fixture
def select_named(pgsql):
    def select_named_impl(query):
        res = []
        with pgsql['pricing_modifications_validator'].cursor() as cursor:
            cursor.execute(query)
            for row in cursor.fetchall():
                obj = {}
                for col in range(len(cursor.description)):
                    obj[cursor.description[col][0]] = row[col]
                res.append(obj)
        return res

    return select_named_impl

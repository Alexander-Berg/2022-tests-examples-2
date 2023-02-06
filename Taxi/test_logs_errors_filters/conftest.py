# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import logs_errors_filters.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['logs_errors_filters.generated.service.pytest_plugins']

INSERT_CGROUP_QUERY = """
INSERT INTO logs_errors_filters.cgroups(name, status)
VALUES
    ('{}', 'ok')
ON CONFLICT (name) DO NOTHING;
"""

CREATE_SQL_QUERY = """
INSERT INTO logs_errors_filters.filters
(description, st_key, cgroup, creator)
values (%s,%s,%s, %s) RETURNING id;
"""

BASE_QUERY_INSERT = """
INSERT INTO
logs_errors_filters.base_queries
(filter_id, matchstring, field)  VALUES (%s,%s,%s);
"""


# Without this tests fail on initialization
@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(
        {
            'STARTRACK_API_PROFILES': {
                'scripts': {'url': '', 'oauth_token': ''},
            },
            'JUGGLER_OAUTH': '',
        },
    )

    return simple_secdist


@pytest.fixture
def create_filter(pgsql):
    async def _wrapper(
            query, description=None, key=None, cgroup=None, creator=None,
    ) -> str:

        if creator is None:
            creator = 'defaultcreator'

        cursor = pgsql['logs_errors_filters'].cursor()
        if cgroup:
            cursor.execute(INSERT_CGROUP_QUERY.format(cgroup))
        cursor.execute(CREATE_SQL_QUERY, (description, key, cgroup, creator))

        f_id = cursor.fetchone()[0]

        def prepare_pquery_with_args(rule):
            return (
                BASE_QUERY_INSERT,
                (
                    f_id,
                    rule['matchstring'],
                    rule['field'] if 'field' in rule else None,
                ),
            )

        pqueries = [prepare_pquery_with_args(rule) for rule in query['rules']]

        for pquery_args in pqueries:
            cursor.execute(*pquery_args)
        return f_id

    return _wrapper


@pytest.fixture
def auth(simple_secdist):  # TODO: simplify
    async def _wrapper():
        apit = simple_secdist['settings_override']['API_ADMIN_SERVICES_TOKENS']
        apit['logs_errors_filters'] = 'fake_token'

    return _wrapper

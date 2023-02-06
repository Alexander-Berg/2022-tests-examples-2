# pylint: disable=redefined-outer-name
from typing import Optional

import pytest

import passenger_profile.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from test_passenger_profile import common

pytest_plugins = ['passenger_profile.generated.service.pytest_plugins']


@pytest.fixture
def pg_cursor(pgsql):
    cursor = pgsql['passenger_profile'].cursor()
    return cursor


@pytest.fixture
def run_sql(pg_cursor):
    def _fetch(query, *args):
        pg_cursor.execute(query, args)
        column_names = [column.name for column in pg_cursor.description]
        result = []
        for row in pg_cursor:
            result.append(dict(zip(column_names, row)))

        return result

    return _fetch


# pylint: disable=invalid-name
@pytest.fixture()
def add_passenger_profile_experiment(client_experiments3):
    def _wrapper(
            yandex_uid: str,
            src_service_name: Optional[str] = None,
            phone_id: Optional[str] = None,
            remote_ip: Optional[str] = None,
            add_application_args: bool = False,
    ):
        args = [{'name': 'yandex_uid', 'type': 'string', 'value': yandex_uid}]
        transformations = None

        if src_service_name is not None:
            args.append(
                {
                    'name': 'src_service_name',
                    'type': 'string',
                    'value': src_service_name,
                },
            )

        if phone_id is not None:
            args.append(
                {'name': 'phone_id', 'type': 'string', 'value': phone_id},
            )

        if remote_ip:
            args.append(
                {'name': 'remote_ip', 'type': 'string', 'value': remote_ip},
            )
            transformations = [
                {
                    'type': 'country_by_ip',
                    'src_args': ['remote_ip'],
                    'dst_arg': 'country_code',
                    'preserve_src_args': True,
                },
            ]

        if add_application_args:
            args.extend(
                [
                    {
                        'name': 'application',
                        'type': 'application',
                        'value': 'android',
                    },
                    {
                        'name': 'version',
                        'type': 'application_version',
                        'value': '3.152.0',
                    },
                    {
                        'name': 'application.brand',
                        'type': 'string',
                        'value': 'yataxi',
                    },
                ],
            )

        client_experiments3.add_record(
            consumer=common.EXPERIMENTS3_CONSUMER,
            experiment_name=common.PASSENGER_PROFILE_EXPERIMENT,
            args=args,
            args_transformations=transformations,
            value={},
        )

    return _wrapper

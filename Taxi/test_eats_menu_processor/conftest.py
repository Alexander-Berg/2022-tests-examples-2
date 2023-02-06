# pylint: disable=redefined-outer-name
import json
import typing

import asynctest
from psycopg2 import extras
from psycopg2 import sql
import pytest

from taxi.clients.mds_s3 import S3Object  # pylint: disable=C5521
from taxi.stq import async_worker_ng

import eats_menu_processor.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_menu_processor.generated.service.pytest_plugins']


@pytest.fixture(name='task_info')
def _build_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=0, reschedule_counter=1, queue='',
    )


@pytest.fixture
def mds3_menu_object():
    return S3Object(Key='s3_key', Body=b'[]', ETag='ETag')


@pytest.fixture
def mds3_menu_head():
    return S3Object(Key='s3_key', Body=None, ETag='ETag')


@pytest.fixture
def emp_pgsql_conn(pgsql):
    conn = pgsql['eats_menu_processor'].conn
    conn.cursor_factory = extras.RealDictCursor
    return conn


@pytest.fixture
def pg_insert(emp_pgsql_conn):
    def wrapper(
            table_name: str,
            data: dict,
            returning: typing.Optional[typing.List[str]] = None,
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        conn = emp_pgsql_conn
        sql_comma = sql.SQL(',')
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            table_name,
            sql_comma.join(map(sql.Identifier, data.keys())).as_string(conn),
            sql_comma.join(map(sql.Placeholder, data.keys())).as_string(conn),
        )
        if returning:
            _format = sql_comma.join(map(sql.Identifier, returning)).as_string(
                conn,
            )
            if returning[0] == '*':
                _format = '*'
            query += ' RETURNING {}'.format(_format)
        with conn.cursor() as cursor:
            cursor.execute(query, data)
            if returning:
                return dict(cursor.fetchall()[0])
        return None

    return wrapper


@pytest.fixture
def processing_data():
    return {
        'uuid': 'uuid__1',
        'brand_id': 'brand_id__1',
        'place_group_id': 'place_group_id__1',
        'place_id': 'place_id__1',
        's3_link': '/s3/eats-menu-processor/menu.json',
    }


@pytest.fixture
def emp_results_factory(pg_insert, processing_data):
    def wrapper(**kwargs) -> typing.Dict[str, typing.Any]:
        processing_data.update(kwargs)
        return pg_insert('results', processing_data, returning=['*'])

    return wrapper


@pytest.fixture
def emp_filters_factory(pg_insert):
    def wrapper(**kwargs):
        data = {'place_group_id': 'place_group_id__1', 'schema': {}}
        data.update(kwargs)
        data['schema'] = json.dumps(data['schema'])
        return pg_insert('dev_filters', data, returning=['*'])

    return wrapper


@pytest.fixture
def emp_filters(emp_filters_factory):
    return emp_filters_factory()


@pytest.fixture
def emp_results(emp_results_factory):
    return emp_results_factory()


@pytest.fixture
def mds3_client_mock(
        stq3_context,
        web_context,
        cron_context,
        mds3_menu_object,
        mds3_menu_head,
):

    from client_mds_s3.components import MdsS3Client  # pylint: disable=C5521
    mocked_mds3_client = asynctest.MagicMock(MdsS3Client)
    mocked_mds3_client.get_object = asynctest.CoroutineMock(
        return_value=mds3_menu_object,
    )
    mocked_mds3_client.head_object = asynctest.CoroutineMock(
        return_value=mds3_menu_head,
    )

    stq3_context.client_mds_s3 = mocked_mds3_client
    web_context.client_mds_s3 = mocked_mds3_client
    cron_context.client_mds_s3 = mocked_mds3_client

    return mocked_mds3_client

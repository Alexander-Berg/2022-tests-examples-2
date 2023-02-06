# pylint: disable=redefined-outer-name
import typing

from psycopg2 import sql
import pytest


from taxi.stq import async_worker_ng

from eats_report_sender.components.senders import settings as sender_settings
import eats_report_sender.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['eats_report_sender.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def mds3_virtual_path_disabling():
    sender_settings.SenderSettings.USE_MDS3_VIRTUAL_PATH = False
    yield
    sender_settings.SenderSettings.USE_MDS3_VIRTUAL_PATH = True


@pytest.fixture
def mds_s3_prefix():
    return '/mds_s3/eats_report_sender'


@pytest.fixture(name='task_info')
def _build_task_info():
    return async_worker_ng.TaskInfo(
        id='1', exec_tries=1, reschedule_counter=1, queue='',
    )


@pytest.fixture
def pg_insert(pgsql):
    def wrapper(
            db_name: str,
            table_name: str,
            data: dict,
            returned: typing.Optional[typing.List[str]] = None,
    ) -> typing.Optional[tuple]:
        conn = pgsql[db_name].conn
        sql_comma = sql.SQL(',')
        query = 'INSERT INTO {} ({}) VALUES ({})'.format(
            table_name,
            sql_comma.join(map(sql.Identifier, data.keys())).as_string(conn),
            sql_comma.join(map(sql.Placeholder, data.keys())).as_string(conn),
        )
        if returned:
            query += 'RETURNING {}'.format(
                sql_comma.join(map(sql.Identifier, returned)).as_string(conn),
            )
        with conn.cursor() as cursor:
            cursor.execute(query, data)
            if returned:
                return cursor.fetchone()
        return None

    return wrapper


@pytest.fixture
def create_report_by_sql(pgsql, pg_insert):
    def wrapper(
            uuid='511b40f-c0b8-4deb-8982-2a80f85e0045', **kwargs,
    ) -> typing.Optional[str]:
        data = {
            'uuid': uuid,
            'brand_id': 'brand_id__1',
            'place_id': 'place_id__1',
            'period': 'daily',
            'report_type': 'test_report_type',
        }
        data.update(kwargs)
        res = pg_insert('eats_report_sender', 'reports', data, ['uuid'])
        if res:
            return res[0]
        return None

    return wrapper

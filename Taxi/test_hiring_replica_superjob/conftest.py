# pylint: disable=redefined-outer-name
import pytest

import hiring_replica_superjob.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from hiring_replica_superjob.generated.cron import run_cron  # noqa: I100
from hiring_replica_superjob.internal import dbops
from hiring_replica_superjob.internal import models

pytest_plugins = ['hiring_replica_superjob.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def simple_secdist(simple_secdist):
    simple_secdist.update(
        {
            'superjob_client_secret': 'test_secret',
            'superjob_login': 'login',
            'superjob_password': 'password',
            'infranaim_api_token': (
                'RVVNVENGTXM1T05pY2c5bnpxU2d3Z25CcU93dVc0ODF4OTh6ZXliQVU5'
            ),
        },
    )
    return simple_secdist


@pytest.fixture  # noqa: F405
def run_crontask():
    async def _run_cron(task_name: str = None):
        argv = [
            'hiring_replica_superjob.crontasks.{}'.format(task_name),
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron


@pytest.fixture  # noqa: F405
def get_all_resumes(cron_context):
    async def _make_query():
        query = """
        SELECT *
        FROM hiring_replica_superjob.resumes
        """
        async with cron_context.postgresql() as conn:
            rows = await conn.fetch(query)
        return rows

    return _make_query


@pytest.fixture  # noqa: F405
def resume_get(cron_context):
    async def _make_query(resume_id=None):
        row = await dbops.resume_get(cron_context, resume_id)
        return row

    return _make_query


@pytest.fixture  # noqa: F405
def get_purchased_resumes(cron_context):
    async def _make_query():
        query = """
        SELECT *
        FROM hiring_replica_superjob.resumes
        WHERE doc->>'contacts_bought' = 'true'
        """
        async with cron_context.postgresql() as conn:
            rows = await conn.fetch(query)
        return rows

    return _make_query


@pytest.fixture  # noqa: F405
def resumes_upsert(cron_context):
    """Записать или обновить пачку резюме в базе данных"""

    async def _wrapped(data=None):
        rows = await dbops.resumes_upsert(cron_context, data)
        return rows

    return _wrapped


@pytest.fixture  # noqa: F405
def get_last_resume(cron_context):
    """Получить последнюю запись из crawl history"""

    async def _wrapped():
        return await dbops.last_resume(cron_context)

    return _wrapped


@pytest.fixture  # noqa: F405
def save_crawl_history(cron_context):
    """Записать ревизию резюме в crawl history"""

    async def _wrapped(rev):
        return await dbops.save_crawl_history(cron_context, rev)

    return _wrapped


@pytest.fixture  # noqa: F405
def resumes_to_buy(cron_context):
    """Отфильтровать записи пригодные для покупки"""

    async def _wrapped():
        return await dbops.resumes_to_buy(cron_context)

    return _wrapped


@pytest.fixture  # noqa: F405
def resumes_by_rev(cron_context):
    """Отфильтровать записи пригодные для покупки"""

    async def _wrapped(rev=None):
        return await dbops.resumes_by_rev(cron_context, rev)

    return _wrapped


@pytest.fixture  # noqa: F405
def serialize_tiket():
    """Собать тикет из резюме"""

    def _wrapped(data=None):
        return models.ZendeskTicket.serialize(data)

    return _wrapped

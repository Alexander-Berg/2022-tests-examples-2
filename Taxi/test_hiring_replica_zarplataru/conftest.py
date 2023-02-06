# pylint: disable=redefined-outer-name
import datetime
import functools
import itertools

import aiohttp
import pytest

import hiring_replica_zarplataru.generated.service.pytest_init  # noqa:F401,E501,I100
import client_zarplataru.pytest_plugin  # noqa:I100
from taxi.util import dates  # noqa:I100,I201

# pylint: disable=ungrouped-imports
from hiring_replica_zarplataru.generated.cron import run_cron  # noqa:I100,I201


pytest_plugins = ['hiring_replica_zarplataru.generated.service.pytest_plugins']


@pytest.fixture
def _simple_secdist(simple_secdist):  # pylint: disable = W0621, E0102
    simple_secdist['zarplataru_history_cursor_salt'] = 'salt-secret'

    # Cannot just add field to `simple_secdist` due it somehow (don't
    # know how) overrides `simple_secdist` from
    # `plugins/clients/zarplataru/pytest_plugin`. That's why have to
    # redefine credentials for client.
    simple_secdist['zarplataru_credentials'] = {
        'login': client_zarplataru.pytest_plugin.LOGIN,  # noqa: F405
        'password': client_zarplataru.pytest_plugin.PASSWORD,  # noqa: F405
    }

    # The same for infrazendesk
    simple_secdist['infrazendesk_client'] = {'token': 'supersecret'}

    return simple_secdist


# To avoid "error: Cannot determine type of 'simple_secdist'"
globals()['simple_secdist'] = _simple_secdist


@pytest.fixture
def run_get_latest_resumes():
    module_name = 'hiring_replica_zarplataru.crontasks.get_latest_resumes'
    return functools.partial(_run_cron, module_name)


@pytest.fixture
def run_buy_contacts():
    module_name = 'hiring_replica_zarplataru.crontasks.buy_contacts'
    return functools.partial(_run_cron, module_name)


@pytest.fixture
def get_resume_updates(
        web_app_client, _simple_secdist,
):  # pylint: disable = W0621
    async def _wrapper(cursor=None):
        params = {}
        if cursor is not None:
            params['cursor'] = cursor
        response = await web_app_client.get(
            '/v1/resumes/updates', params=params,
        )
        response.raise_for_status()
        return await response.json()

    return _wrapper


@pytest.fixture
def get_resumes_and_history(web_app_client):
    async def _wrapper():
        response = await web_app_client.post(
            '/test-handlers/all-resumes-and-history',
        )
        response_body = await response.json()
        return response_body['resumes'], response_body['history']

    return _wrapper


@pytest.fixture
def update_resume_fields(web_app_client):
    async def _wrapper(resume_id, **kwargs):
        fields = []
        for key, value in kwargs.items():
            if isinstance(value, datetime.datetime):
                value = dates.timestring(value)
            fields.append({'field': key, 'value': value})
        response = await web_app_client.post(
            '/test-handlers/update-resume-in-db',
            json={'resume_id': resume_id, 'fields': fields},
        )
        assert response.status == 200

    return _wrapper


@pytest.fixture
def step_auth_and_get_latest(
        zarplataru_auth_handler,
        zarplataru_resumes_handler,
        run_get_latest_resumes,
        _latest_resumes_provider,
        get_resumes_and_history,
):
    async def _wrapper(*filenames, run_cron_times=1):
        static_provider = _latest_resumes_provider(*filenames)
        auth_handler_ = zarplataru_auth_handler()
        resumes_handler_ = zarplataru_resumes_handler(static_provider)

        for dummy_i in range(run_cron_times):
            await run_get_latest_resumes()

        resumes_, history_ = await get_resumes_and_history()

        class Step:
            auth_handler = auth_handler_
            resumes_handler = resumes_handler_
            latest_resumes_calls = static_provider.calls
            resumes = resumes_
            history = history_

        return Step()

    return _wrapper


@pytest.fixture
def step_buy_contacts(
        step_auth_and_get_latest,
        zarplataru_contacts_handler,
        run_buy_contacts,
        _buy_contacts_provider,
        get_resumes_and_history,
):
    async def _wrapper(latest_resumes_filename, run_cron_times=1):
        static_provider = _buy_contacts_provider()
        contacts_handler_ = zarplataru_contacts_handler(static_provider)

        prev_step = await step_auth_and_get_latest(latest_resumes_filename)
        for dummy_i in range(run_cron_times):
            await run_buy_contacts()

        resumes_, history_ = await get_resumes_and_history()

        class Step:
            auth_handler = prev_step.auth_handler
            resumes_handler = prev_step.resumes_handler
            contacts_handler = contacts_handler_
            latest_resumes_calls = prev_step.latest_resumes_calls
            buy_contacts_calls = static_provider.calls
            resumes = resumes_
            history = history_

        return Step()

    return _wrapper


@pytest.fixture
def step_fetch_resumes(step_buy_contacts, get_resume_updates):
    async def _wrapper(resumes_filename=None):
        prev_step = object()
        if resumes_filename is not None:
            prev_step = await step_buy_contacts(resumes_filename)

        chunk_ = await get_resume_updates()

        class Step(prev_step.__class__):
            chunk = chunk_

        return Step()

    return _wrapper


async def _run_cron(module_name):
    await run_cron.main([module_name, '-d', '-t', '0'])


@pytest.fixture
def _latest_resumes_provider(load_json):
    def _wrapper(*filenames):
        last_filename = filenames[-1]

        class LatestResumesProvider:
            _infinite_filenames = itertools.chain(
                filenames, itertools.repeat(last_filename),
            )
            calls = []

            def __call__(self):
                self.calls.append(load_json(next(self._infinite_filenames)))
                return self.calls[-1]

        return LatestResumesProvider()

    return _wrapper


@pytest.fixture
def _buy_contacts_provider(load_json):
    def _wrapper():
        class BuyContactsProvider:
            calls = []

            def __call__(self, resume_id):
                try:
                    response = load_json('full_resume_%s.json' % resume_id)
                except FileNotFoundError:
                    self.calls.append(None)
                    return aiohttp.web.json_response(status=404, data={})
                else:
                    self.calls.append(response)
                    return response

        return BuyContactsProvider()

    return _wrapper


@pytest.fixture  # noqa: F405
def run_crontask():
    async def _run_cron(task_name: str = None):
        argv = [
            'hiring_replica_zarplataru.crontasks.{}'.format(task_name),
            '-t',
            '0',
        ]
        await run_cron.main(argv)

    return _run_cron


@pytest.fixture  # noqa: F405
def get_all_responds(cron_context):
    async def _make_query():
        query = """
        SELECT *
        FROM hiring_replica_zarplataru.responds
        """
        async with cron_context.postgresql() as conn:
            rows = await conn.fetch(query)
        return rows

    return _make_query


@pytest.fixture
def send_updated_to_zendesk():
    module_name = 'hiring_replica_zarplataru.crontasks.send_updated_to_zendesk'
    return functools.partial(_run_cron, module_name)

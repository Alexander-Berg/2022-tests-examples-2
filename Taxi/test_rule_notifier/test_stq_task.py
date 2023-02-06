from unittest import mock

import aiohttp
import bson
import pytest

from taxi_billing_subventions.common import const
from taxi_billing_subventions.rule_notifier import context as ctx
from taxi_billing_subventions.rule_notifier import entities
from taxi_billing_subventions.rule_notifier import startrack
from taxi_billing_subventions.rule_notifier import task


@pytest.mark.now('2020-04-10T12:00:00')
@pytest.mark.filldb(subvention_rules='notify_end')
async def test_notify_end_of_rule(startrack_client, context):
    rule_id = bson.ObjectId('5e58b3a98fe28d5ce4da0950')
    await task.task(
        context,
        rule_id,
        kind=entities.TaskKind.NOTIFY_END.value,
        rule_kind=const.KIND_DRIVER_FIX_RULE,
    )
    assert startrack_client['calls'] == [
        {
            'url': 'http://startrack/issues/RUPRICING-5001/comments',
            'json': {
                'text': (
                    '((https://tariff-editor.taxi.yandex-team.ru/'
                    f'driver-modes/zone/zelenograd/show/{rule_id} '
                    'Режим работы)) завершает действие '
                    '2020-04-11T00:00:00+03:00.'
                ),
                'summonees': ['someone'],
            },
        },
    ]


@pytest.fixture(name='secdist')
def make_secdist():
    return {
        'settings_override': {
            'STARTRACK_API_PROFILES': {
                startrack.STARTTRACK_PROFILE: {
                    'oauth_token': 'secret',
                    'org_id': 0,
                    'url': 'http://startrack/',
                },
            },
        },
    }


@pytest.fixture(name='config')
def make_config():
    return mock.Mock(
        EXTERNAL_STARTRACK_DISABLE={},
        EXTERNAL_STARTRACK_REQUESTS_RATE={},
        EXTERNAL_STARTRACK_TIMEOUT={'__default__': 1},
        OPENTRACING_REPORT_SPAN_ENABLED={'__default__': False},
        TRACING_SAMPLING_PROBABILITY={},
        STQ_AGENT_CLIENT_TIMEOUT=5000,
    )


@pytest.fixture(name='session')
async def make_session():
    _session = aiohttp.client.ClientSession()
    yield _session
    await _session.close()


@pytest.fixture(name='context')
def make_context(db, config, secdist, session):
    return ctx.Context(secdist=secdist, session=session, config=config, db=db)


@pytest.fixture(name='startrack_client')
def make_startrack_client(patch_aiohttp_session, response_mock):
    calls = []

    @patch_aiohttp_session('http://startrack')
    def _wrapper(_method, url, json, **_kwargs):
        calls.append({'url': url, 'json': json})
        return response_mock(json={})

    return {'calls': calls}

# pylint: disable=protected-access, redefined-outer-name
import pytest

from replication import settings
from replication.monrun import general_check
from replication.monrun.checks import consistency
from replication.targets.yt import prefixes

_CRON_ACTUALIZE = 'replication-stuff-actualize_rules_metadata'

_CRON_OK_INFO = {_cron[0].replace('.', '-'): 1 for _cron in consistency._CRONS}


@pytest.fixture
def mock_crons(patch, response_mock):
    def setup(count_by_task: dict):
        @patch('taxi.clients.crons.CronsClient._request')
        async def _request(url, method, *args, **kwargs):
            assert url == '/utils/v1/get-finished-tasks-count/'
            assert method == 'POST'
            data = kwargs['json']
            assert data['task_name'] in count_by_task
            count = count_by_task[data['task_name']]
            return response_mock(json={'count': count})

    return setup


@pytest.mark.now('2020-01-03T00:00:00+03:00')
async def test_check_metadata_cron(mock_crons, replication_ctx):
    mock_crons({**_CRON_OK_INFO, _CRON_ACTUALIZE: 0})
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=consistency.CHECK_NAME,
    )
    assert res == (
        '1; Problem: no successful launches of /dev/cron/replication-'
        'stuff-actualize_rules_metadata in the last 300 seconds'
    )


@pytest.mark.config(
    REPLICATION_CRON_MAIN_SETUP={
        'consistency_alerts': {
            'replication.stuff.actualize_rules_metadata': 600,
        },
    },
)
@pytest.mark.now('2020-01-03T00:00:00+03:00')
async def test_override_cron(mock_crons, replication_ctx):
    mock_crons({**_CRON_OK_INFO, _CRON_ACTUALIZE: 0})
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=consistency.CHECK_NAME,
    )
    assert 'last 600 seconds' in res


@pytest.mark.now('2020-01-01T00:03:00+03:00')
@pytest.mark.config(
    REPLICATION_RULES_PARSE_ERRORS={'raise_on_parse_errors_at_load': False},
)
async def test_many_errors(
        _broken_secdist, monkeypatch, mock_crons, replication_ctx,
):
    mock_crons(_CRON_OK_INFO)
    all_yt_prefixes = None

    def _no_allowed_prefix(flaky_config):
        yt_prefixes_dict = flaky_config.get('yt_prefixes')
        assert (
            yt_prefixes_dict is not None
        ), 'Flaky config does not contain required "yt_prefixes" field'
        yt_prefixes = {}
        yt_prefixes['prefixes'] = {
            prefix: value
            for prefix, value in yt_prefixes_dict.items()
            if prefix != 'allowed'
        }
        nonlocal all_yt_prefixes
        all_yt_prefixes = sorted(yt_prefixes['prefixes'].keys())
        return prefixes.YTEntity(**yt_prefixes)

    monkeypatch.setattr(prefixes, 'load_yt_entity', _no_allowed_prefix)
    res = await general_check.run_general_check(
        replication_ctx, general_check_type=consistency.CHECK_NAME,
    )
    pattern = (
        'Unsupported YT prefix \'allowed\' got from target '
        f'(not found in {all_yt_prefixes})'
    )
    assert pattern in res


@pytest.fixture
def _broken_secdist(simple_secdist, monkeypatch):
    monkeypatch.setattr(settings, 'SAFELY_LOAD_RULES', True)
    secdist = simple_secdist
    conn = secdist.get('_testsuite_postgresql', {})
    conn['example_pg'] = [{'fail': '123'}]
    secdist.setdefault('_testsuite_postgresql', {}).update(conn)

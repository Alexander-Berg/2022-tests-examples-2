import logging

from aiohttp import web
import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils

logger = logging.getLogger(__name__)


class Tags:
    tag1 = 'tag1'
    tag2 = 'tag2'
    tag3 = 'tag3'


UNRELATED = 'unrelated'


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(sync_tags=utils.job_settings()),
    QC_SANCTION_TAG_MAP=dict(
        dkk=dict(
            enabled=True,
            reverse_tags_map=dict(reverse_sanction='reverse'),
            tags_map=dict(map_sanction='map'),
            tags=['simple', 'unrelated'],
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00')
@pytest.mark.parametrize(
    'state, tags',
    [
        (utils.make_state('p_d1', [], enabled=False), []),
        (utils.make_state('p_d1', []), ['reverse']),
        (utils.make_state('p_d1', [], has_present=False), ['reverse']),
        (utils.make_state('p_d1', ['reverse_sanction']), []),
        (utils.make_state('p_d1', ['map_sanction']), ['map', 'reverse']),
        (
            utils.make_state('p_d1', ['map_sanction', 'reverse_sanction']),
            ['map'],
        ),
        (utils.make_state('p_d1', ['simple']), ['simple', 'reverse']),
        (
            utils.make_state('p_d1', ['simple', 'map_sanction']),
            ['simple', 'map', 'reverse'],
        ),
        (
            utils.make_state(
                'p_d1', ['simple', 'map_sanction', 'reverse_sanction'],
            ),
            ['simple', 'map'],
        ),
    ],
)
async def test_qc_sync_tags_assign(
        patch, mock_quality_control_py3, mock_tags, state, tags,
):
    @mock_quality_control_py3('/api/v1/state/list')
    async def _api_v1_state_list(request):
        assert request.method == 'GET'
        return web.json_response(
            data=dict(modified='2010-01-01', cursor='next', items=[state]),
        )

    # mock retries
    @patch('taxi_qc_exams.helpers.retry.DelayStrategy.retry_async')
    async def _fake_retry(func, **kwargs):
        return await func()

    @mock_tags('/v1/assign')
    async def _v1_assign(request):
        return web.json_response(data={})

    # crontask
    await run_cron.main(
        ['taxi_qc_exams.crontasks.sync_tags.driver', '-t', '0'],
    )

    assert _v1_assign.times_called == 1
    request_json = _v1_assign.next_call()['request'].json

    assert request_json.pop('provider', None) == 'qc_dkk'
    assert request_json.pop('entities') == [
        dict(name='p_d1', type='dbid_uuid', tags={x: {} for x in tags}),
    ]
    assert not request_json

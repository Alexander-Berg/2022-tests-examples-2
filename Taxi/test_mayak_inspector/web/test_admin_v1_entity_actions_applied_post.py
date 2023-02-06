import datetime as dt

import pytest

from mayak_inspector.common import utils
from mayak_inspector.common.utils import yt_utils
from mayak_inspector.storage.ydb import extractors


URI = '/admin/v1/entity/actions/applied'


def rel_time(**kwargs) -> str:
    stamp = utils.now() - dt.timedelta(**kwargs)
    return stamp.isoformat()


@pytest.mark.now('2022-04-01T00:00:00')
@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        (
            {
                'entity_type': 'contractor',
                'entity_id': '1',
                'action_type': 'tagging',
                'rule_name': 'Cancel20',
                'datetime_from': rel_time(days=-7),
            },
            200,
            [
                {
                    'mayak_action_uuid': 1,
                    'action_type': 'tagging',
                    'rule_name': 'Cancel20',
                    'zone': '',
                    'tariff': '',
                    'action_params': {},
                    'triggered_context': {
                        'entity': {
                            'driver_profiles': {},
                            'park_driver_profile_ids': {},
                            'prefix_tags': [],
                        },
                        'tags': [],
                    },
                    'metrics_reasons': [],
                    'updated_at': '2022-04-01T03:00:00+03:00',
                },
            ],
        ),
    ],
)
async def test_modify(
        taxi_mayak_inspector_web,
        web_app_client,
        web_context,
        patch,
        tst_request,
        expected_status,
        expected_res,
):
    repo_module = 'mayak_inspector.storage.ydb.metrics.MetricsRepo'

    @patch(repo_module + '.get_actions_history_filtered')
    async def _get_actions_history_filtered(*args, **kwargs):
        return [
            extractors.ActionRecordAdmin(
                mayak_action_uuid=1,
                action_type=tst_request.get('action_type', str()),
                rule_name=tst_request.get('rule_name', str()),
                zone=tst_request.get('zone', str()),
                tariff=tst_request.get('tariff', str()),
                updated_at=utils.now(),
                triggered_context=yt_utils.yson_load(
                    yt_utils.yson_dump(
                        {
                            'tags': [],
                            'entity': {
                                'prefix_tags': [],
                                'park_driver_profile_ids': {},
                                'driver_profiles': {},
                            },
                        },
                    ),
                ),
                action_params=dict(),
                reasons=list(),
            ),
        ]

    res = await web_app_client.post(URI, json=tst_request)
    assert res.status == expected_status

    if expected_status > 200:
        return

    body = await res.json()
    items = body['items']

    data = utils.expected_fields(items, expected_res)

    assert data == expected_res

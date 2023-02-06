# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_restapp_marketing_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.
import json
import pytest


async def test_upload_statistics_without_campaigns(
        testpoint, taxi_eats_restapp_marketing,
):
    @testpoint('upload_advert_statistics_worker-finished')
    def handle_finished(arg):
        pass

    async with taxi_eats_restapp_marketing.spawn_task(
            'upload-advert-statisics',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'


@pytest.mark.xfail(reason='flaky test, will be fixed in EDADEV-39843')
async def test_upload_statistics(
        testpoint, taxi_eats_restapp_marketing, mockserver, pgsql,
):
    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_sessions(req):
        assert req.json['action'] == 'RUN'
        query = req.json['content']
        assert '1111' not in query
        assert '2222' in query
        assert '3333' in query
        return mockserver.make_response(
            status=200,
            json={
                'createdAt': '2021-02-02T00:00:00.060326Z',
                'execMode': 'RUN',
                'externalQueryIds': [],
                'id': '6019692ff301c38e94992596',
                'projectId': '5f97ce6768a6f5c079a61aa3',
                'queryData': {
                    'attributes': {'user_agent': ''},
                    'clusterType': 'UNKNOWN',
                    'content': '',
                    'files': [],
                    'parameters': {},
                    'type': 'SQLv1',
                },
                'queryType': 'SQLv1',
                'status': 'PENDING',
                'title': '',
                'updatedAt': '2021-02-02T00:00:00.132560Z',
                'username': 'vkoorits',
                'version': 0,
                'workerId': '6974305d-f18339ad-174b72f9-376d5dea',
            },
        )

    @testpoint('upload_advert_statistics_worker-finished')
    def handle_finished(arg):
        pass

    cursor = pgsql['eats_restapp_marketing'].cursor()
    cursor.execute(
        """
      INSERT INTO eats_restapp_marketing.advert
      (updated_at, averagecpc, place_id, campaign_id, group_id, ad_id, banner_id, is_active)
      VALUES (NOW(), 25000000, 1, 11, 111, 1111, 11111, false),
             (NOW(), 25000000, 2, 22, 222, 2222, 22222, true),
             (NOW(), 25000000, 3, 33, 333, 3333, 33333, true);
             """,
    )

    async with taxi_eats_restapp_marketing.spawn_task(
            'upload-advert-statisics',
    ):
        result = await handle_finished.wait_call()
        assert result['arg'] == 'test'

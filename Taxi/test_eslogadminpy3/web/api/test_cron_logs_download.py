# pylint: disable=unused-variable
import pytest

from test_eslogadminpy3 import constants


@pytest.mark.parametrize(
    'es_response, expected_response',
    [
        (constants.ES_RESPONSE_CRONS_EMPTY, ''),
        (
            constants.ES_RESPONSE_CRONS_SOME_LOGS,
            (
                '2019-06-26T13:00:10.347000+03:00\t'
                'info\tStarting '
                'replication-archive-queue_mongo-dm_storage_events, pid 6623\n'
                '2019-06-26T13:00:17.275000+03:00\tinfo\t'
                'Finished replication-archive-queue_mongo-dm_storage_events '
                'successfully, pid 6623'
            ),
        ),
    ],
)
async def test_get_cron_logs(
        patch, web_app_client, es_response, expected_response,
):
    @patch('elasticsearch_async.AsyncElasticsearch.search')
    async def search(*args, **kwargs):
        return es_response

    response = await web_app_client.get(
        '/v1/logs/crons/download/', params={'task_id': '123'},
    )
    assert response.status == 200
    assert (await response.text()) == expected_response

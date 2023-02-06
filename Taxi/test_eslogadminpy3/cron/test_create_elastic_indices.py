# pylint: disable=redefined-outer-name
import pytest

from eslogadminpy3.generated.cron import run_cron


@pytest.mark.now('2019-07-31T08:30:00.0Z')
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                LOGS_ELASTIC_INDEX_CREATION_TASK={
                    'create_enabled': True,
                    'create_index_timeout': 0,
                    'delay_after_index_creation': 0,
                    'concurrency': 0,
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                LOGS_ELASTIC_INDEX_CREATION_TASK={
                    'create_enabled': True,
                    'create_index_timeout': 0,
                    'delay_after_index_creation': 0,
                    'concurrency': 1,
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                LOGS_ELASTIC_INDEX_CREATION_TASK={
                    'create_enabled': True,
                    'create_index_timeout': 0,
                    'delay_after_index_creation': 0,
                    'concurrency': 2,
                },
            ),
        ),
    ],
)
async def test_task(patch):
    @patch('elasticsearch.client.indices.IndicesClient.get_mapping')
    async def _indices_get_mapping_mock(*args, **kwargs):
        return {
            'matching-index-2019.07.31.08': {
                'mappings': {'properties': {}, 'dynamic_templates': []},
            },
            'non-matching-index': {},
        }

    @patch('elasticsearch.client.indices.IndicesClient.create')
    async def _indices_create_mock(*args, **kwargs):
        assert kwargs['index'] == 'matching-index-2019.07.31.09'
        assert kwargs['body'] == {
            'mappings': {'properties': {}, 'dynamic_templates': []},
        }

    await run_cron.main(
        ['eslogadminpy3.crontasks.create_elastic_indices', '-t', '0', '-d'],
    )


async def test_stats(load_json, patch):
    @patch('elasticsearch.client.indices.IndicesClient.get_mapping')
    async def _indices_get_mapping_mock(*args, **kwargs):
        return load_json('mapping_es_7.json')

    @patch('elasticsearch.client.indices.IndicesClient.create')
    async def _indices_create_mock(*args, **kwargs):
        return {}

    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _solomon_push_data(data, log_extra):
        pass

    await run_cron.main(
        ['eslogadminpy3.crontasks.create_elastic_indices', '-t', '0', '-d'],
    )

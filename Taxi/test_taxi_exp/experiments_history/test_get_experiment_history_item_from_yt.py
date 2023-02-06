import json

import pytest

from taxi import discovery

from test_taxi_exp.helpers import experiment

ARCHIVE_API_URL = discovery.find_service('archive_api').url
REV = 1
EXPERIMENT_NAME = 'Experiment_name'
EXPECTED_RESPONSE = {
    'name': 'Experiment_name',
    'is_config': False,
    'is_removed': False,
    'is_closed': False,
    'is_enabled': True,
    'files': [],
    'tags': [],
    'exp_schema_version': 1,
    'body': {
        'name': 'Experiment_name',
        'closed': False,
        'removed': False,
        'description': 'Description for Experiment',
        'last_modified_at': 1,
        'biz_revision': 1,
        'financial': True,
        'default_value': None,
        'self_ok': False,
        'shutdown_mode': 'instant_shutdown',
        'enable_debug': False,
        'owners': [],
        'watchers': [],
        'trait_tags': [],
        'st_tickets': [],
        'clauses': [
            {'title': 'default', 'predicate': {'type': 'true'}, 'value': {}},
        ],
        'match': {
            'enabled': True,
            'schema': (
                '\ndescription: \'default schema\'\n'
                'additionalProperties: true\n    '
            ),
            'predicate': {'type': 'true'},
            'action_time': {
                'from': '2021-12-31T23:59:59+03:00',
                'to': '2021-12-31T23:59:59+03:00',
            },
            'consumers': [{'name': 'test_consumer'}],
            'applications': [
                {
                    'name': 'ios',
                    'version_range': {'from': '0.0.0', 'to': '99.99.99'},
                },
                {
                    'name': 'android',
                    'version_range': {'from': '0.0.0', 'to': '99.99.99'},
                },
            ],
        },
    },
}


@pytest.mark.config(TVM_RULES=[{'src': 'taxi_exp', 'dst': 'archive-api'}])
async def test_get_experiment_history_item_from_yt(
        taxi_exp_client, patch_aiohttp_session, response_mock,
):
    body = experiment.generate_default_history_item(
        name=EXPERIMENT_NAME,
        rev=REV,
        action_time={
            'from': '2021-12-31T23:59:59+0300',
            'to': '2021-12-31T23:59:59+0300',
        },
    )

    @patch_aiohttp_session(f'{ARCHIVE_API_URL}/v1/yt/lookup_rows', 'POST')
    def _mock_request(*args, **kwargs):
        data = kwargs['json']
        assert data['query'][0]['rev'] == REV
        return response_mock(
            json={
                'items': [
                    {
                        'name': EXPERIMENT_NAME,
                        'is_config': False,
                        'body': json.dumps(body),
                        'rev': REV,
                    },
                ],
            },
        )

    response = await taxi_exp_client.get(
        '/v1/history/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'revision': 1},
    )
    assert response.status == 200
    content = await response.json()
    assert content == EXPECTED_RESPONSE

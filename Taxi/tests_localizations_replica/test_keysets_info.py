import pytest


CONFIG = {
    'keysets': {
        'antifraud': {
            'mongo_collection_name': 'localization.taxi.antifraud',
            'tanker_keyset_id': 'antifraud',
            'tanker_project_id': 'taxi',
        },
        'backend_promotions': {
            'mongo_collection_name': 'localization.taxi.backend_promotions',
            'tanker_keyset_id': 'backend.promotions',
            'tanker_project_id': 'taxi',
        },
        'chatterbox': {
            'mongo_collection_name': 'localization.taxi.chatterbox',
            'tanker_keyset_id': 'chatterbox',
            'tanker_project_id': 'taxi',
        },
    },
}


@pytest.mark.servicetest
@pytest.mark.config(LOCALIZATIONS_KEYSETS=CONFIG)
@pytest.mark.parametrize(
    ('params', 'response_code', 'response_body'),
    [
        (
            {'verbose': 'false'},
            200,
            {
                'keysets': [
                    {'id': 'antifraud'},
                    {'id': 'backend_promotions'},
                    {'id': 'chatterbox'},
                ],
            },
        ),
        (
            {'verbose': 'true'},
            200,
            {
                'keysets': [
                    {
                        'id': 'chatterbox',
                        'project': 'taxi',
                        'tanker_name': 'chatterbox',
                    },
                    {
                        'id': 'antifraud',
                        'project': 'taxi',
                        'tanker_name': 'antifraud',
                    },
                    {
                        'id': 'backend_promotions',
                        'project': 'taxi',
                        'tanker_name': 'backend.promotions',
                    },
                ],
            },
        ),
    ],
)
async def test_keysets_response(
        taxi_localizations_replica, params, response_code, response_body,
):
    response = await taxi_localizations_replica.get(
        'v1/keysets/info', params=params,
    )
    assert response.status_code == response_code
    assert sorted(response.json()['keysets'], key=lambda x: x['id']) == sorted(
        response_body['keysets'], key=lambda x: x['id'],
    )

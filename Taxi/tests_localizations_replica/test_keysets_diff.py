import pytest


@pytest.mark.parametrize('response_code', [200])
async def test_keyset_response_empty(
        taxi_localizations_replica, response_code,
):
    response = await taxi_localizations_replica.get('v1/keysets/diff')
    assert response.status_code == response_code


@pytest.mark.filldb(localizations_meta='keysets')
@pytest.mark.parametrize(
    ('response_code', 'response_body'),
    [
        (
            200,
            {
                'keysets': [
                    {'id': 'chatterbox'},
                    {'id': 'geoareas'},
                    {'id': 'color'},
                    {'id': 'corp'},
                ],
            },
        ),
    ],
)
async def test_keyset_response_body_fill(
        taxi_localizations_replica, response_code, response_body,
):
    response = await taxi_localizations_replica.get('v1/keysets/diff')
    assert response.status_code == response_code

    assert sorted(response.json()['keysets'], key=lambda x: x['id']) == sorted(
        response_body['keysets'], key=lambda x: x['id'],
    )

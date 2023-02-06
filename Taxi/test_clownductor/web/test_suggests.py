import pytest


@pytest.mark.parametrize(
    'request_type, response_status, response_data',
    [
        pytest.param(
            'disk_profiles',
            200,
            {'items': []},
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={'disk_profiles': False},
            ),
        ),
        (
            'non_existing',
            400,
            {
                'code': 'UNKNOWN_SUGGEST_TYPE',
                'message': 'Unknown suggest type non_existing',
            },
        ),
    ],
)
async def test_suggests(
        web_app_client, request_type, response_status, response_data,
):
    response = await web_app_client.get(
        '/v1/suggest/', params={'type': request_type},
    )
    assert response.status == response_status
    assert (await response.json()) == response_data


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'disk_profiles': True})
async def test_suggests_disk_profile(web_app_client):
    response = await web_app_client.get(
        '/v1/suggest/', params={'type': 'disk_profiles'},
    )
    assert response.status == 200
    content = await response.json()
    assert content['items']

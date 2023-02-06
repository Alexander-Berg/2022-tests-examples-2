import json

import pytest


BASE_PATH = '/dkvu'
PATH = BASE_PATH + '/v1'
PING_PATH = BASE_PATH + '/ping'


# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'dkvu'}),
]


@pytest.mark.skip
async def test_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


@pytest.mark.skip
async def test_rand_img(web_app_client):
    response = await web_app_client.post(
        PATH,
        data=json.dumps(
            {
                'qc_id': 'qc_id_1',
                'driver_info': {
                    'country': 'russia',
                    'city': 'moscow',
                    'license_id': 'license_id_1',
                },
                'media': {'front': 'test', 'back': 'test'},
            },
        ),
    )

    assert response.status == 200
    data = json.loads(await response.text())
    assert data['resolution'] is not None

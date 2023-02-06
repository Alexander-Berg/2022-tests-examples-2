import pytest

from taxi_plotva_ml.api import smm_eats_v1

BASE_PATH = '/smm_eats'
PING_PATH = BASE_PATH + '/ping'
V1_PATH = BASE_PATH + '/v1'

# pylint: disable=C0103
pytestmark = [
    pytest.mark.enable_ml_handler(url_path=V1_PATH),
    pytest.mark.download_ml_resource(attrs={'type': 'smm_eats'}),
]


async def test_smm_eats_ping(web_app_client):
    response = await web_app_client.get(PING_PATH)
    assert response.status == 200


async def test_smm_eats_v1(web_app_client):
    response = await web_app_client.post(V1_PATH, json={})
    assert response.status == 400


@pytest.mark.skip(reason='Undo skip after resources will be used')
@pytest.mark.client_experiments3(
    consumer=smm_eats_v1.EXP3_SMM_EATS_SUPPORT,
    experiment_name='smm_eats',
    args=[{'name': 'post_id', 'type': 'string', 'value': '12345'}],
    value={'user_in_control': False},
)
async def test_smm_eats_v1_positive(web_app_client):
    response = await web_app_client.post(
        V1_PATH,
        json={
            'chat_id': '12334567890',
            'dialog': {
                'messages': [
                    {'author': 'user', 'text': 'У вас лучшая поддержка!!!'},
                ],
            },
            'features': [],
        },
    )
    assert response.status == 200

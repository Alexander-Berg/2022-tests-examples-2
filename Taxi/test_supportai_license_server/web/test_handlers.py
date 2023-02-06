import base64
import datetime

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
import pytest

from supportai_license_server.utils import postgres


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.pgsql('supportai_license_server', files=['default.sql'])
async def test_get_info(web_app_client, web_context):
    response = await web_app_client.get(
        '/info?unique_id=12345&project_slug=test_project',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['timestamp'] == str(
        datetime.datetime.utcnow().timestamp(),
    )

    assert 'iv' in response_json
    async with web_context.pg.slave_pool.acquire() as conn:
        query, args = web_context.sqlt.get_iv_by_unique_id(unique_id='12345')
        rows = await postgres.fetch(conn, query, args)
    assert len(rows) == 1
    assert rows[0]['iv'] == response_json['iv']

    assert 'signature' in response_json
    timestamp_hash = SHA256.new(response_json['timestamp'].encode('utf-8'))
    public_key_str = (
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDh0WVoF7xvFImwKnAIFAH1RtBij72GC'
        'fRe7DMt9x4Z/QUsZNfxzkFblRnndioiJbrck9i9ICMJ22LbnEUjXfKbG9E4hnwYcJKDnL'
        'dglmQCQ2Bc6dDI8GjGNHWy1eclyITgC2sXS5n4WzHX1rNV7NHieFA2ihayr7SPJCVEixd'
        '3i8BrRnHmRibqqFmH3ubB+XedKcFo3feC9BAS9DledJJky/1vVcS/aYo54H0s0AFi5bFy'
        'avMA5GE64QqMlS0Od97ghzgnReY/LxuHK1XT23V55yQRQiCXBj9LFTSDxRmP5I7mjhvPB'
        'k8pVSQw0O1mVQIp8gEKDyosBnglI9og1EQlqWQfNSxR9NZtwS74072x0Gb2uvWecgDkfq'
        'X35DoPfGETRGefl3MonK2ONGg7weDyHEmpmp6DqDc8Kl+Jb0B+jyXCCaB2Fr8Vvvyvxiq'
        '6f4gNIRTqPcb0XiuKI4nMWzM8OJdHR32OXL1Ug8YtRmVLaIPxfyCyHfo/whwoGWSDK6s='
    )
    public_key = RSA.import_key(public_key_str)
    try:
        pkcs1_15.new(public_key).verify(
            timestamp_hash, base64.b64decode(response_json['signature']),
        )
    except ValueError:
        assert False, 'Invalid signature'

    assert 'key_hash' in response_json
    assert response_json['key_hash'] == base64.b64encode(
        SHA256.new(public_key.export_key()).digest(),
    ).decode('utf-8')


@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.pgsql('supportai_license_server', files=['default.sql'])
@pytest.mark.parametrize(
    ('data', 'status'),
    [
        ('zeUEswheVuwSyXAHZdpIYLbZ47W0criZu7Db0Ky2n4g=', 200),
        ('deUEswheVuwSyXAHZdpIYLbZ47W0criZu7Db0Ky2n4D=', 400),
        ('1234534=', 400),
        ('DrJj1Lbmj/y+uGzwN1u32g==', 400),
    ],
)
async def test_post_statistic(web_app_client, web_context, data, status):
    response = await web_app_client.post(
        '/statistics?unique_id=54321&project_slug=test_project',
        json={'data': data},
    )
    assert response.status == status

    if status == 200:
        async with web_context.pg.slave_pool.acquire() as conn:
            query = (
                'SELECT support_count FROM supportai.statistics '
                'WHERE project_slug = $1'
            )
            rows = await postgres.fetch(conn, query, ['test_project'])

        assert len(rows) == 1
        assert rows[0]['support_count'] == 12

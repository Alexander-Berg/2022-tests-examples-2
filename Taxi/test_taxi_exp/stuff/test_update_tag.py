"""
План теста:
1. Замокать стафф
2. Замокать территории
3. Замокать user_api
3. Замокать trusted
4. Запустить таску
5. Убедиться, что в trusted пришли корректные данные
"""
import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import files

FIRST = 0


@pytest.fixture
def local_setup_mocks(
        taxi_exp_client, patch_aiohttp_session, response_mock, mockserver,
):
    @patch_aiohttp_session('{}/v3/persons'.format(settings.STAFF_API_URL))
    def _phones_from_staff(method, url, json, headers, params):
        return response_mock(
            json={
                'result': [{'phones': [{'number': '+79219201122'}], 'id': 0}],
                'pages': 1,
                'page': 1,
            },
        )

    @mockserver.json_handler('/user-api/user_phones/bulk')
    def _phone_id_from_user_api(request):
        return {
            'items': [
                {
                    'id': '566afbe7ed2c89a5e03b049b',
                    'phone': '+79219201122',
                    'type': 'yandex',
                    'personal_phone_id': '507f191e810c19729de860ea',
                    'stat': '',
                    'is_loyal': False,
                    'is_yandex_staff': True,
                    'is_taxi_staff': True,
                },
            ],
        }

    trusted_files_updation = []

    @mockserver.json_handler('/taxi-exp/v1/files/')
    def _trusted_files(request):
        trusted_files_data = request.get_data()
        trusted_files_data_length = int(request.headers['Content-Length'])
        trusted_files_updation.append(
            (trusted_files_data, trusted_files_data_length),
        )
        return {}

    @mockserver.json_handler('/taxi-exp/v1/trusted-files/metadata/')
    async def _trusted_file_metadata(request):
        return {}

    yield trusted_files_updation


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'taxi_exp', 'dst': 'staff'},
        {'src': 'taxi_exp', 'dst': 'taxi_exp'},
    ],
    TAXI_EXP_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'request_timeout_ms': 500,
                'num_retries': 0,
                'retry_delay_ms': [50],
            },
        },
    },
    USER_API_USE_USER_PHONES_CREATION_PY3=True,
)
async def test_update_tag(
        taxi_exp_client,
        local_setup_mocks,  # pylint: disable=redefined-outer-name
):
    trusted_files = local_setup_mocks

    # running cron
    await cron_run.main(['taxi_exp.stuff.update_tags.taxi', '-t', '0'])

    # check trusted file is correct
    assert len(trusted_files) == 1

    data, data_length = trusted_files[FIRST]
    assert data_length == len('566afbe7ed2c89a5e03b049b\n')
    assert data == b'566afbe7ed2c89a5e03b049b\n'
    trusted_files = []

    # non-mocked update trusted file
    response = await files.post_trusted_file(
        taxi_exp_client, 'taxi_phone_id', data,
    )
    assert response.status == 200

    # check metadata
    response = await files.get_trusted_file_metadata(
        taxi_exp_client, 'taxi_phone_id',
    )
    assert response.status == 200
    body = await response.json()
    mds_id = body['mds_id']
    assert (
        body['sha256']
        == '8d5c337bb6b4acd3e932f47d37909e1db7d360eb4bcd170172c16c8eeab79130'
    )

    # again running cron
    await cron_run.main(['taxi_exp.stuff.update_tags.taxi', '-t', '0'])
    assert not trusted_files

    # check metadata
    response = await files.get_trusted_file_metadata(
        taxi_exp_client, 'taxi_phone_id',
    )
    assert response.status == 200
    body = await response.json()
    assert body['mds_id'] == mds_id
    assert (
        body['sha256']
        == '8d5c337bb6b4acd3e932f47d37909e1db7d360eb4bcd170172c16c8eeab79130'
    )


@pytest.mark.config(
    TVM_RULES=[
        {'src': 'taxi_exp', 'dst': 'staff'},
        {'src': 'taxi_exp', 'dst': 'taxi_exp'},
    ],
    TAXI_EXP_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'request_timeout_ms': 500,
                'num_retries': 0,
                'retry_delay_ms': [50],
            },
        },
    },
    EXP3_ADMIN_CONFIG={
        'settings': {
            'backend': {
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
                },
            },
        },
    },
    USER_API_USE_USER_PHONES_CREATION_PY3=True,
)
async def test_update_tag_yandex(
        taxi_exp_client, patch_aiohttp_session, response_mock, mockserver,
):
    @patch_aiohttp_session('{}/v3/persons'.format(settings.STAFF_API_URL))
    def _phones_from_staff(method, url, json, headers, params):
        assert params.get('official.affiliation') == 'yandex'
        return response_mock(
            json={
                'result': [{'phones': [{'number': '777'}], 'id': 0}],
                'pages': 1,
                'page': 1,
            },
        )

    @mockserver.json_handler('/taxi-exp/v1/trusted-files/metadata/')
    async def _trusted_file_metadata(request):
        return {}

    @mockserver.json_handler('/taxi-exp/v1/files/')
    def _trusted_files(request):
        return {}

    await cron_run.main(['taxi_exp.stuff.update_tags.yandex', '-t', '0'])

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
from taxi_exp.stuff.update_tags import eats_team
from test_taxi_exp.helpers import files

FIRST = 0

PHONE = '+79219201122'
PHONE_ID = '22110291297+'


@pytest.mark.config(
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
)
@pytest.fixture
def local_setup_mocks(
        taxi_exp_client, patch_aiohttp_session, response_mock, mockserver,
):
    class Controller:
        trusted_files_updation = []
        is_not_found_metadata = False

    @patch_aiohttp_session('{}/v3/persons'.format(settings.STAFF_API_URL))
    def _phones_from_staff(method, url, json, headers, params):
        return response_mock(
            json={
                'result': [{'phones': [{'number': PHONE}], 'id': 0}],
                'pages': 1,
                'page': 1,
            },
        )

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    async def _phone_ids_from_personal(request):
        return {'items': [{'id': PHONE_ID, 'value': PHONE}]}

    @mockserver.json_handler('/taxi-exp/v1/files/')
    def _trusted_files(request):
        trusted_files_data = request.get_data()
        trusted_files_data_length = int(request.headers['Content-Length'])
        Controller.trusted_files_updation.append(
            (trusted_files_data, trusted_files_data_length),
        )
        return {}

    @mockserver.json_handler('/taxi-exp/v1/trusted-files/metadata/')
    async def _trusted_file_metadata(request):
        if Controller.is_not_found_metadata:
            return mockserver.make_response(status=404)
        return {}

    yield Controller


@pytest.mark.parametrize('is_not_found_metadata', [True, False])
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'taxi_exp', 'dst': 'staff'},
        {'src': 'taxi_exp', 'dst': 'taxi_exp'},
        {'src': 'taxi_exp', 'dst': 'territories'},
        {'src': 'taxi_exp', 'dst': 'personal'},
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
        is_not_found_metadata,
):
    trusted_files = local_setup_mocks.trusted_files_updation
    local_setup_mocks.is_not_found_metadata = is_not_found_metadata

    # running cron
    await cron_run.main(['taxi_exp.stuff.update_tags.eats_team', '-t', '0'])
    if is_not_found_metadata:
        return

    # check trusted file is correct
    assert len(trusted_files) == 1

    data, data_length = trusted_files[FIRST]
    assert data_length == len(b'22110291297+\n')
    assert data == b'22110291297+\n'
    trusted_files = []

    # non-mocked update trusted file
    response = await files.post_trusted_file(
        taxi_exp_client, eats_team.TAG, data,
    )
    assert response.status == 200

    # check metadata
    response = await files.get_trusted_file_metadata(
        taxi_exp_client, eats_team.TAG,
    )
    assert response.status == 200
    body = await response.json()
    mds_id = body['mds_id']
    assert (
        body['sha256']
        == 'b6f20b48459cbf57964f3faad60e4f4a9d84ceff9be925ad7e478e0314c0a0a2'
    )

    # again running cron
    await cron_run.main(['taxi_exp.stuff.update_tags.eats_team', '-t', '0'])
    assert not trusted_files

    # check metadata
    response = await files.get_trusted_file_metadata(
        taxi_exp_client, eats_team.TAG,
    )
    assert response.status == 200
    body = await response.json()
    assert body['mds_id'] == mds_id
    assert (
        body['sha256']
        == 'b6f20b48459cbf57964f3faad60e4f4a9d84ceff9be925ad7e478e0314c0a0a2'
    )

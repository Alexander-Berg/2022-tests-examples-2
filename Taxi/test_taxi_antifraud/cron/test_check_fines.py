import pytest

from taxi_antifraud.crontasks import check_fines
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import state

YT_INPUT_TABLE_PATH_STS = '//home/taxi-fraud/unittests/fines_checks/input_sts'
YT_INPUT_TABLE_PATH_LICENSES = (
    '//home/taxi-fraud/unittests/fines_checks/input_licenses'
)
YT_OUTPUT_TABLE_PATH_STS = (
    '//home/taxi-fraud/unittests/fines_checks/output_sts'
)
YT_OUTPUT_TABLE_PATH_LICENSES = (
    '//home/taxi-fraud/unittests/fines_checks/output_licenses'
)

CURSOR_STATE_NAME_STS = check_fines.CURSOR_STATE_NAME_STS
CURSOR_STATE_NAME_LICENSES = check_fines.CURSOR_STATE_NAME_LICENSES


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override'][
        'ANTIFRAUD_ANIMALS_PASSWORD'
    ] = 'very_secret_pass'
    return simple_secdist


def _mock_yoomoney(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(check_fines.YOOMONEY_HTML_URL, 'GET')
    def _yoomoney_html(method, url, **kwargs):
        return response_mock(
            text=(
                '..\nlots of html and js here\nand there\n'
                'window.__language__=undefined;'
                'window.__secretKey__="VERYVERYSECRET";'
                '</script><div><script nonce=...'
            ),
        )

    @patch_aiohttp_session(check_fines.YOOMONEY_URL, 'POST')
    def _yoomoney_api(method, url, json, headers, **kwargs):
        if 'car' in json and json['car']:
            response = {
                'status': 'progress',
                'result': {
                    'requestId': 'some_sts_request_id',
                    'retryAfter': 5,
                    'charges': [],
                },
            }
        elif 'driver' in json and json['driver']:
            response = {
                'status': 'progress',
                'result': {
                    'requestId': 'some_license_request_id',
                    'retryAfter': 5,
                    'charges': [],
                },
            }
        elif (
            'requestId' in json and json['requestId'] == 'some_sts_request_id'
        ):
            response = {
                'status': 'success',
                'result': {
                    'retryAfter': 5000,
                    'charges': [
                        {
                            'reason': 'very bad car',
                            'paymentLink': 'VERY VERY LONG',
                        },
                    ],
                },
            }
        elif (
            'requestId' in json
            and json['requestId'] == 'some_license_request_id'
        ):
            response = {
                'status': 'success',
                'result': {
                    'retryAfter': 5000,
                    'charges': [
                        {
                            'reason': 'very bad driver',
                            'paymentLink': 'VERY VERY LONG',
                        },
                    ],
                },
            }
        else:
            return response_mock(status=500)
        return response_mock(json=response)

    return _yoomoney_api


def _prepare_data(data_sts, data_licenses, yt_client):
    yt_client.create(
        'table',
        path=YT_INPUT_TABLE_PATH_STS,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_INPUT_TABLE_PATH_STS, data_sts)
    yt_client.create(
        'table',
        path=YT_INPUT_TABLE_PATH_LICENSES,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_INPUT_TABLE_PATH_LICENSES, data_licenses)
    yt_client.remove(YT_OUTPUT_TABLE_PATH_STS, force=True)
    yt_client.remove(YT_OUTPUT_TABLE_PATH_LICENSES, force=True)


@pytest.mark.config(
    AFS_CRON_CHECK_FINES_ENABLED=True,
    AFS_CRON_CHECK_FINES_LICENSES_INPUT_TABLE_SUFFIX='fines_checks/input_licenses',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_CHECK_FINES_LICENSES_OUTPUT_TABLE_SUFFIX='fines_checks/output_licenses',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_CHECK_FINES_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CHECK_FINES_STS_INPUT_TABLE_SUFFIX='fines_checks/input_sts',
    AFS_CRON_CHECK_FINES_STS_OUTPUT_TABLE_SUFFIX='fines_checks/output_sts',
    AFS_CRON_CURSOR_USE_PGSQL='dry',
)
@pytest.mark.now('2021-06-23T00:01:04+03:00')
@pytest.mark.parametrize(
    'comment,'
    'data_sts,data_licenses,api_response,expected_requests,expected_headers,'
    'expected_output_data_sts,expected_output_data_licenses',
    [
        (
            'successful_check',
            [{'sts': '123456', 'created_timestamp': 1622134891}],
            [{'license': '9988776655', 'created_timestamp': 1622134892}],
            {},
            [
                {
                    'car': ['123456'],
                    'driver': [],
                    'ref': 'ym',
                    'supplierBillId': '',
                },
                {
                    'ref': 'ym',
                    'requestId': 'some_sts_request_id',
                    'supplierBillId': '',
                },
                {
                    'car': [],
                    'driver': ['9988776655'],
                    'ref': 'ym',
                    'supplierBillId': '',
                },
                {
                    'ref': 'ym',
                    'requestId': 'some_license_request_id',
                    'supplierBillId': '',
                },
            ],
            [
                {
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/90.0.4430.212 Safari/537.36'
                    ),
                    'X-CSRF-Token': 'VERYVERYSECRET',
                },
                {
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/90.0.4430.212 Safari/537.36'
                    ),
                    'X-CSRF-Token': 'VERYVERYSECRET',
                },
                {
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/90.0.4430.212 Safari/537.36'
                    ),
                    'X-CSRF-Token': 'VERYVERYSECRET',
                },
                {
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/90.0.4430.212 Safari/537.36'
                    ),
                    'X-CSRF-Token': 'VERYVERYSECRET',
                },
            ],
            [
                {
                    'charges': [{'reason': 'very bad car'}],
                    'created_timestamp': 1622134891,
                    'processed_timestamp': 1624395664.0,
                    'request_id': 'some_sts_request_id',
                    'status': 'success',
                    'sts': '123456',
                },
            ],
            [
                {
                    'charges': [{'reason': 'very bad driver'}],
                    'created_timestamp': 1622134892,
                    'processed_timestamp': 1624395664.0,
                    'license': '9988776655',
                    'request_id': 'some_license_request_id',
                    'status': 'success',
                },
            ],
        ),
    ],
)
async def test_cron(
        mock_secdist,  # pylint: disable=redefined-outer-name
        patch_aiohttp_session,
        response_mock,
        yt_apply,
        yt_client,
        cron_context,
        db,
        comment,
        data_sts,
        data_licenses,
        api_response,
        expected_requests,
        expected_headers,
        expected_output_data_sts,
        expected_output_data_licenses,
):
    yoomoney_api = _mock_yoomoney(patch_aiohttp_session, response_mock)

    _prepare_data(data_sts, data_licenses, yt_client)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME_STS)
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME_LICENSES)

    await run_cron.main(['taxi_antifraud.crontasks.check_fines', '-t', '0'])

    yoomoney_api_calls = list(yoomoney_api.calls)
    assert [x.get('json') for x in yoomoney_api_calls] == expected_requests
    assert [x.get('headers') for x in yoomoney_api_calls] == expected_headers

    assert (
        list(yt_client.read_table(YT_OUTPUT_TABLE_PATH_STS))
        == expected_output_data_sts
    )

    assert (
        list(yt_client.read_table(YT_OUTPUT_TABLE_PATH_LICENSES))
        == expected_output_data_licenses
    )

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME_STS: str(len(data_sts)),
        CURSOR_STATE_NAME_LICENSES: str(len(data_licenses)),
    }

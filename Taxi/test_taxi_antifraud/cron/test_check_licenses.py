import pytest

from taxi_antifraud.crontasks import check_licenses
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import state


YT_TABLE_PATH = '//home/taxi-fraud/unittests/license_checks/input'
YT_TABLE_PATH_OUTPUT = '//home/taxi-fraud/unittests/license_checks/output'

CURSOR_STATE_NAME = check_licenses.CURSOR_STATE_NAME


@pytest.mark.config(
    AFS_CRON_CHECK_LICENSES_CHECK_TRIES=3,
    AFS_CRON_CHECK_LICENSES_ENABLED=True,
    AFS_CRON_CHECK_LICENSES_INPUT_TABLE_SUFFIX='license_checks/input',
    AFS_CRON_CHECK_LICENSES_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CHECK_LICENSES_USE_DRIVE=True,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
@pytest.mark.now('2021-05-27T19:39:04')
async def test_cron(
        patch_aiohttp_session, response_mock, yt_client, cron_context,
):
    data = [
        {
            'license_number': 'K123KK750',
            'issue_date': '2020-02-31',
            'priority': 2,
            'created_timestamp': 1622134891,
        },
    ]

    requests = [
        {
            'Callback': 'taxi',
            'CallbackData': (
                '{"license_number": "K123KK750", "issue_date": "2020-02-31", '
                '"created_timestamp": 1622134891}'
            ),
            'CheckTries': 3,
            'LicenseIssueDate': '2020-02-31',
            'LicenseNumber': 'K123KK750',
            'Priority': 2,
        },
    ]

    @patch_aiohttp_session(check_licenses.DRIVE_API_STABLE, 'POST')
    def _drive_api(method, url, json, **kwargs):
        return response_mock(status=201)

    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(['taxi_antifraud.crontasks.check_licenses', '-t', '0'])

    assert [x.get('json') for x in _drive_api.calls] == requests

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }


@pytest.mark.config(
    AFS_CRON_CHECK_LICENSES_ENABLED=True,
    AFS_CRON_CHECK_LICENSES_INPUT_TABLE_SUFFIX='license_checks/input',
    AFS_CRON_CHECK_LICENSES_OUTPUT_TABLE_SUFFIX='license_checks/output',
    AFS_CRON_CHECK_LICENSES_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CHECK_LICENSES_USE_DRIVE=False,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
@pytest.mark.now('2021-05-27T19:39:04')
async def test_cron_via_gibdd(
        patch_aiohttp_session, response_mock, yt_client, cron_context,
):
    data = [
        {
            'license_number': 'K123KK750',
            'issue_date': '2020-02-31',
            'priority': 2,
            'created_timestamp': 1622134891,
        },
    ]

    requests = [{'date': '2020-02-31', 'num': 'K123KK750'}]

    output_rows = [
        {
            'code': 100,
            'count': 1,
            'created_timestamp': 1622134891,
            'decis': [
                {
                    'bplace': 'МОСКОВСКАЯ ОБЛ.',
                    'comment': 'ЛИШЕНИЕ ПРАВА УПРАВЛЕНИЯ ТС+ШТРАФ',
                    'date': '2015-01-15',
                    'fis_id': '50#50060463110010334246',
                    'reg_code': '1146',
                    'reg_name': 'МОСКОВСКАЯ ОБЛАСТЬ',
                    'srok': 18,
                    'state': '79',
                },
            ],
            'doc': {
                'bdate': '1982-04-13',
                'cat': 'В',
                'date': '2012-10-16',
                'divid': '4631',
                'division': 'РЭП ГИБДД РАМЕНСКОГО ОВД',
                'num': '1234567890',
                'srok': '2022-10-16',
                'st_kart': 'Т',
                'stag': '2002',
                'type': '45',
            },
            'hostname': 'h6-check1-dc',
            'issue_date': '2020-02-31',
            'license_number': 'K123KK750',
            'message': 'Ответ сервера успешно получен',
            'processed_timestamp': 1622133544.0,
            'requestTime': '19.05.2022 00:17',
        },
    ]

    @patch_aiohttp_session(check_licenses.GIBDD_API_URL, 'POST')
    def _gibdd_api(method, url, data, **kwargs):
        return response_mock(
            status=200,
            json={
                'requestTime': '19.05.2022 00:17',
                'hostname': 'h6-check1-dc',
                'code': 100,
                'count': 1,
                'doc': {
                    'date': '2012-10-16',
                    'bdate': '1982-04-13',
                    'num': '1234567890',
                    'type': '45',
                    'srok': '2022-10-16',
                    'division': 'РЭП ГИБДД РАМЕНСКОГО ОВД',
                    'stag': '2002',
                    'cat': 'В',
                    'st_kart': 'Т',
                    'divid': '4631',
                },
                'message': 'Ответ сервера успешно получен',
                'decis': [
                    {
                        'date': '2015-01-15',
                        'fis_id': '50#50060463110010334246',
                        'bplace': 'МОСКОВСКАЯ ОБЛ.',
                        'comment': 'ЛИШЕНИЕ ПРАВА УПРАВЛЕНИЯ ТС+ШТРАФ',
                        'reg_name': 'МОСКОВСКАЯ ОБЛАСТЬ',
                        'state': '79',
                        'srok': 18,
                        'reg_code': '1146',
                    },
                ],
            },
        )

    yt_client.create(
        'table', path=YT_TABLE_PATH, recursive=True, ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH, data)
    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)
    await run_cron.main(['taxi_antifraud.crontasks.check_licenses', '-t', '0'])

    assert [x.get('data') for x in _gibdd_api.calls] == requests

    assert list(yt_client.read_table(YT_TABLE_PATH_OUTPUT)) == output_rows

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }

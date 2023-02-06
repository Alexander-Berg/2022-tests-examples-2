from aiohttp import web
import pytest

from taxi_antifraud.crontasks import check_passports
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import state


YT_INPUT_TABLE_PATH = '//home/taxi-fraud/unittests/passport_checks/input'
YT_OUTPUT_TABLE_PATH = '//home/taxi-fraud/unittests/passport_checks/output'

CURSOR_STATE_NAME = check_passports.CURSOR_STATE_NAME


@pytest.fixture
def mock_secdist(simple_secdist):
    simple_secdist['settings_override'][
        'ANTIFRAUD_ANIMALS_PASSWORD'
    ] = 'very_secret_pass'
    return simple_secdist


def _prepare_data(data, yt_client):
    yt_client.create(
        'table',
        path=YT_INPUT_TABLE_PATH,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_INPUT_TABLE_PATH, data)
    yt_client.remove(YT_OUTPUT_TABLE_PATH, force=True)


@pytest.mark.config(
    AFS_CRON_CHECK_PASSPORTS_ENABLED=True,
    AFS_CRON_CHECK_PASSPORTS_INPUT_TABLE_SUFFIX='passport_checks/input',
    AFS_CRON_CHECK_PASSPORTS_OUTPUT_TABLE_SUFFIX='passport_checks/output',
    AFS_CRON_CHECK_PASSPORTS_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
@pytest.mark.now('2021-06-17T19:53:04')
@pytest.mark.parametrize(
    'comment,' 'data,api_response,expected_requests,expected_output_data',
    [
        (
            'successful_check',
            [
                {
                    'lastname': 'Иванов',
                    'firstname': 'Иван',
                    'middlename': 'Иванович',
                    'birthday': '12.11.1913',
                    'number': '8134578901',
                    'created_timestamp': 1622134891,
                },
                {
                    'lastname': 'Джонсон',
                    'firstname': 'Джон',
                    'middlename': 'Джонсович',
                    'birthday': '06.01.1917',
                    'number': '8374696423',
                    'doctype': '10',
                    'created_timestamp': 1622134892,
                },
            ],
            {'code': 1, 'inn': '025003742161', 'captchaRequired': False},
            [
                {
                    'bdate': '12.11.1913',
                    'bplace': '',
                    'c': 'innMy',
                    'captcha': '',
                    'captchaToken': '',
                    'docdt': '',
                    'docno': '81 34 578901',
                    'doctype': '21',
                    'fam': 'Иванов',
                    'nam': 'Иван',
                    'otch': 'Иванович',
                },
                {
                    'bdate': '06.01.1917',
                    'bplace': '',
                    'c': 'innMy',
                    'captcha': '',
                    'captchaToken': '',
                    'docdt': '',
                    'docno': '8374696423',
                    'doctype': '10',
                    'fam': 'Джонсон',
                    'nam': 'Джон',
                    'otch': 'Джонсович',
                },
            ],
            [
                {
                    'birthday': '12.11.1913',
                    'code': 1,
                    'created_timestamp': 1622134891,
                    'doctype': '21',
                    'firstname': 'Иван',
                    'inn': '025003742161',
                    'lastname': 'Иванов',
                    'middlename': 'Иванович',
                    'number': '8134578901',
                    'processed_timestamp': 1623948784.0,
                },
                {
                    'birthday': '06.01.1917',
                    'code': 1,
                    'created_timestamp': 1622134892,
                    'doctype': '10',
                    'firstname': 'Джон',
                    'inn': '025003742161',
                    'lastname': 'Джонсон',
                    'middlename': 'Джонсович',
                    'number': '8374696423',
                    'processed_timestamp': 1623948784.0,
                },
            ],
        ),
        (
            'failed_check',
            [
                {
                    'lastname': 'Петров',
                    'firstname': 'Петр',
                    'middlename': 'Петрович',
                    'birthday': '04.09.1923',
                    'number': '3847563946',
                    'created_timestamp': 1622134892,
                },
            ],
            {'code': 0, 'captchaRequired': False},
            [
                {
                    'bdate': '04.09.1923',
                    'bplace': '',
                    'c': 'innMy',
                    'captcha': '',
                    'captchaToken': '',
                    'docdt': '',
                    'docno': '38 47 563946',
                    'doctype': '21',
                    'fam': 'Петров',
                    'nam': 'Петр',
                    'otch': 'Петрович',
                },
            ],
            [
                {
                    'birthday': '04.09.1923',
                    'code': 0,
                    'created_timestamp': 1622134892,
                    'doctype': '21',
                    'firstname': 'Петр',
                    'inn': None,
                    'lastname': 'Петров',
                    'middlename': 'Петрович',
                    'number': '3847563946',
                    'processed_timestamp': 1623948784.0,
                },
            ],
        ),
        (
            'missing_middlename',
            [
                {
                    'lastname': 'Сидоров',
                    'firstname': 'Сидор',
                    'middlename': '',
                    'birthday': '01.01.1945',
                    'number': '3867394622',
                    'created_timestamp': 1622134893,
                },
            ],
            {'code': 1, 'inn': '394563475634', 'captchaRequired': False},
            [
                {
                    'bdate': '01.01.1945',
                    'bplace': '',
                    'c': 'innMy',
                    'captcha': '',
                    'captchaToken': '',
                    'docdt': '',
                    'docno': '38 67 394622',
                    'doctype': '21',
                    'fam': 'Сидоров',
                    'nam': 'Сидор',
                    'opt_otch': '1',
                },
            ],
            [
                {
                    'birthday': '01.01.1945',
                    'code': 1,
                    'created_timestamp': 1622134893,
                    'doctype': '21',
                    'firstname': 'Сидор',
                    'inn': '394563475634',
                    'lastname': 'Сидоров',
                    'middlename': '',
                    'number': '3867394622',
                    'processed_timestamp': 1623948784.0,
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
        db,
        cron_context,
        comment,
        data,
        api_response,
        expected_requests,
        expected_output_data,
):
    @patch_aiohttp_session(check_passports.NALOG_RU_URL, 'POST')
    def _nalog_api(method, url, data, **kwargs):
        return response_mock(json=api_response)

    _prepare_data(data, yt_client)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.check_passports', '-t', '0'],
    )

    assert [x.get('data') for x in _nalog_api.calls] == expected_requests

    assert (
        list(yt_client.read_table(YT_OUTPUT_TABLE_PATH))
        == expected_output_data
    )

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }


@pytest.mark.config(
    AFS_CRON_CHECK_PASSPORTS_ENABLED=True,
    AFS_CRON_CHECK_PASSPORTS_INPUT_TABLE_SUFFIX='passport_checks/input',
    AFS_CRON_CHECK_PASSPORTS_OUTPUT_TABLE_SUFFIX='passport_checks/output',
    AFS_CRON_CHECK_PASSPORTS_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CHECK_PASSPORTS_USE_SELFEMPLOYED=True,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
@pytest.mark.now('2022-02-16T00:00:04')
@pytest.mark.parametrize(
    'comment,data,is_valid,expected_output_data',
    [
        (
            'successful_check',
            [
                {
                    'lastname': 'Иванов',
                    'firstname': 'Иван',
                    'middlename': 'Иванович',
                    'birthday': '12.11.1913',
                    'number': '8134578901',
                    'created_timestamp': 1622134891,
                },
                {
                    'lastname': 'Джонсон',
                    'firstname': 'Джон',
                    'middlename': 'Джонсович',
                    'birthday': '06.01.1917',
                    'number': '8374696423',
                    'created_timestamp': 1622134892,
                },
            ],
            True,
            [
                {
                    'birthday': '12.11.1913',
                    'code': 1,
                    'created_timestamp': 1622134891,
                    'firstname': 'Иван',
                    'lastname': 'Иванов',
                    'middlename': 'Иванович',
                    'number': '8134578901',
                    'processed_timestamp': 1644958804.0,
                },
                {
                    'birthday': '06.01.1917',
                    'code': 1,
                    'created_timestamp': 1622134892,
                    'firstname': 'Джон',
                    'lastname': 'Джонсон',
                    'middlename': 'Джонсович',
                    'number': '8374696423',
                    'processed_timestamp': 1644958804.0,
                },
            ],
        ),
        (
            'failed_check',
            [
                {
                    'lastname': 'Петров',
                    'firstname': 'Петр',
                    'middlename': 'Петрович',
                    'birthday': '04.09.1923',
                    'number': '3847563946',
                    'created_timestamp': 1622134892,
                },
            ],
            False,
            [
                {
                    'birthday': '04.09.1923',
                    'code': 0,
                    'created_timestamp': 1622134892,
                    'firstname': 'Петр',
                    'lastname': 'Петров',
                    'middlename': 'Петрович',
                    'number': '3847563946',
                    'processed_timestamp': 1644958804.0,
                },
            ],
        ),
        (
            'missing_middlename',
            [
                {
                    'lastname': 'Сидоров',
                    'firstname': 'Сидор',
                    'middlename': '',
                    'birthday': '01.01.1945',
                    'number': '3867394622',
                    'created_timestamp': 1622134893,
                },
            ],
            True,
            [
                {
                    'birthday': '01.01.1945',
                    'code': 1,
                    'created_timestamp': 1622134893,
                    'firstname': 'Сидор',
                    'lastname': 'Сидоров',
                    'middlename': '',
                    'number': '3867394622',
                    'processed_timestamp': 1644958804.0,
                },
            ],
        ),
    ],
)
async def test_selfemployed(
        mock_selfemployed,
        yt_apply,
        yt_client,
        cron_context,
        comment,
        data,
        is_valid,
        expected_output_data,
):
    @mock_selfemployed('/admin/selfemployed-check-passport/')
    async def _check_passport(request):
        assert request.method == 'POST'
        if not is_valid:
            return web.json_response(
                status=404,
                data={'code': '404', 'text': 'Passport is not valid'},
            )
        return web.json_response(data={'message': 'Passport is valid'})

    _prepare_data(data, yt_client)

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.check_passports', '-t', '0'],
    )

    assert (
        list(yt_client.read_table(YT_OUTPUT_TABLE_PATH))
        == expected_output_data
    )

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }

import datetime

import pytest
import pytz

from personal_py3.generated.cron import run_cron

PERSONAL_YT_DIR = '//home/taxi/unittests/services/personal-py3'


def return_in_personal_mock(request):
    assert request.json == {
        'items': [{'id': 'pd_id_1'}, {'id': 'pd_id_2'}],
        'primary_replica': False,
    }
    return {
        'items': [
            {'id': 'pd_id_1', 'value': '+11111111111'},
            {'id': 'pd_id_2', 'value': '+22222222222'},
        ],
    }


async def check_db_and_yt_table(yt_client, item_name, data_type, cron_context):
    result_table = (
        PERSONAL_YT_DIR + '/' + f'{data_type}_replication/{data_type}_table'
    )
    responses = [
        {'id': 'pd_id_1', item_name: '+11111111111'},
        {'id': 'pd_id_2', item_name: '+22222222222'},
        {'id': 'pd_id_default_1', item_name: '+1'},
        {'id': 'pd_id_default_2', item_name: '+2'},
    ]
    for response in responses:
        row = list(
            yt_client.select_rows(
                f'(id, {item_name}) FROM [{result_table}] '
                f'WHERE id = "{response["id"]}"',
            ),
        )
        assert row == [response]

    result = await cron_context.pg.master_pool.fetchrow(
        'select last_created from yt_export.last_synced_created_time '
        'WHERE data_type = $1',
        data_type,
    )
    assert result['last_created'] == datetime.datetime(
        2020, 10, 30, 12, 7, tzinfo=pytz.utc,
    )


@pytest.mark.yt(dyn_table_data=['yt_phones_table.yaml'])
async def test_phones_yt_export(yt_client, yt_apply, mockserver, cron_context):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _phones_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(['personal_py3.crontasks.phones_yt_export', '-t', '0'])
    assert _phones_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(yt_client, 'phone', 'phones', cron_context)


@pytest.mark.yt(dyn_table_data=['yt_driver_licenses_table.yaml'])
async def test_driver_licenses_yt_export(
        yt_client, yt_apply, mockserver, cron_context,
):
    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    async def _driver_licenses_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(
        ['personal_py3.crontasks.driver_licenses_yt_export', '-t', '0'],
    )
    assert _driver_licenses_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(
        yt_client, 'driver_license', 'driver_licenses', cron_context,
    )


@pytest.mark.yt(dyn_table_data=['yt_identifications_table.yaml'])
async def test_identifications_yt_export(
        yt_client, yt_apply, mockserver, cron_context,
):
    @mockserver.json_handler('/personal/v1/identifications/bulk_retrieve')
    async def _identifications_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(
        ['personal_py3.crontasks.identifications_yt_export', '-t', '0'],
    )
    assert _identifications_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(
        yt_client, 'identification', 'identifications', cron_context,
    )


@pytest.mark.yt(dyn_table_data=['yt_tins_table.yaml'])
async def test_tins_yt_export(yt_client, yt_apply, mockserver, cron_context):
    @mockserver.json_handler('/personal/v1/tins/bulk_retrieve')
    async def _tins_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(['personal_py3.crontasks.tins_yt_export', '-t', '0'])
    assert _tins_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(yt_client, 'tin', 'tins', cron_context)


@pytest.mark.yt(dyn_table_data=['yt_emails_table.yaml'])
async def test_emails_yt_export(yt_client, yt_apply, mockserver, cron_context):
    @mockserver.json_handler('/personal/v1/emails/bulk_retrieve')
    async def _emails_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(['personal_py3.crontasks.emails_yt_export', '-t', '0'])
    assert _emails_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(yt_client, 'email', 'emails', cron_context)


@pytest.mark.yt(dyn_table_data=['yt_yandex_logins_table.yaml'])
async def test_yandex_logins_yt_export(
        yt_client, yt_apply, mockserver, cron_context,
):
    @mockserver.json_handler('/personal/v1/yandex_logins/bulk_retrieve')
    async def _yandex_logins_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(
        ['personal_py3.crontasks.yandex_logins_yt_export', '-t', '0'],
    )
    assert _yandex_logins_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(
        yt_client, 'yandex_login', 'yandex_logins', cron_context,
    )


@pytest.mark.yt(dyn_table_data=['yt_telegram_logins_table.yaml'])
async def test_telegram_logins_yt_export(
        yt_client, yt_apply, mockserver, cron_context,
):
    @mockserver.json_handler('/personal/v1/telegram_logins/bulk_retrieve')
    async def _telegram_logins_bulk_retrieve(request):
        return return_in_personal_mock(request)

    await run_cron.main(
        ['personal_py3.crontasks.telegram_logins_yt_export', '-t', '0'],
    )
    assert _telegram_logins_bulk_retrieve.times_called == 1
    await check_db_and_yt_table(
        yt_client, 'telegram_login', 'telegram_logins', cron_context,
    )

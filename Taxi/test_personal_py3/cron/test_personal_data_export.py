import pytest
import yt.wrapper as yt_wrapper_orig

from personal_py3.generated.cron import run_cron
from personal_py3.utils import admin_consts

TICKET = 'TESTTICKET-1'


def _personal_response(prefix):
    return {
        'items': [
            {'id': prefix + '_id_1', 'value': prefix + '_value_1'},
            {'id': prefix + '_id_2', 'value': prefix + '_value_2'},
        ],
    }


@pytest.fixture(name='cron_mocks')
def _cron_mocks(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    async def _phones_bulk_retrieve(request):
        assert request.json['primary_replica'] is not None
        assert not request.json['primary_replica']

        items = request.json['items']
        if items == [{'id': 'phone_id_1'}, {'id': 'phone_id_2'}]:
            return _personal_response('phone')
        if items == [{'id': 'other_phone_id_1'}, {'id': 'other_phone_id_2'}]:
            return _personal_response('other_phone')
        assert False

    @mockserver.json_handler('/personal/v1/phones/bulk_find')
    async def _phones_bulk_find(request):
        assert request.json == {
            'items': [{'value': 'phone_value_1'}, {'value': 'phone_value_2'}],
            'primary_replica': False,
        }
        return _personal_response('phone')

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_retrieve')
    async def _driver_licenses_bulk_retrieve(request):
        assert request.json == {
            'items': [
                {'id': 'driver_license_id_1'},
                {'id': 'driver_license_id_2'},
            ],
            'primary_replica': False,
        }
        return _personal_response('driver_license')

    @mockserver.json_handler('/personal/v1/driver_licenses/bulk_find')
    async def _driver_licenses_bulk_find(request):
        assert request.json == {
            'items': [
                {'value': 'driver_license_value_1'},
                {'value': 'driver_license_value_2'},
            ],
            'primary_replica': False,
        }
        return _personal_response('driver_license')

    @mockserver.json_handler('/idm/api/v1/rolerequests/')
    async def _mock_idm(request):
        assert request.json['path'] == '/read/'
        assert request.json['fields_data'] == {
            'path': f'//home/taxi/unittests/services/personal-py3/{TICKET}',
        }
        data = {
            'path': '/read/',
            'user': request.json['user'],
            'id': 'idm_request_id',
        }
        return data

    @mockserver.json_handler(f'/startrek/issues/{TICKET}/comments')
    def _create_comment(request):
        text = request.json['text']
        assert 'Выгрузка персональных данных' in text


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
@pytest.mark.parametrize(
    'pd_export_id, expected_status, expected_yt_columns, expected_yt_values',
    [
        (
            1,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id',
                'phone_id__phone__converted',
                'driver_license_id',
                'driver_license_id__driver_license__converted',
            },
            None,
        ),
        (
            2,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id',
                'phone_id__phone__converted',
                'phone_id__phone__status',
                'driver_license_id',
                'driver_license_id__driver_license__converted',
                'driver_license_id__driver_license__status',
            },
            None,
        ),
        (
            3,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id__phone__converted',
                'other_phone_id',
                'phone',
                'driver_license_id__driver_license__converted',
                'driver_license',
                'extra_column',
                'extra_column_int',
                'extra_column_uint',
                'extra_column_double',
                'extra_column_bool',
                'extra_column_utf',
                'extra_column_binary',
            },
            None,
        ),
        (
            4,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id__phone__converted',
                'phone_id__phone__status',
                'other_phone_id',
                'phone',
                'driver_license_id__driver_license__converted',
                'driver_license_id__driver_license__status',
                'driver_license',
                'extra_column',
                'extra_column_int',
                'extra_column_uint',
                'extra_column_double',
                'extra_column_bool',
                'extra_column_utf',
                'extra_column_binary',
            },
            None,
        ),
        (5, admin_consts.ExportStatus.NEED_RETRY, None, None),
        (
            6,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id',
                'other_phone_id',
                'phone__phone_id__converted',
                'phone__phone_id__status',
                'driver_license_id',
                'driver_license__driver_license_id__converted',
                'driver_license__driver_license_id__status',
                'extra_column',
                'extra_column_int',
                'extra_column_uint',
                'extra_column_double',
                'extra_column_bool',
                'extra_column_utf',
                'extra_column_binary',
            },
            None,
        ),
        (7, admin_consts.ExportStatus.FINISHED, None, None),
        (
            111,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id',
                'phone_id__phone__converted',
                'other_phone_id',
                'other_phone_id__phone__converted',
                'phone',
                'phone__phone_id__converted',
                'driver_license_id',
                'driver_license_id__driver_license__converted',
                'driver_license',
                'driver_license__driver_license_id__converted',
            },
            [
                {
                    b'phone_id': b'phone_id_1',
                    b'phone_id__phone__converted': b'phone_value_1',
                },
                {
                    b'phone_id': b'phone_id_2',
                    b'phone_id__phone__converted': b'phone_value_2',
                },
                {b'phone_id': None, b'phone_id__phone__converted': None},
            ],
        ),
        (
            222,
            admin_consts.ExportStatus.FINISHED,
            {
                'phone_id__phone__converted',
                'phone_id__phone__status',
                'other_phone_id__phone__converted',
                'other_phone_id__phone__status',
                'phone__phone_id__converted',
                'phone__phone_id__status',
                'driver_license_id__driver_license__converted',
                'driver_license_id__driver_license__status',
                'driver_license__driver_license_id__converted',
                'driver_license__driver_license_id__status',
                'extra_column',
                'extra_column_int',
                'extra_column_uint',
                'extra_column_double',
                'extra_column_bool',
                'extra_column_utf',
                'extra_column_binary',
            },
            [
                {
                    b'phone_id__phone__converted': b'phone_value_1',
                    b'phone_id__phone__status': b'OK',
                    b'extra_column': b'extra_value_1',
                    b'extra_column_int': -123,
                    b'extra_column_uint': 123,
                    b'extra_column_double': 123.456,
                    b'extra_column_bool': False,
                    b'extra_column_utf': b'utf-8-string',
                    b'extra_column_binary': b'\xff',
                },
                {
                    b'phone_id__phone__converted': b'phone_value_2',
                    b'phone_id__phone__status': b'OK',
                    b'extra_column': b'extra_value_2',
                    b'extra_column_int': None,
                    b'extra_column_uint': None,
                    b'extra_column_double': None,
                    b'extra_column_bool': None,
                    b'extra_column_utf': None,
                    b'extra_column_binary': b'extra_value_2',
                },
                {
                    b'phone_id__phone__converted': None,
                    b'phone_id__phone__status': b'NOT FOUND',
                    b'extra_column': b'extra_value_3',
                    b'extra_column_binary': None,
                },
            ],
        ),
    ],
)
async def test_personal_data_export(
        yt_client,
        yt_apply,
        cron_mocks,
        cron_context,
        testpoint,
        cron_runner,
        pd_export_id,
        expected_status,
        expected_yt_columns,
        expected_yt_values,
):
    @testpoint('table_path_tp')
    async def table_path_testpoint_handler(data):
        assert data['id'] == pd_export_id
        assert (
            set(
                column['name']
                for column in yt_client.get(data['table_path'] + '/@schema')
            )
            == expected_yt_columns
        )
        assert yt_client.row_count(data['table_path']) == 3

        if expected_yt_values is not None:
            yt_rows = list(
                yt_client.read_table(
                    data['table_path'],
                    format=yt_wrapper_orig.YsonFormat(
                        format='binary', encoding=None,
                    ),
                ),
            )
            assert len(yt_rows) == len(expected_yt_values)
            for yt_row, expected_values in zip(yt_rows, expected_yt_values):
                for key, value in expected_values.items():
                    assert yt_row[key] == value

    async with cron_context.pg.master_pool.acquire() as conn:
        await conn.execute(
            'UPDATE personal_export.export_info '
            'SET status = \'finished\' '
            'WHERE id != $1;',
            pd_export_id,
        )

    await cron_runner.personal_data_export()

    assert table_path_testpoint_handler.times_called == int(
        expected_yt_columns is not None,
    )

    result = await cron_context.pg.master_pool.fetchrow(
        'SELECT status FROM personal_export.export_info WHERE id = $1',
        pd_export_id,
    )
    assert result['status'] == expected_status.value


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_personal_data_export_startrack_error(
        mockserver, yt_client, yt_apply, cron_mocks, cron_context,
):
    @mockserver.json_handler(f'/startrek/issues/{TICKET}/comments')
    def _create_comment(request):
        return mockserver.make_response(
            status=500, json={'code': 'internal error'},
        )

    await run_cron.main(
        ['personal_py3.crontasks.personal_data_export', '-t', '0'],
    )
    result = await cron_context.pg.master_pool.fetchrow(
        'select status from personal_export.export_info '
        'where yandex_login = \'test_login\'',
    )
    assert result['status'] == admin_consts.ExportStatus.NEED_POST_MSG.value


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_personal_data_export_startrack_error_mark_as_finished(
        mockserver, yt_client, yt_apply, cron_mocks, cron_context,
):
    @mockserver.json_handler(f'/startrek/issues/{TICKET}/comments')
    def _create_comment(request):
        return mockserver.make_response(
            status=500, json={'code': 'internal error'},
        )

    await run_cron.main(
        ['personal_py3.crontasks.personal_data_export', '-t', '0'],
    )
    result = await cron_context.pg.master_pool.fetchrow(
        'select status from personal_export.export_info '
        'where yandex_login = \'test_login_need_post_msg_status\'',
    )
    assert result['status'] == admin_consts.ExportStatus.FINISHED.value


@pytest.mark.yt(static_table_data=['yt_pd_input_table.yaml'])
async def test_personal_data_export_yt_error(
        yt_client, yt_apply, cron_mocks, cron_context,
):
    await run_cron.main(
        ['personal_py3.crontasks.personal_data_export', '-t', '0'],
    )
    result = await cron_context.pg.master_pool.fetchrow(
        'select status from personal_export.export_info '
        'where yandex_login = \'test_login_wrong_input_table\'',
    )
    assert result['status'] == admin_consts.ExportStatus.NEED_RETRY.value

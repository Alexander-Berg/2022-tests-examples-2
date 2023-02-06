import pytest
import xlrd

from taxi_corp.stq import export_users_cabinet
from . import test_user_report_util as util

HEADERS_NEW_CC = ('Настройки центров затрат',)

USERS = {
    'good user': (
        'good user',
        '+79654646546',
        'svyat@yandex-team.ru',
        '',
        'Активен',
        'department 1',
        '2000/month',
        '1000/month',
        'inf',
        'inf',
        '',
        '',
    ),
    'user in root department': (
        'user in root department',
        '+79654646545',
        'svyat@yandex-team.ru',
        '',
        'Активен',
        '',
        '2000/month',
        '',
        '',
        '',
        '',
        'Основной',
    ),
    'fullname': (
        'fullname',
        '+79654646543',
        'svyat@yandex-team.ru',
        '',
        'Активен',
        'department 1.1',
        '2000/month',
        '',
        '',
        '',
        '',
        'Основной',
    ),
    'user 4': (
        'user 4',
        '+79654646345',
        '',
        '',
        'Активен',
        'department 1',
        '',
        '1000/month',
        '',
        '',
        '',
        'Основной',
    ),
    'user 5': (
        'user 5',
        '+79654646123',
        '',
        '',
        'Неактивен',
        'department 1',
        '',
        '1000/month',
        '',
        '',
        '',
        '',
    ),
    'Drive user': (
        'Drive user',
        '+79990001122',
        'user6@yandex-team.ru',
        '',
        'Активен',
        'department 1',
        '',
        '',
        '',
        '',
        '',
        '',
    ),
}


@pytest.mark.now('2020-02-02T03:00:00.000')
@pytest.mark.parametrize(
    ['extension', 'expected_task'],
    [
        pytest.param(
            'xls',
            {
                'status': 'complete',
                'response_data': {
                    'result': {
                        'mds_key': 'mds_key_id',
                        'file_name': 'result.xls',
                        'content_type': 'application/vnd.ms-excel',
                    },
                },
            },
        ),
        pytest.param(
            'xlsx',
            {
                'status': 'complete',
                'response_data': {
                    'result': {
                        'mds_key': 'mds_key_id',
                        'file_name': 'result.xlsx',
                        'content_type': (
                            'application/'
                            'vnd.openxmlformats-officedocument.spreadsheetml'
                        ),
                    },
                },
            },
        ),
    ],
)
@pytest.mark.parametrize(
    ['task_args', 'expected_content'],
    [
        pytest.param(
            {'client_id': 'client3', 'department_id': None},
            util.get_headers_cells(
                util.HEADERS_CABINET + HEADERS_NEW_CC,
                report_date='2020-02-02',
                company='client3_name',
            )
            + [
                USERS['good user'],
                USERS['user in root department'],
                USERS['fullname'],
                USERS['user 4'],
                USERS['user 5'],
                USERS['Drive user'],
            ],
        ),
        pytest.param(
            {'client_id': 'client3', 'department_id': 'dep1_1'},
            util.get_headers_cells(
                util.HEADERS_CABINET + HEADERS_NEW_CC,
                report_date='2020-02-02',
                company='client3_name',
            )
            + [USERS['fullname']],
        ),
    ],
)
@pytest.mark.translations(corp=util.CORP_TRANSLATIONS)
@pytest.mark.config(LOCALES_CORP_SUPPORTED=['ru', 'en'])
async def test_main(
        pd_patch,
        patch,
        taxi_corp_app_stq,
        db,
        task_args,
        extension,
        expected_content,
        expected_task,
):
    @patch('taxi.stq.client.put')
    async def _put(*args, **kwargs):
        pass

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        book = xlrd.open_workbook(file_contents=kwargs['file_obj'])
        sheet = book.sheet_by_index(0)
        actual_content = [
            tuple(col.value for col in row) for row in sheet.get_rows()
        ]
        assert sorted(actual_content, key=lambda x: x[0]) == sorted(
            expected_content, key=lambda x: x[0],
        )
        return 'mds_key_id'

    task_id = 'task0'
    task_args.update({'format': extension})

    await db.corp_long_tasks.update_one(
        {'_id': task_id}, {'$set': {'task_args': task_args}},
    )

    task_kwargs = {
        'task_id': task_id,
        'request_info': {
            'login': 'corp-test',
            'uid': '4010776088',
            'method': 'POST',
            'user_ip': '2a02:6b8:c0f:4:0:42d5:a437:0',
            'locale': 'ru',
        },
    }

    await export_users_cabinet.export_users(taxi_corp_app_stq, **task_kwargs)

    task = await db.corp_long_tasks.find_one({'_id': task_id})

    for k, val in expected_task.items():
        assert task[k] == val

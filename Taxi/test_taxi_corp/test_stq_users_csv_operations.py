# pylint: disable=redefined-outer-name
import datetime
import hashlib

import bson
import pytest

from taxi_corp.stq import users_csv_operations

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(
        corp={
            'error.users.validation': {
                'ru': 'Ошибка в столбце {} в строке {}',
            },
            'error.required_field.csv_validation': {
                'ru': 'Нет обязательного поля {} на строке {}',
            },
            'error.departments.csv_validation': {
                'ru': 'Ошибка валидации департаментов на строке {}',
            },
            'error.cost_center.csv_validation': {
                'ru': 'Неправильно указан центр затрат на строке {}',
            },
            'error.user_creation.csv_validation': {
                'ru': 'Ошибка при создании сотрудника на строке {}',
            },
            'error.ids.csv_validation': {
                'ru': 'Ошибка. Такого id не существует на строке {}',
            },
            'error.duplicate_phone.csv_validation': {
                'ru': (
                    'Ошибка. Обнаружен дубликат'
                    ' телефонного номера на строке {}'
                ),
            },
            'error.deleted_user.csv_validation': {
                'ru': (
                    'Ошибка. Попытка изменить или создать'
                    ' удаленного сотрудника на строке {}'
                ),
            },
            'error.duplicate_id.csv_validation': {
                'ru': 'Ошибка. Обнаружен дубликат id на строке {}',
            },
            'error.limits.csv_validation': {
                'ru': 'Ошибка при валидации лимитов на строке {}',
            },
            'error.users.csv_parse': {'ru': 'Ошибка в структуре csv файла'},
        },
    ),
]
NOW_DATETIME = datetime.datetime(year=2021, month=4, day=14)


@pytest.fixture
def personal_csv_mock(patch):
    @patch('taxi.clients.user_api.UserApiClient.create_user_phone')
    async def _create_user_phone(phone, *args, **kwargs):
        return {
            '_id': bson.ObjectId(
                hashlib.md5(phone.encode('utf-8')).hexdigest()[:24],
            ),
        }

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': '{}_id'.format(request_value)}


@pytest.fixture
def personal_csv_mock_invalid(patch):
    @patch('taxi.clients.user_api.UserApiClient.create_user_phone')
    async def _create_user_phone(phone, *args, **kwargs):
        return {
            '_id': bson.ObjectId(
                hashlib.md5(phone.encode('utf-8')).hexdigest()[:24],
            ),
        }

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'xxx': 'zzz'}


async def test_export_users(taxi_corp_app_stq, patch, db, load_binary):
    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        result = kwargs['file_obj'].decode('utf-8-sig').replace('\r', '')
        expected = (
            load_binary('result.csv').decode('utf-8-sig').replace('\r\n', '')
        )
        assert expected == result
        return 'mds_key'

    long_task = await db.corp_long_tasks.find_one({'_id': 'new_task'})
    assert long_task['status'] == 'init'

    await users_csv_operations.export_users(
        taxi_corp_app_stq, 'new_task', {'locale': 'ru'},
    )

    long_task = await db.corp_long_tasks.find_one({'_id': 'new_task'})
    users = await db.corp_users.count({'client_id': 'client1'})
    assert long_task['status'] == 'complete'
    assert long_task['progress']['processed_size'] == users
    assert long_task['exec_tries'] == 1


async def test_export_auxiliary_dictionary(
        taxi_corp_app_stq, patch, db, load_binary,
):
    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        result = kwargs['file_obj'].decode('utf-8-sig').replace('\r', '')
        expected = (
            load_binary('result_auxiliary.csv')
            .decode('utf-8-sig')
            .replace('\r\n', '')
        )
        assert expected == result
        return 'mds_key'

    long_task = await db.corp_long_tasks.find_one({'_id': 'new_task'})
    assert long_task['status'] == 'init'

    await users_csv_operations.export_auxiliary_dictionary(
        taxi_corp_app_stq, 'new_task', {'locale': 'ru'},
    )

    long_task = await db.corp_long_tasks.find_one({'_id': 'new_task'})
    limits = await db.corp_limits.count({'client_id': 'client1'})
    cost_centers = await db.corp_cost_center_options.count(
        {'client_id': 'client1'},
    )
    departments = await db.corp_departments.count({'client_id': 'client1'})

    assert long_task['status'] == 'complete'
    assert (
        long_task['progress']['processed_size']
        == limits + cost_centers + departments
    )
    assert long_task['exec_tries'] == 1


async def test_import_create_users(
        taxi_corp_app_stq,
        personal_csv_mock,
        patch,
        db,
        load_binary,
        load_json,
):
    await taxi_corp_app_stq.phones.refresh_cache()

    @patch('taxi.clients.mds.MDSClient.download')
    async def _download(**kwargs):
        return load_binary('import_create.csv')

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        return 'mds_key'

    @patch('taxi_corp.internal.limits_helper._generate_drive_task_id')
    def _uuid4():
        return '66051e1659be4c7dbb19fec53360717c'

    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})
    assert long_task['status'] == 'waiting'

    await users_csv_operations.import_users(
        taxi_corp_app_stq,
        task_id='import_task',
        request_info={
            'locale': 'ru',
            'login': 'there',
            'uid': 'uid',
            'method': 'method',
            'user_ip': 'ip',
        },
    )
    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})

    assert long_task['status'] == 'complete'
    assert long_task['response_data']['result']['updated'] == 0
    assert long_task['response_data']['result']['created'] == 4
    assert long_task['response_data']['result'].get('errors', []) == []

    expected = load_json('import_create_result.json')
    phone_list = [
        '+79291112312',
        '+79291112314',
        '+79291112917',
        '+79291112918',
    ]
    result = await db.secondary.corp_users.find(
        {'phone': {'$in': phone_list}},
        projection={
            'created': False,
            'updated': False,
            'phone_id': False,
            '_id': False,
        },
    ).to_list(None)

    assert result == expected


async def test_import_update_users(
        taxi_corp_app_stq,
        personal_csv_mock,
        patch,
        db,
        load_binary,
        load_json,
):
    await taxi_corp_app_stq.phones.refresh_cache()

    @patch('taxi.clients.mds.MDSClient.download')
    async def _download(**kwargs):
        return load_binary('import_update.csv')

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        return 'mds_key'

    @patch('taxi_corp.internal.limits_helper._generate_drive_task_id')
    def _uuid4():
        return '66051e1659be4c7dbb19fec53360717c'

    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})
    assert long_task['status'] == 'waiting'

    await users_csv_operations.import_users(
        taxi_corp_app_stq,
        task_id='import_task',
        request_info={
            'locale': 'ru',
            'login': 'there',
            'uid': 'uid',
            'method': 'method',
            'user_ip': 'ip',
        },
    )
    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})

    assert long_task['status'] == 'complete'
    assert long_task['response_data']['result']['updated'] == 9
    assert long_task['response_data']['result']['created'] == 0
    assert long_task['response_data']['result'].get('errors', []) == []

    expected = load_json('import_update_result.json')
    result = await db.secondary.corp_users.find(
        {}, projection={'updated': False, 'phone_id': False},
    ).to_list(None)

    assert result == expected


@pytest.mark.parametrize(
    ['import_file_name', 'result_filename', 'errors'],
    [
        pytest.param(
            'broken_import.csv',
            None,
            ['Ошибка в структуре csv файла'],
            id='validate csv structure errors',
        ),
        pytest.param(
            'import_invalid_users_scheme_format.csv',
            'import_invalid_users_scheme_format_result.csv',
            [
                'Ошибка в столбце email в строке 2',
                'Ошибка в столбце phone в строке 3',
                'Ошибка в столбце phone в строке 4',
            ],
            id='validate input format errors',
        ),
        pytest.param(
            'import_invalid_users_data_input.csv',
            'import_invalid_users_data_input_result.csv',
            [
                'Неправильно указан центр затрат на строке 3',
                'Неправильно указан центр затрат на строке 5',
                'Ошибка валидации департаментов на строке 5',
                'Ошибка валидации департаментов на строке 9',
                'Ошибка при валидации лимитов на строке 9',
                'Ошибка при валидации лимитов на строке 12',
                'Ошибка. Обнаружен дубликат id на строке 3',
                'Ошибка. Такого id не существует на строке 4',
                'Ошибка. Обнаружен дубликат телефонного номера на строке 11',
            ],
            id='validate input data errors',
        ),
    ],
)
async def test_import_users_invalid_input(
        taxi_corp_app_stq,
        personal_csv_mock,
        patch,
        db,
        load_binary,
        tvm_client,
        import_file_name,
        result_filename,
        errors,
):
    await taxi_corp_app_stq.phones.refresh_cache()

    @patch('taxi.clients.mds.MDSClient.download')
    async def _download(**kwargs):
        return load_binary(import_file_name)

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        if result_filename:
            result = kwargs['file_obj'].decode('utf-8-sig').replace('\r', '')
            expected = (
                load_binary(result_filename)
                .decode('utf-8-sig')
                .replace('\r\n', '')
            )
            assert expected == result
            return 'mds_key'

    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})
    assert long_task['status'] == 'waiting'

    total_users = await db.corp_users.count()

    await users_csv_operations.import_users(
        taxi_corp_app_stq,
        task_id='import_task',
        request_info={
            'locale': 'ru',
            'login': 'there',
            'uid': 'uid',
            'method': 'method',
            'user_ip': 'ip',
        },
    )

    assert total_users == await db.corp_users.count()
    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})
    assert long_task['status'] == 'error'
    assert long_task['response_data']['result']['errors'] == errors


async def test_import_create_users_invalid_upsert(
        taxi_corp_app_stq,
        personal_csv_mock_invalid,
        patch,
        db,
        load_binary,
        load_json,
):
    await taxi_corp_app_stq.phones.refresh_cache()

    @patch('taxi.clients.mds.MDSClient.download')
    async def _download(**kwargs):
        return load_binary('import_create.csv')

    @patch('taxi.clients.mds.MDSClient.upload')
    async def _upload(**kwargs):
        result = kwargs['file_obj'].decode('utf-8-sig').replace('\r', '')
        expected = (
            load_binary('invalid_upsert.csv')
            .decode('utf-8-sig')
            .replace('\r\n', '')
        )
        assert expected == result
        return 'mds_key'

    @patch('taxi_corp.internal.limits_helper._generate_drive_task_id')
    def _uuid4():
        return '66051e1659be4c7dbb19fec53360717c'

    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})
    assert long_task['status'] == 'waiting'

    await users_csv_operations.import_users(
        taxi_corp_app_stq,
        task_id='import_task',
        request_info={
            'locale': 'ru',
            'login': 'there',
            'uid': 'uid',
            'method': 'method',
            'user_ip': 'ip',
        },
    )
    long_task = await db.corp_long_tasks.find_one({'_id': 'import_task'})

    assert long_task['status'] == 'error'

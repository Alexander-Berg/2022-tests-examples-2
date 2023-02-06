import datetime
import uuid

import aiohttp
import pytest

from . import test_client_cost_centers_util as util


@pytest.mark.parametrize(
    ['client_id', 'cost_centers', 'expected_cost_centers', 'file_name'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            ['foo', 'bar', 'FOO'],
            ['bar', 'foo'],
            'cost_centers.xls',
        ),
        (
            '79110cc5c5754ac787f80e7452dee5c8',
            ['foo', 'bar', 'FOO'],
            ['bar', 'foo'],
            'new_cost_centers.xls',
        ),
        (
            '79110cc5c5754ac787f80e7452dee5c8',
            ['foo', 'bar', 42, 13.0, 7.25],
            ['13', '42', '7.25', 'bar', 'foo'],
            'new_cost_centers.xls',
        ),
    ],
)
async def test_single_put(
        taxi_corp_auth_client,
        db,
        client_id,
        cost_centers,
        expected_cost_centers,
        file_name,
):

    writer = aiohttp.MultipartWriter('form-data')
    payload = aiohttp.payload.BytesPayload(util.prepare_xls(cost_centers))
    payload.set_content_disposition(
        'form-data', name='cost_centers_file', filename=file_name,
    )
    writer.append_payload(payload)

    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/cost_centers'.format(client_id),
        data=writer,
        headers=writer.headers,
    )

    assert response.status == 200
    assert await response.json() == {}

    client = await db.corp_clients.find_one({'_id': client_id})
    assert client['cost_centers']['content'] == expected_cost_centers
    assert client['cost_centers']['file_name'] == file_name


RESTRICTIONS_BASE_TEST = dict(
    method='POST',
    mongo_init='db/default_only.json',
    mongo_result='db/default_only.json',
    request='requests/default_to_change.json',
    expected_status=400,
    client_id='some_client_id',
    uuids=['some_custom_field_uuid_id', 'another_field_uuid_id'],
)

RESTRICTIONS_TEST_CASES = [
    #   - если прислать настройки с default: true, и лишним полем
    #       то вернуть ошибку 400
    pytest.param(
        dict(
            RESTRICTIONS_BASE_TEST,
            request_updater=util.add_extra_field,
            response='error:too_many_fields',
            uuids=[],
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, total_fields_max_count=2,
            ),
        ),
        id='error-update-default-true-too-many-fields',
    ),
    #   - если прислать настройки с default: true, и лишним полем
    #       то вернуть ошибку 400
    pytest.param(
        dict(
            RESTRICTIONS_BASE_TEST,
            request_updater=util.add_extra_field_hidden,
            response='error:too_many_active_fields',
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS,
                total_fields_max_count=4,
                active_fields_max_count=2,
            ),
        ),
        id='error-update-default-true-too-many-active-fields',
    ),
    #   - если прислать настройки с default: true, и мало полей
    #       то вернуть ошибку 400
    pytest.param(
        dict(RESTRICTIONS_BASE_TEST, response='error:too_few_fields'),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, total_fields_min_count=5,
            ),
        ),
        id='error-update-default-true-too-few-fields',
    ),
    #   - если прислать настройки с default: true, и мало активных полей
    #       то вернуть ошибку 400
    pytest.param(
        dict(
            RESTRICTIONS_BASE_TEST,
            request_updater=util.add_extra_field_hidden,
            response='error:too_few_active_fields',
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS,
                total_fields_min_count=4,
                active_fields_min_count=4,
            ),
        ),
        id='error-update-default-true-too-few-active-fields',
    ),
    #   - если прислать настройки с default: true и длинным заголовком поля
    #       то вернуть ошибку 400
    pytest.param(
        dict(
            method='POST',
            mongo_init='db/default_only.json',
            mongo_result='db/default_only.json',
            request='requests/default_to_change.json',
            response='error:too_long_field_title',
            expected_status=400,
            client_id='some_client_id',
            uuids=['some_custom_field_uuid_id'],
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, field_title_max_length=10,
            ),
        ),
        id='error-update-default-true-too-long-field-title',
    ),
    #   - если прислать настройки с default: true и длинным названием ЦЗ
    #       то вернуть ошибку 400
    pytest.param(
        dict(
            method='POST',
            mongo_init='db/default_only.json',
            mongo_result='db/default_only.json',
            request='requests/default_to_change.json',
            response='error:too_long_value',
            response_param='18',
            expected_status=400,
            client_id='some_client_id',
            uuids=['some_custom_field_uuid_id'],
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, field_value_max_length=2,
            ),
        ),
        id='error-update-default-true-too-long-value',
    ),
    #   - если прислать настройки с default: true и коротким заголовком поля
    #       то вернуть ошибку 400
    pytest.param(
        dict(
            method='POST',
            mongo_init='db/default_only.json',
            mongo_result='db/default_only.json',
            request='requests/default_to_change.json',
            response='error:too_short_field_title',
            expected_status=400,
            client_id='some_client_id',
            uuids=['some_custom_field_uuid_id'],
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, field_title_min_length=15,
            ),
        ),
        id='error-update-default-true-too-short-field-title',
    ),
    #   - если прислать настройки с default: true и длинным списком значений
    #       то вернуть ошибку 400
    pytest.param(
        dict(RESTRICTIONS_BASE_TEST, response='error:too_many_field_values'),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, field_values_max_count=2,
            ),
        ),
        id='error-update-default-true-too-many-field-values',
    ),
    #   - если прислать настройки с default: true и коротким списком значений
    #       то вернуть ошибку 400
    pytest.param(
        dict(RESTRICTIONS_BASE_TEST, response='error:too_few_field_values'),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, field_values_min_count=4,
            ),
        ),
        id='error-update-default-true-too-few-field-values',
    ),
    #   - если прислать настройки без id при ограничении числа настроек
    #       то вернуть 400
    pytest.param(
        dict(
            method='POST',
            mongo_init='db/default_and_other.json',
            mongo_result='db/default_and_other.json',
            request='requests/not_default.json',
            request_updater=util.change_option_name,
            response='error:too_many_options',
            expected_status=400,
            client_id='some_client_id',
            uuids=[],
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, cost_centers_max_count=2,
            ),
        ),
        id='error-create-not-default-too-many-options',
    ),
    pytest.param(
        dict(
            method='POST',
            mongo_init='db/default_and_other.json',
            mongo_result='db/default_and_other.json',
            request='requests/not_default_to_change.json',
            response='error:too_long_value',
            response_param='21',
            expected_status=400,
            client_id='some_client_id',
            uuids=['yet_another_field_uuid_id', 'yet_hidden_field_id'],
        ),
        marks=pytest.mark.config(
            CORP_COST_CENTERS_RESTRICTIONS=dict(
                util.COST_CENTERS_RESTRICTIONS, field_value_max_length=2,
            ),
        ),
        id='update-not-default',
    ),
]


@pytest.mark.translations(corp=util.CORP_TRANSLATIONS)
@pytest.mark.parametrize(
    'case_dict',
    [
        # кейсы для POST:
        # 1) изначально для клиента нет никаких настроек:
        #   - если прислать настройки с default: true
        #       то вернуть ошибку 400 (т.к. id клиента нет в конфиге)
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/empty.json',
                request='requests/default.json',
                response='error:creation_not_allowed',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-default-true-not-in-config',
        ),
        #   - если прислать настройки с default: true
        #       то создать их (т.к. id клиента есть в конфиге)
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/default_created.json',
                request='requests/default.json',
                response='responses/created_default.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=['some_cc_options_id', 'custom_field_uuid_id'],
                check_history_item=-1,
                check_users_cc_id='some_cc_options_id',
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='create-default-true',
        ),
        #   - если прислать настройки с повотряющимися values
        #       то дубли значений удаляются
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/default_created.json',
                request='requests/default.json',
                request_updater=util.duplicate_field_values,
                response='responses/created_default.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=['some_cc_options_id', 'custom_field_uuid_id'],
                check_history_item=-1,
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='create-default-true-with-duplicated-values',
        ),
        #   - если прислать настройки с повторяющимися title
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/empty.json',
                request='requests/default_duplicate_titles.json',
                response='error:duplicate_titles',
                expected_status=400,
                uuids=[],
                client_id='some_client_id',
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='error-duplicate-titles',
        ),
        #   - если прислать настройки с повторяющимися id
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/empty.json',
                request='requests/default_duplicate_ids.json',
                response='error:duplicate_ids',
                expected_status=400,
                uuids=['some_unique_id'],
                client_id='some_client_id',
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='error-duplicate-ids',
        ),
        #   - если прислать настройки с пустым заголовком поля
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/empty.json',
                request='requests/default_empty_title.json',
                response='error:empty_title',
                expected_status=400,
                uuids=[],
                client_id='some_client_id',
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='error-empty-title',
        ),
        #   - если прислать настройки с пустым значением для выбора
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/empty.json',
                request='requests/default_empty_value.json',
                response='error:empty_value',
                expected_status=400,
                uuids=[],
                client_id='some_client_id',
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='error-empty-value',
        ),
        #   - если прислать настройки с default: false
        #       то создать их как основные (т.к. id клиента есть в конфиге)
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/other_as_default.json',
                request='requests/not_default.json',
                response='responses/created_other_default.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=['other_cc_options_id', 'other_field_uuid_id'],
                check_history_item=-1,
                check_users_cc_id='other_cc_options_id',
            ),
            marks=pytest.mark.config(
                CORP_COST_CENTERS_OLD_CLIENTS_ENABLED=['some_client_id'],
            ),
            id='create-default-from-false',
        ),
        #   - если прислать настройки с default: false
        #       то вернуть ошибку 400 (т.к. id клиента нет в конфиге)
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/empty.json',
                mongo_result='db/empty.json',
                request='requests/not_default.json',
                response='error:creation_not_allowed',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-default-from-false-not-in-config',
        ),
        # 2) у клиента уже есть дефолтные настройки:
        #   - если прислать настройки с default: true, с тем же id
        #       то обновить документ
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_changed.json',
                request='requests/default_to_change.json',
                response='responses/changed_default.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=['other_custom_field_uuid_id'],
                check_history_item=-1,
            ),
            id='update-default-true-same-id',
        ),
        #   - если прислать настройки с default: true, но другим id
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/default_other_id.json',
                response='error:default_exists',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='update-default-true-new-id',
        ),
        #   - если прислать настройки с default: true, но с удалённым полем
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/default_to_change.json',
                request_updater=util.remove_field,
                response='error:default_less_fields',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-update-default-with-less-fields',
        ),
        #   - если прислать настройки с default: true, поля поменяны местами
        #       то вернуть ошибку 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/default_to_change.json',
                request_updater=util.reorder_fields,
                response='error:default_no_reorder',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-update-default-with-reordered-fields',
        ),
        #   - если прислать настройки с default: false и без id
        #       то создать новый документ
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_and_other_created.json',
                request='requests/not_default.json',
                response='responses/created_not_default.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=['other_cc_options_id'],
                check_history_item=-1,
            ),
            id='create-not-default',
        ),
        #   - если прислать настройки с default: false и меньшим числом полей
        #       то вернуть 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/not_default.json',
                request_updater=util.remove_field,
                response='error:different_fields_count',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-not-default-less-fields',
        ),
        #   - если прислать настройки с default: false и большим числом полей
        #       то вернуть 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/not_default.json',
                request_updater=util.add_extra_field,
                response='error:different_fields_count',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-not-default-more-fields',
        ),
        #   - если прислать настройки с default: false и другим title поля
        #       то вернуть 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/not_default.json',
                request_updater=util.change_field_title,
                response='error:different_fields_title',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-not-default-different-titles',
        ),
        #   - если прислать настройки с default: false и другими сервисами поля
        #       то вернуть 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/not_default.json',
                request_updater=util.change_field_services,
                response='error:different_fields_services',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-not-default-different-services',
        ),
        #   - если прислать настройки без id с существующим названием
        #       то вернуть 400
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_and_other.json',
                mongo_result='db/default_and_other.json',
                request='requests/not_default.json',
                response='error:same_name',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='error-create-not-default-with-same-name',
        ),
        #   - аналогично предыдущему, но в запросе у поля id: ''
        #     в этом случае тоже ошибка
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/not_default_empty_field_id.json',
                response='error:different_fields_id',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='create-not-default-replaced-empty-field-id',
        ),
        #   - если прислать основные настройки с default: false
        #       то вернуть ошибку 400
        #       (нельзя оставлять клиента совсем без основных настроек)
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                request='requests/default_false_same_id.json',
                response='error:default_must_exist',
                expected_status=400,
                client_id='some_client_id',
                uuids=[],
            ),
            id='update-default-false-old-id',
        ),
        #   - если прислать настройки с default: false и существующим id
        #     (не основные настройки)
        #       то обновить документ
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_and_other.json',
                mongo_result='db/default_and_other_changed.json',
                request='requests/not_default_to_change.json',
                response='responses/changed_not_default.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=[],
                check_history_item=-1,
            ),
            id='update-not-default',
        ),
        #   - если прислать настройки с default: true и существующим id
        #     (основные настройки)
        #       то обновить основной набор,
        #       а также дополнительный (заголовки полей и сервисы)
        #       при этом значения, обязательность и прочее остаётся как было
        pytest.param(
            dict(
                method='POST',
                mongo_init='db/default_and_other.json',
                mongo_result='db/default_and_other_both_changed.json',
                request='requests/default_to_change_more.json',
                response='responses/changed_default_with_extra.json',
                expected_status=200,
                client_id='some_client_id',
                uuids=['yet_another_field_uuid_id'],
                check_history_item=0,  # check default only
            ),
            id='update-default-and-other-too',
        ),
        # TODO: проверить все кейсы при наличии документов для других клиентов
        #
        # кейсы для GET
        #
        pytest.param(
            dict(
                method='GET',
                mongo_init='db/default_only.json',
                mongo_result='db/default_only.json',
                response='responses/get_default_only.json',
                expected_status=200,
                client_id='some_client_id',
            ),
            marks=pytest.mark.filldb(corp_users='for_get'),
            id='get-for-existing-client-default-only',
        ),
        pytest.param(
            dict(
                method='GET',
                mongo_init='db/default_and_other.json',
                mongo_result='db/default_and_other.json',
                response='responses/get_default_and_other.json',
                expected_status=200,
                client_id='some_client_id',
            ),
            marks=pytest.mark.filldb(corp_users='for_get'),
            id='get-for-existing-client-default-and-other',
        ),
        pytest.param(
            dict(
                method='GET',
                mongo_init='db/default_and_other.json',
                mongo_result='db/default_and_other.json',
                response='responses/get_empty_list.json',
                expected_status=200,
                client_id='some_other_client_id',
            ),
            id='get-for-non-existing-client',
        ),
    ]
    + RESTRICTIONS_TEST_CASES,
)
@pytest.mark.now('2021-03-01T15:00:00+0300')
@pytest.mark.usefixtures('patch_current_date')
async def test_single_post_get(
        taxi_corp_auth_client, db, load_json, patch, case_dict,
):
    uuids = iter(case_dict.get('uuids', []))

    @patch('taxi_corp.api.common.cost_centers._uuid4')
    def _uuid4():
        try:
            return next(uuids)
        except StopIteration:
            return uuid.uuid4().hex

    # set up test data
    client_id = case_dict['client_id']
    mongo_init = load_json(case_dict['mongo_init'])
    expected_docs = load_json(case_dict['mongo_result'])
    response_key = case_dict['response']
    if response_key.startswith('error:'):
        expected_response = util.build_error(
            response_key[len('error:') :], case_dict.get('response_param'),
        )
    else:
        expected_response = load_json(response_key)
    users_query = {'client_id': client_id}

    # prepare database
    await db.corp_history.remove()
    await db.corp_cost_center_options.remove()
    if mongo_init:
        await db.corp_cost_center_options.insert(mongo_init)

    # check users before creating default cost center
    if 'check_users_cc_id' in case_dict:
        users = await db.corp_users.find(users_query).to_list(None)
        assert all('cost_centers_id' not in user for user in users)

    if case_dict['method'] == 'POST':
        request_data = load_json(case_dict['request'])
        request_updater = case_dict.get('request_updater')
        if request_updater is not None:
            request_updater(request_data)

        # make test
        response = await taxi_corp_auth_client.post(
            '/1.0/client/{}/cost_centers'.format(client_id), json=request_data,
        )
    elif case_dict['method'] == 'GET':
        # make test
        response = await taxi_corp_auth_client.get(
            '/1.0/client/{}/cost_centers'.format(client_id),
        )
    else:
        raise ValueError('wrong method in test params')

    assert response.status == case_dict['expected_status']
    response_data = await response.json()
    assert response_data == expected_response

    # check database
    cursor = db.corp_cost_center_options.find()
    result_docs = await cursor.to_list(None)

    assert result_docs == expected_docs

    history_doc = await db.corp_history.find_one()
    if case_dict.get('check_history_item') is None:
        assert history_doc is None
    else:
        assert history_doc is not None
        item_index = case_dict['check_history_item']
        assert history_doc['e'] == expected_docs[item_index]
        assert history_doc['c'] == 'corp_cost_center_options'
        assert history_doc['cl'] == client_id

    # check users after creating default cost center
    if 'check_users_cc_id' in case_dict:
        users = await db.corp_users.find(users_query).to_list(None)
        assert all(
            user['cost_centers_id'] == case_dict['check_users_cc_id']
            for user in users
        )


@pytest.mark.parametrize(
    ['client_id', 'expected_response'],
    [
        pytest.param(
            '7ff7900803534212a3a66f4d0e114fc2',
            {
                'items': [
                    {
                        'client_id': '7ff7900803534212a3a66f4d0e114fc2',
                        'default': True,
                        'field_settings': [
                            {
                                'format': 'text',
                                'hidden': False,
                                'id': 'cost_center',
                                'required': False,
                                'services': ['taxi'],
                                'title': 'Цель поездки',
                                'values': [],
                            },
                        ],
                        'name': 'Основной центр затрат',
                    },
                ],
            },
            id='default-config',
        ),
    ],
)
async def test_cost_center_templates(
        taxi_corp_auth_client, client_id, expected_response,
):
    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/cost_centers/templates'.format(client_id),
    )
    response_content = await response.json()
    assert response_content == expected_response


@pytest.mark.parametrize(
    [
        'client_id',
        'content',
        'content_name',
        'file_name',
        'expected_code',
        'expected_response',
    ],
    [
        (
            '79110cc5c5754ac787f80e7452dee5c8',
            'something',
            'something',
            'new_cost_centers.xls',
            400,
            {
                'errors': [
                    {
                        'code': 'XLS_FILE_CONTENT_IS_REQUIRED',
                        'text': 'Файл с кост-центрами отсутствует.',
                    },
                ],
                'message': 'Файл с кост-центрами отсутствует.',
                'code': 'XLS_FILE_CONTENT_IS_REQUIRED',
            },
        ),
        (
            '79110cc5c5754ac787f80e7452dee5c8',
            'invalid content',
            'cost_centers_file',
            'new_cost_centers.xls',
            400,
            {
                'errors': [
                    {
                        'code': 'UPLOADED_FILE_COULD_NOT_BE_PARSED_AS_XLS',
                        'text': (
                            'Загружаемый файл не удалось прочитать '
                            'в .xls формате.'
                        ),
                    },
                ],
                'message': (
                    'Загружаемый файл не удалось прочитать ' 'в .xls формате.'
                ),
                'code': 'UPLOADED_FILE_COULD_NOT_BE_PARSED_AS_XLS',
            },
        ),
    ],
)
@pytest.mark.translations(
    corp={
        'error.failed_to_parse_xls': {
            'ru': 'Загружаемый файл не удалось прочитать в .xls формате.',
        },
        'error.xls_is_absent': {'ru': 'Файл с кост-центрами отсутствует.'},
    },
)
async def test_single_put_fail(
        taxi_corp_auth_client,
        client_id,
        content,
        content_name,
        file_name,
        expected_code,
        expected_response,
):
    writer = aiohttp.MultipartWriter('form-data')
    payload = aiohttp.payload.StringPayload(content)
    payload.set_content_disposition(
        'form-data', name=content_name, filename=file_name,
    )
    writer.append_payload(payload)

    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/cost_centers'.format(client_id),
        data=writer,
        headers=writer.headers,
    )
    response_json = await response.json()
    assert response.status == expected_code, response_json
    assert response_json == expected_response


@pytest.mark.parametrize(
    ['client_id', 'cost_centers', 'file_name'],
    [
        (
            '7ff7900803534212a3a66f4d0e114fc2',
            ['foo', 'bar', 'FOO'],
            'cost_centers.xls',
        ),
    ],
)
async def test_single_updated_field_put(
        taxi_corp_auth_client, db, client_id, cost_centers, file_name,
):
    writer = aiohttp.MultipartWriter('form-data')
    payload = aiohttp.payload.BytesPayload(util.prepare_xls(cost_centers))
    payload.set_content_disposition(
        'form-data', name='cost_centers_file', filename=file_name,
    )
    writer.append_payload(payload)

    response = await taxi_corp_auth_client.put(
        '/1.0/client/{}/cost_centers'.format(client_id),
        data=writer,
        headers=writer.headers,
    )

    assert response.status == 200
    assert await response.json() == {}

    db_item = await db.corp_clients.find_one({'_id': client_id})
    assert 'updated' in db_item
    assert isinstance(db_item['updated'], datetime.datetime)

# pylint: disable=unused-variable
import pytest

from crm_admin.generated.service.swagger import models
from crm_admin.utils.validation import filters_yt_validators
from test_crm_admin.web import test_validators

PERMISSION_ALLOW = {'action': 'allow'}
PERMISSION_DENY = {'action': 'deny'}


@pytest.mark.parametrize(
    'file, id_, result',
    [
        ('filters_new.json', 6, 200),
        ('filters_empty.json', 1, 200),
        ('filters_new.json', 100, 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_retrieve_filters(web_app_client, load_json, file, id_, result):
    existing_filters = load_json(file)
    response = await web_app_client.get(
        '/v1/campaigns/filters', params={'id': id_},
    )
    assert response.status == result
    if response.status == 200:
        retrieved_filters = await response.json()
        assert existing_filters == retrieved_filters


@pytest.mark.parametrize(
    'file, id_, result, exists',
    [
        ('filters_updated.json', 100, 404, False),
        ('filters_updated.json', 1, 200, True),
        ('filters_empty.json', 6, 200, True),
        ('filters_updated.json', 7, 400, False),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_update_filters(
        web_app_client, load_json, is_filters_exist, file, id_, result, exists,
):
    updated_form = load_json(file)
    response = await web_app_client.put(
        '/v1/campaigns/filters',
        params={'id': id_},
        json=updated_form,
        headers={'X-Yandex-Login': 'test'},
    )
    assert response.status == result
    assert is_filters_exist(id_, updated_form) == exists


@pytest.mark.parametrize(
    'campaign_id, filters, schema, result, exists, permission, broken_data',
    [
        (
            6,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [],
            200,
            None,
            None,
            False,
        ),
        (
            8,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [],
            200,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [{'type_v3': {'item': 'int32'}, 'name': 'required_attr'}],
            200,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [{'type_v3': {'item': 'int32'}, 'name': 'required_attr'}],
            400,
            True,
            PERMISSION_DENY,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [{'type_v3': {'item': 'int32'}, 'name': 'required_attr'}],
            400,
            False,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [{'type_v3': {'item': 'int32'}, 'name': 'required_attr'}],
            400,
            False,
            PERMISSION_DENY,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'correct_name2'},
            ],
            200,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'incorrect name'},
            ],
            400,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr2'},
            ],
            400,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr2'},
            ],
            400,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr2'},
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr3'},
            ],
            200,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr'},
            ],
            200,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': 'int32', 'name': 'some_attr'},
                {'type_v3': 'int32', 'name': 'required_attr'},
            ],
            200,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr'},
                {'type_v3': {'item': 'boolean'}, 'name': 'some_attr'},
            ],
            400,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'string'}, 'name': 'required_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr'},
            ],
            400,
            True,
            PERMISSION_ALLOW,
            False,
        ),
        (
            1,
            [{'fieldId': 'field', 'value': 'value_1'}],
            [
                {'type_v3': {'item': 'int32'}, 'name': 'some_attr'},
                {'type_v3': {'item': 'int32'}, 'name': 'required_attr'},
            ],
            400,
            True,
            PERMISSION_ALLOW,
            True,
        ),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_campaigns.sql'])
async def test_filters_validation(
        web_app_client,
        patch,
        campaign_id,
        filters,
        schema,
        result,
        exists,
        permission,
        broken_data,
):
    _yt_client = 'crm_admin.generated.web.yt_wrapper.plugin.AsyncYTClient.'

    @patch(_yt_client + 'get')
    async def _get(*args, **kwargs):
        return schema

    @patch(_yt_client + 'exists')
    async def _exists(*args, **kwargs):
        return exists

    @patch(_yt_client + 'check_permission')
    async def _check_permission(*args, **kwargs):
        return permission

    @patch(_yt_client + 'read_table')
    async def _read_table(*args, **kwargs):
        if not broken_data:
            return []
        raise UnicodeDecodeError('utf-8', b'', 0, 1, 'reason')

    response = await web_app_client.put(
        '/v1/campaigns/filters',
        params={'id': campaign_id},
        json=filters,
        headers={'X-Yandex-Login': 'test'},
    )

    assert response.status == result


_FILTER_SCHEMA_FRAGMENT = [
    # table for elimination
    {
        'id': 'g_external_data_source',
        'type': 'group',
        'label': 'Внешний источник данных (YT, Сервис Тегов)',
    },
    {
        'id': 'g_table_for_elimination_url',
        'type': 'filter',
        'label': 'Исключить пользователей из таблицы на YT',
        'isMultiple': True,
        'groupId': 'g_external_data_source',
    },
    {
        'id': 'table_for_elimination_url',
        'type': 'string',
        'label': 'Исключить пользователей из таблицы на YT',
        'description': 'Some text',
        'required': True,  # should be skipped cause parent have isMultiple
        'groupId': 'g_table_for_elimination_url',
    },
    # taxi activity
    {
        'id': 'g_trips_and_tariffs',
        'type': 'group',
        'label': 'Поездки и заказы',
    },
    {
        'id': 'g_active_taxi',
        'type': 'filter',
        'label': 'Активность в Такси',
        'groupId': 'g_trips_and_tariffs',
    },
    {
        'id': 'active_taxi',
        'type': 'radio',
        'label': 'Поездки на такси',
        'groupId': 'g_active_taxi',
        'defaultValue': 'active',
        'required': True,  # should not be skipped
        'help': 'some text',
        'options': [{'label': 'Были поездки', 'value': 'active'}],
    },
    {
        'id': 'active_taxi_interval',
        'type': 'radio',
        'label': 'Период',
        'groupId': 'g_active_taxi',
        'required': True,  # should be skipped cause showIf is present
        'defaultValue': '12_weeks',
        'showIf': [
            {'fieldId': 'active_taxi', 'type': 'equals', 'value': 'inactive'},
            {'fieldId': 'active_taxi', 'type': 'equals', 'value': 'active'},
        ],
        'options': [{'label': '1 неделя', 'value': '1_week'}],
    },
    # communicated days
    {
        'id': 'g_regular',
        'type': 'group',
        'label': 'Регулярные',
        'campaign_type': 'regular',
    },
    {
        'id': 'g_communicated',
        'type': 'filter',
        'label': 'Не отправлять повторные коммуникации',
        'campaign_type': 'regular',
        'groupId': 'g_regular',
    },
    {
        'id': 'communicated_days',
        'type': 'number',
        'campaign_type': 'regular',
        'label': 'some text',
        'groupId': 'g_communicated',
        'maxValue': 10000,
        'minValue': 0,
        'required': True,  # should be skipped only for oneshot campaign
        'defaultValue': 90,
    },
]


@pytest.mark.config(
    CRM_ADMIN_SETTINGS={
        'ValidationSettings': {'communicated_days_limit': 100},
    },
)
@pytest.mark.parametrize(
    'is_regular, filter_values, filter_schemas, expected_result',
    [
        (
            False,
            [
                {'value': ['br_russia'], 'fieldId': 'country'},
                {'value': [], 'fieldId': 'city'},
                {'value': [], 'fieldId': 'city_exclude'},
                {'value': 'yandex', 'fieldId': 'brand'},
                {'value': 'off', 'fieldId': 'active_taxi'},
            ],
            _FILTER_SCHEMA_FRAGMENT,
            [],
        ),
        (
            False,
            [
                {'value': ['br_russia'], 'fieldId': 'country'},
                {'value': [], 'fieldId': 'city'},
                {'value': [], 'fieldId': 'city_exclude'},
                {'value': 'yandex', 'fieldId': 'brand'},
            ],
            _FILTER_SCHEMA_FRAGMENT,
            [
                {
                    'code': 'required_filter_missing',
                    'details': {
                        'field': 'active_taxi',
                        'value': 'Поездки на такси',
                    },
                },
            ],
        ),
        (
            True,
            [
                {'value': ['br_russia'], 'fieldId': 'country'},
                {'value': [], 'fieldId': 'city'},
                {'value': [], 'fieldId': 'city_exclude'},
                {'value': 'yandex', 'fieldId': 'brand'},
                {'value': 'off', 'fieldId': 'active_taxi'},
            ],
            _FILTER_SCHEMA_FRAGMENT,
            [
                {
                    'code': 'required_filter_missing',
                    'details': {
                        'field': 'communicated_days',
                        'value': 'some text',
                    },
                },
            ],
        ),
        (
            True,
            [
                {'value': ['br_russia'], 'fieldId': 'country'},
                {'value': [], 'fieldId': 'city'},
                {'value': [], 'fieldId': 'city_exclude'},
                {'value': 'yandex', 'fieldId': 'brand'},
                {'value': 'off', 'fieldId': 'active_taxi'},
                {'value': 223, 'fieldId': 'communicated_days'},
            ],
            _FILTER_SCHEMA_FRAGMENT,
            [
                {
                    'code': 'filter_value_error',
                    'details': {
                        'field_id': 'communicated_days',
                        'reason': (
                            'communicated_days can not be greater than 100'
                        ),
                    },
                },
            ],
        ),
    ],
)
async def test_required_filters(
        web_context,
        patch,
        is_regular,
        filter_values,
        filter_schemas,
        expected_result,
):
    @patch('crm_admin.utils.common.get_input_schema')
    async def schema_getter(*args, **kwargs):
        return filter_schemas

    @patch(
        'crm_admin.utils.validation.filters_yt_validators'
        '._validate_yt_table_filters',
    )
    async def table_validator(*args, **kwargs):
        return []

    campaign = test_validators.get_blank_campaign()
    campaign.is_regular = is_regular

    filter_values = [
        models.api.FilterFieldInfo.deserialize(data=value, allow_extra=True)
        for value in filter_values
    ]
    result = await filters_yt_validators.validate_filters_values(
        context=web_context, campaign=campaign, filter_values=filter_values,
    )
    result = [val.serialize_to_dict() for val in result]
    assert expected_result == result

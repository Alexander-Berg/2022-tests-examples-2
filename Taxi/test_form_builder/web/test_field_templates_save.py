import dataclasses
import json

import asyncpg
import pytest

from form_builder.utils import field_templates as fts


def _string(val: str):
    return {'type': 'string', 'stringValue': val}


def _choice(val, title):
    return {'value': val, 'title': {'static_value': title}}


def _remove_ro_fields(template: dict):
    return {
        k: v
        for k, v in template.items()
        if k not in ['can_be_filler', 'can_be_fillable']
    }


def _field_template(**kwargs):
    return {
        'id': 1,
        'name': 'test',
        'value_type': 'integer',
        'is_array': False,
        'has_choices': False,
        'tags': ['Select'],
        **kwargs,
    }


def _to_dict(record):
    if isinstance(record, asyncpg.Record):
        record = dict(record)
    if isinstance(record, dict):
        return {key: _to_dict(val) for key, val in record.items()}
    if isinstance(record, list):
        return [_to_dict(x) for x in record]
    if isinstance(record, str):
        try:
            return json.loads(record)
        except json.JSONDecodeError:
            return record
    return record


def _dt_to_dict(dataclass) -> dict:
    result = {
        key: val
        for key, val in dataclasses.asdict(dataclass).items()
        if val is not None
    }
    result['id'] = result.pop('field_template_id')
    return result


@pytest.mark.parametrize(
    'method,input_data,expected_code,expected_data',
    [
        ('PUT', _field_template(), 200, {}),
        (
            'PUT',
            _field_template(value_type=None, has_choices=True),
            400,
            {
                'code': 'CHOICES_ARE_NOT_ACCEPTABLE',
                'message': 'choices are not acceptable cause no value type',
            },
        ),
        (
            'PUT',
            _field_template(id=2),
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'field template with id "2" is not found',
            },
        ),
        (
            'PUT',
            _field_template(id=None),
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': 'field template id is required',
            },
        ),
        ('POST', _field_template(id=None), 200, {'id': 2}),
        (
            'PUT',
            _field_template(
                default_choices=[
                    {
                        'value': {'type': 'integer', 'integerValue': 1},
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            400,
            {
                'code': 'CHOICES_ARE_NOT_ACCEPTABLE',
                'message': 'choices are turned off for template "test"',
            },
        ),
        (
            'PUT',
            _field_template(
                has_choices=True,
                default_choices=[
                    {
                        'value': {'type': 'integer', 'integerValue': 1},
                        'title': {},
                    },
                ],
            ),
            400,
            {
                'code': 'BUILDER_ERROR',
                'message': 'tanker_key or static_value is required',
            },
        ),
        (
            'PUT',
            _field_template(
                has_choices=True,
                default_choices=[
                    {
                        'value': {'type': 'integer', 'integerValue': 1},
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            200,
            {},
        ),
        (
            'PUT',
            _field_template(
                has_choices=True,
                default_choices=[
                    {
                        'value': {'type': 'string', 'stringValue': 'x'},
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            400,
            {
                'code': 'CHOICE_VALUE_ERROR',
                'message': (
                    'choice value validation error: type "integer" expected, '
                    'not "string"'
                ),
            },
        ),
        ('PUT', _field_template(has_choices=True), 200, {}),
        (
            'PUT',
            _field_template(
                value_type='string',
                is_array=True,
                has_choices=True,
                default_choices=[
                    {
                        'value': {'type': 'string', 'stringValue': 'x'},
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            200,
            {},
        ),
        (
            'PUT',
            _field_template(
                value_type='string',
                is_array=True,
                has_choices=True,
                default_choices=[
                    {
                        'value': {
                            'type': 'array',
                            'arrayValue': [
                                {'type': 'integer', 'integerValue': 1},
                            ],
                        },
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            400,
            {
                'code': 'CHOICE_VALUE_ERROR',
                'message': (
                    'choice value validation error: type "string" expected, '
                    'not "array"'
                ),
            },
        ),
        (
            'PUT',
            _field_template(
                value_type='integer',
                is_array=True,
                has_choices=True,
                default_choices=[
                    {
                        'value': {
                            'type': 'array',
                            'arrayValue': [
                                {'type': 'integer', 'integerValue': 1},
                            ],
                        },
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            400,
            {
                'code': 'CHOICE_VALUE_ERROR',
                'message': (
                    'choice value validation error: type "integer" expected, '
                    'not "array"'
                ),
            },
        ),
        (
            'PUT',
            _field_template(
                value_type='string',
                is_array=False,
                has_choices=True,
                default_choices=[
                    {
                        'value': {
                            'type': 'array',
                            'arrayValue': [
                                {'type': 'integer', 'integerValue': 1},
                            ],
                        },
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            400,
            {
                'code': 'CHOICE_VALUE_ERROR',
                'message': (
                    'choice value validation error: type "string" expected, '
                    'not "array"'
                ),
            },
        ),
        (
            'PUT',
            _field_template(
                value_type='integer',
                is_array=True,
                has_choices=True,
                default_choices=[
                    {
                        'value': {
                            'type': 'array',
                            'arrayValue': [
                                {'type': 'integer', 'integerValue': 1},
                            ],
                        },
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            400,
            {
                'code': 'CHOICE_VALUE_ERROR',
                'message': (
                    'choice value validation error: '
                    'type "integer" expected, not "array"'
                ),
            },
        ),
        (
            'PUT',
            _field_template(value_type='string', regex_pattern=r'\d'),
            200,
            {},
        ),
        (
            'PUT',
            _field_template(
                value_type='number',
                has_choices=True,
                default_choices=[
                    {
                        'value': {'type': 'number', 'numberValue': 1},
                        'title': {'static_value': 'x'},
                    },
                ],
            ),
            200,
            {},
        ),
    ],
)
async def test_field_templates_save(
        taxi_form_builder_web,
        method,
        input_data,
        expected_code,
        expected_data,
        web_context,
):
    request_method = (
        taxi_form_builder_web.put
        if method == 'PUT'
        else taxi_form_builder_web.post
    )
    response = await request_method(
        '/v1/builder/field-templates/',
        json=input_data,
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == expected_code, await response.text()
    save_data = await response.json()
    if expected_data is not None:
        assert save_data == expected_data
    if expected_code != 200:
        return
    if method == 'PUT':
        field_template_id = input_data['id']
    else:
        field_template_id = save_data['id']
    response = await taxi_form_builder_web.get(
        '/v1/builder/field-templates/list/',
    )
    assert response.status == 200
    field_templates = (await response.json())['field_templates']
    field_templates_by_id = {
        field_template['id']: field_template
        for field_template in field_templates
    }
    get_data = field_templates_by_id[field_template_id]
    input_data.pop('id')
    get_data.pop('id')
    assert input_data == _remove_ro_fields(get_data)
    count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.field_templates;',
    )
    if field_template_id != 1:
        # field_template_1 is already in db
        extra_count = 1
    else:
        extra_count = 0
    assert count == 1 + extra_count


@pytest.mark.parametrize(
    'method, expected_data', [('PUT', {}), ('POST', {'id': 2})],
)
async def test_check_translatable_for_form_templates(
        taxi_form_builder_web, web_context, method, expected_data,
):
    request_method = (
        taxi_form_builder_web.put
        if method == 'PUT'
        else taxi_form_builder_web.post
    )
    input_data = _field_template(
        has_choices=True,
        default_choices=[
            {
                'value': {'type': 'integer', 'integerValue': 1},
                'title': {'static_value': 'x', 'tanker_key': 'some_key'},
            },
        ],
        default_hint={'static_value': 'email', 'tanker_key': 'some_key'},
        default_placeholder={
            'static_value': 'email',
            'tanker_key': 'some_key',
        },
        default_label={'static_value': 'email', 'tanker_key': 'some_key'},
    )
    response = await request_method(
        '/v1/builder/field-templates/',
        json=input_data,
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == 200
    save_data = await response.json()
    assert save_data == expected_data
    field_template = await web_context.pg.primary.fetchrow(
        'SELECT name, value_type, is_array, has_choices, '
        'tags, default_choices, default_label, default_hint, '
        'default_placeholder '
        'FROM form_builder.field_templates WHERE id = $1;',
        save_data.get('id', 1),
    )
    input_data.pop('id')
    assert _to_dict(field_template) == input_data


@pytest.mark.parametrize(
    'method, template, expected',
    [
        ('POST', _field_template(), _field_template(id=2)),
        ('PUT', _field_template(), _field_template()),
        (
            'POST',
            _field_template(default_label={'static_value': ''}),
            _field_template(id=2),
        ),
        (
            'PUT',
            _field_template(default_label={'static_value': ''}),
            _field_template(),
        ),
        (
            'POST',
            _field_template(default_placeholder={'static_value': ''}),
            _field_template(id=2),
        ),
        (
            'PUT',
            _field_template(default_placeholder={'static_value': ''}),
            _field_template(),
        ),
        (
            'POST',
            _field_template(default_hint={'static_value': ''}),
            _field_template(id=2),
        ),
        (
            'PUT',
            _field_template(default_hint={'static_value': ''}),
            _field_template(),
        ),
    ],
)
async def test_do_not_save_empty(
        taxi_form_builder_web, web_context, method, template, expected,
):
    request_method = (
        taxi_form_builder_web.put
        if method == 'PUT'
        else taxi_form_builder_web.post
    )
    response = await request_method(
        '/v1/builder/field-templates/',
        json=template,
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == 200, await response.text()

    _templates = await fts.FieldTemplate.fetch(
        author='nevladov',
        less_than_id=None,
        limit=10,
        conn=web_context.pg.primary,
        context=web_context,
    )
    _templates_by_id = {x.primary_key: x for x in _templates}
    assert _dt_to_dict(_templates_by_id[expected['id']]) == expected

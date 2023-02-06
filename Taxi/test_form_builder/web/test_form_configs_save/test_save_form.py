import pytest

from test_form_builder.web.test_form_configs_save import _utils


@pytest.mark.parametrize(
    'method,input_data,expected_code,expected_data',
    [
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(),
                    submit_options=_utils.stage_submit_options(
                        'url',
                        'POST',
                        (
                            '{"driver_email": {{ driver_email }}, '
                            '"submit_id": {{ submit_id }} }'
                        ),
                        '123',
                    ),
                ),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field()),
                submit_options_=[_utils.submit_options(headers=[])],
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(code=None, template_id=4))),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(template_id=4))),
            400,
            {
                'code': 'VALUE_TYPE_IS_REQUIRED',
                'message': (
                    'field "driver_email" has no value type '
                    'for template "Caption"'
                ),
            },
        ),
        (
            'PUT',
            _utils.form(_utils.stage(_utils.field()), code='form_1'),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field()), code='form_1'),
            409,
            {
                'code': 'CONFLICT_ERROR',
                'message': 'form with code "form_1" already exists',
            },
        ),
        (
            'PUT',
            _utils.form(_utils.stage(_utils.field()), code='form_3'),
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'form with code "form_3" is not found',
            },
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(template_id=0))),
            400,
            {
                'code': 'UNKNOWN_TEMPLATE_ID',
                'message': 'unknown template id "0"',
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        choices=[
                            {
                                'title': _utils.translation(),
                                'value': {
                                    'type': 'integer',
                                    'integerValue': 1,
                                },
                            },
                        ],
                    ),
                ),
            ),
            400,
            {
                'code': 'CHOICES_ARE_NOT_ACCEPTABLE',
                'message': 'choices are turned off for template "email"',
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(template_id=3, label=_utils.translation()),
                ),
            ),
            400,
            {
                'code': 'CHOICES_ARE_REQUIRED',
                'message': (
                    'neither field "driver_email" nor its template has '
                    'choices but they are required for template '
                    '"1-3_no_choices"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        template_id=3,
                        choices=[
                            {
                                'title': _utils.translation(),
                                'value': {
                                    'type': 'integer',
                                    'integerValue': 1,
                                },
                            },
                        ],
                    ),
                ),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        template_id=3,
                        choices=[
                            {
                                'title': _utils.translation(),
                                'value': {
                                    'type': 'string',
                                    'stringValue': '1',
                                },
                            },
                        ],
                    ),
                ),
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
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        template_id=3,
                        choices=[
                            {
                                'title': _utils.translation(),
                                'value': {
                                    'type': 'integer',
                                    'integerValue': 1,
                                },
                            },
                        ],
                        label=None,
                    ),
                ),
            ),
            400,
            {
                'code': 'FIELD_LABEL_IS_REQUIRED',
                'message': (
                    'neither field "driver_email" nor its template has label'
                ),
            },
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(), _utils.field())),
            400,
            {
                'code': 'FIELD_CODE_IS_DUPLICATED',
                'message': 'field code "driver_email" is duplicated',
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(), _utils.field(code='park_email')),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(), _utils.field(code='park_email')),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(), _utils.field(code='some_email')),
                _utils.stage(_utils.field(code='park_email')),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(), _utils.field(code='some_email')),
                _utils.stage(_utils.field(code='some_email')),
            ),
            400,
            {
                'code': 'FIELD_CODE_IS_DUPLICATED',
                'message': 'field code "some_email" is duplicated',
            },
        ),
        (
            'POST',
            _utils.form(_utils.stage()),
            400,
            {
                'code': 'FIELD_LIST_IS_EMPTY',
                'message': 'some stage has no fields',
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        default={'type': 'integer', 'integerValue': 1},
                    ),
                ),
            ),
            400,
            {
                'code': 'DEFAULT_VALUE_IS_REDUNDANT',
                'message': (
                    'default value of field "driver_email" is redundant cause '
                    'field is obligatory'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        obligatory=False,
                        default={'type': 'string', 'stringValue': 'x'},
                    ),
                ),
            ),
            400,
            {
                'code': 'DEFAULT_VALUE_IS_NOT_ACCEPTABLE',
                'message': (
                    'default value of field "driver_email" is not acceptable: '
                    'value "x" does not match regular expression "^\\S+@\\S+$"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        template_id=2,
                        obligatory=False,
                        default={'type': 'integer', 'integerValue': 1},
                    ),
                ),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        code='1-3_field',
                        template_id=2,
                        obligatory=False,
                        default={'type': 'integer', 'integerValue': 4},
                    ),
                ),
            ),
            400,
            {
                'code': 'DEFAULT_VALUE_IS_NOT_ACCEPTABLE',
                'message': (
                    'default value of field "1-3_field" is not acceptable: '
                    'value "4" is not corresponding to any choice'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(label=_utils.translation(tanker_key='x.y')),
                ),
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(label=_utils.translation(tanker_key='x.z')),
                ),
                supported_locales=['en', 'ge'],
            ),
            400,
            {
                'code': 'TRANSLATION_ERROR',
                'message': (
                    'no translation for tanker key "x.z" for locale "ru"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(label=_utils.translation(tanker_key='x.z')),
                ),
                default_locale='ge',
                supported_locales=['en', 'ge'],
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(label=_utils.translation(tanker_key='x.z')),
                ),
                default_locale='ge',
                supported_locales=['en', 'ge', 'de'],
            ),
            400,
            {
                'code': 'TRANSLATION_ERROR',
                'message': (
                    'no translation for tanker key "x.z" for locale "de"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(obligation_condition='cond_1')),
            ),
            400,
            {
                'code': 'UNKNOWN_CONDITION',
                'message': (
                    'unknown condition code "cond_1" of field "driver_email"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(obligation_condition='cond_1')),
                conditions={
                    'cond_1': {
                        'driver_email': {
                            '$in': [{'type': 'integer', 'integerValue': 1}],
                        },
                    },
                },
            ),
            400,
            {
                'code': 'PREDICATE_ARGUMENT_ERROR',
                'message': (
                    'argument validation error for predicate "$in": type '
                    '"string" expected, not "integer"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        code='1-3_field',
                        template_id=2,
                        obligation_condition='cond_1',
                    ),
                ),
                conditions={
                    'cond_1': {
                        '1-3_field': {
                            '$in': [{'type': 'integer', 'integerValue': 4}],
                        },
                    },
                },
            ),
            400,
            {
                'code': 'PREDICATE_ARGUMENT_ERROR',
                'message': (
                    'argument validation error for predicate "$in": value "4" '
                    'is not corresponding to any choice'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(
                        code='1-3_field',
                        template_id=2,
                        obligation_condition='cond_1',
                        choices=[
                            {
                                'title': _utils.translation(),
                                'value': {
                                    'type': 'integer',
                                    'integerValue': 4,
                                },
                            },
                        ],
                    ),
                ),
                conditions={
                    'cond_1': {
                        '1-3_field': {
                            '$in': [{'type': 'integer', 'integerValue': 4}],
                        },
                    },
                },
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field()),
                submit_options_=[
                    _utils.submit_options(body_template='test{{'),
                ],
            ),
            400,
            {
                'code': 'BODY_TEMPLATE_SYNTAX_ERROR',
                'message': 'unexpected \'end of template\'',
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(code='field_1'), _utils.field(code='field_2'),
                ),
                submit_options_=[
                    _utils.submit_options(
                        body_template=(
                            'test {{ field_1 }} {{ field_3 }} {{ field_4 }}'
                        ),
                    ),
                ],
            ),
            400,
            {
                'code': 'UNKNOWN_FIELD_CODES',
                'message': (
                    'body template contains unknown field codes: "field_3", '
                    '"field_4"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(template_id=3, label=None))),
            400,
            {
                'code': 'FIELD_LABEL_IS_REQUIRED',
                'message': (
                    'neither field "driver_email" nor its template has label'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(), title=_utils.translation(static_value=''),
                ),
            ),
            400,
            {
                'code': 'BUILDER_ERROR',
                'message': 'tanker_key or static_value is required',
            },
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(template_id=5))),
            400,
            {
                'code': 'FILES_NOT_SUPPORTED',
                'message': (
                    'receiver is not marked as multipart, cant accept files'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field(template_id=5)),
                submit_options_=[_utils.submit_options(is_multipart=True)],
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field()), ya_metric_counter=123),
            200,
            {},
        ),
        (
            'PUT',
            _utils.simple_form(
                _utils.field(
                    external_source=_utils.external_source(
                        external_suggest='dadata_suggests',
                        inline_from='data.name.short_with_opf',
                    ),
                ),
                code='form_1',
            ),
            200,
            {},
        ),
        (
            'PUT',
            _utils.simple_form(
                _utils.field(
                    async_validator={
                        'async_validator_code': 'sms_validator',
                        'validate_for': 'driver_email',
                    },
                ),
                code='form_1',
            ),
            400,
            {
                'code': 'WRONG_PD_TYPE',
                'message': (
                    'validator sms_validator expects phones pd type, '
                    'but field has emails'
                ),
            },
        ),
        (
            'PUT',
            _utils.simple_form(
                _utils.field(
                    code='driver_phone',
                    template_id=7,
                    async_validator={
                        'async_validator_code': 'sms_validator',
                        'validate_for': 'driver_phone',
                    },
                ),
                code='form_1',
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field()),
                submit_options_=[
                    _utils.submit_options(
                        body_template='{"submit_id": {{ submit_id }}}',
                    ),
                ],
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(_utils.stage(_utils.field(code='submit_id'))),
            400,
            {
                'code': 'RESERVED_FIELD_NAMES_USED',
                'message': 'used reserved field names: submit_id',
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field()),
                submit_options_=[
                    _utils.submit_options(
                        headers=[{'name': 'test', 'value': '{{ submit_id }}'}],
                    ),
                ],
            ),
            200,
            {},
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(_utils.field()),
                submit_options_=[
                    _utils.submit_options(
                        headers=[
                            {'name': 'test', 'value': '{{ unknown_field }}'},
                        ],
                    ),
                ],
            ),
            400,
            {
                'code': 'UNKNOWN_FIELD_CODES',
                'message': (
                    'header \'test\' template contains unknown field codes: '
                    '"unknown_field"'
                ),
            },
        ),
        (
            'POST',
            _utils.form(
                _utils.stage(
                    _utils.field(),
                    submit_options=_utils.stage_submit_options(
                        'url',
                        'POST',
                        None,
                        headers=[
                            {'name': 'test', 'value': '{{ unknown_field }}'},
                        ],
                    ),
                ),
            ),
            400,
            {
                'code': 'UNKNOWN_FIELD_CODES',
                'message': (
                    'header \'test\' template contains unknown field codes: '
                    '"unknown_field"'
                ),
            },
        ),
    ],
)
@_utils.TRANSLATIONS
async def test_forms_configs_save(
        web_app_client,
        method,
        input_data,
        expected_code,
        expected_data,
        web_context,
):
    request_method = (
        web_app_client.put if method == 'PUT' else web_app_client.post
    )
    response = await request_method(
        '/v1/builder/form-configs/',
        json=input_data,
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == expected_code, await response.text()
    put_data = await response.json()
    if expected_data is not None:
        assert put_data == expected_data
    if expected_code != 200:
        return
    response = await web_app_client.get(
        '/v1/builder/form-configs/',
        params={'code': input_data['form']['code']},
    )
    assert response.status == 200
    get_data = await response.json()
    assert _utils.remove_ro_fields(get_data['form']) == input_data['form']
    assert get_data['submit_options'] == input_data['submit_options']

    form_count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.forms;',
    )
    stage_count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.stages;',
    )
    field_count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.fields;',
    )
    if input_data['form']['code'] != 'form_1':
        # form_1 with 1 stage, 1 field is already in db
        extra_form_count = extra_stage_count = extra_field_count = 1
    else:
        extra_form_count = extra_stage_count = extra_field_count = 0
    assert form_count == 1 + extra_form_count
    stages = input_data['form']['stages']
    assert stage_count == len(stages) + extra_stage_count
    assert (
        field_count
        == sum(len(stage['fields']) for stage in stages) + extra_field_count
    )

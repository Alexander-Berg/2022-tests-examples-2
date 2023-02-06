import pytest

from test_form_builder.web.test_form_configs_save import _utils


@pytest.mark.parametrize(
    'input_data, expected_code, expected_data',
    [
        (
            _utils.simple_form(
                _utils.field(
                    external_source=_utils.external_source(
                        external_suggest='dadata_suggests',
                        inline_from='data.name.short_with_opf',
                    ),
                ),
            ),
            200,
            {},
        ),
        (
            _utils.simple_form(
                _utils.field(
                    external_source=_utils.external_source(
                        external_suggest='unknown',
                        inline_from='data.name.short_with_opf',
                    ),
                ),
            ),
            400,
            {
                'code': 'EXTERNAL_SUGGEST_CONFLICT',
                'message': 'unknown external source "unknown"',
            },
        ),
        (
            _utils.simple_form(
                _utils.field(
                    code='source',
                    external_source=_utils.external_source(
                        external_suggest='dadata_suggests',
                        inline_from='data.name.short_with_opf',
                    ),
                ),
                _utils.field(
                    code='receiver',
                    external_source=_utils.external_source(
                        suggest_from='source',
                        inline_from='data.name.short_with_opf',
                    ),
                ),
            ),
            200,
            {},
        ),
        (
            _utils.simple_form(
                _utils.field(
                    code='source',
                    external_source=_utils.external_source(
                        external_suggest='dadata_suggests',
                        inline_from='data.name.short_with_opf',
                    ),
                ),
                _utils.field(
                    code='receiver',
                    external_source=_utils.external_source(
                        suggest_from='source', inline_from='non.exists',
                    ),
                ),
            ),
            400,
            {
                'code': 'EXTERNAL_SUGGEST_CONFLICT',
                'message': 'invalid path "non.exists"',
            },
        ),
        (
            _utils.simple_form(
                _utils.field(code='country_id_filter', template_id=2),
                _utils.field(
                    code='field_geo_name',
                    external_source=_utils.external_source(
                        external_suggest='geo_suggests_city',
                        inline_from='name',
                        extra_kwargs_from={'country_ids': 'country_id_filter'},
                    ),
                ),
            ),
            200,
            {},
        ),
        (
            _utils.simple_form(
                _utils.field(code='country_ids_filter', template_id=6),
                _utils.field(
                    code='field_geo_name',
                    external_source=_utils.external_source(
                        external_suggest='geo_suggests_city',
                        inline_from='name',
                        extra_kwargs_from={
                            'country_ids': 'country_ids_filter',
                        },
                    ),
                ),
            ),
            200,
            {},
        ),
        pytest.param(
            _utils.simple_form(
                _utils.field(
                    code='some_field',
                    external_source=_utils.external_source(
                        external_suggest='', suggest_from='', inline_from='',
                    ),
                ),
            ),
            200,
            {},
            id='bad_front_payload',
        ),
    ],
)
async def test_save_form_with_external(
        web_context,
        taxi_form_builder_web,
        input_data,
        expected_code,
        expected_data,
):
    response = await taxi_form_builder_web.post(
        '/v1/builder/form-configs/',
        json=input_data,
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == expected_code, await response.text()
    put_data = await response.json()
    if expected_data is not None:
        assert put_data == expected_data
    if expected_code != 200:
        return
    response = await taxi_form_builder_web.get(
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

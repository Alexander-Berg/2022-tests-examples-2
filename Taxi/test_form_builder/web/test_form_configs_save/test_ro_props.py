from test_form_builder.web.test_form_configs_save import _utils


async def test_ro_props(taxi_form_builder_web):
    response = await taxi_form_builder_web.post(
        '/v1/builder/form-configs/',
        json=_utils.form(
            _utils.stage(
                _utils.field(template_id=1, code='simple_field'),
                _utils.field(template_id=2, code='field_with_choices'),
                _utils.field(template_id=5, code='file_field'),
                _utils.field(template_id=6, code='integer_array_field'),
                _utils.field(template_id=4, code=None),
            ),
            submit_options_=[_utils.submit_options(is_multipart=True)],
        ),
        headers={'X-Yandex-Login': 'd1mbas'},
    )
    assert response.status == 200, await response.text()

    response = await taxi_form_builder_web.get(
        '/v1/builder/form-configs/', params={'code': 'form_2'},
    )
    assert response.status == 200, await response.text()
    data = await response.json()
    assert data['form']['stages'][0]['fields'] == [
        _utils.conf_field(1, 'simple_field', True, True),
        _utils.conf_field(2, 'field_with_choices', True, True),
        _utils.conf_field(5, 'file_field', False, False),
        _utils.conf_field(6, 'integer_array_field', True, False),
        _utils.conf_field(4, None, False, False),
    ]

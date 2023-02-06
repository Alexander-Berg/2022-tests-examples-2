import pytest

from test_form_builder.web.test_form_configs_save import _utils


@pytest.mark.parametrize(
    'method, input_data, expected_data',
    [
        ('POST', _utils.form(_utils.stage(_utils.field(label=None))), {}),
        (
            'PUT',
            _utils.form(_utils.stage(_utils.field(label=None)), code='form_1'),
            {},
        ),
    ],
)
@_utils.TRANSLATIONS
async def test_saving_optional_field_props(
        taxi_form_builder_web, method, input_data, expected_data,
):
    # save form
    request_method = (
        taxi_form_builder_web.put
        if method == 'PUT'
        else taxi_form_builder_web.post
    )
    response = await request_method(
        '/v1/builder/form-configs/',
        json=input_data,
        headers={'X-Yandex-Login': 'nevladov'},
    )
    assert response.status == 200
    put_data = await response.json()
    assert put_data == expected_data

    # check saved
    response = await taxi_form_builder_web.get(
        '/v1/builder/form-configs/',
        params={'code': input_data['form']['code']},
    )
    assert response.status == 200
    get_data = await response.json()
    assert _utils.remove_ro_fields(get_data['form']) == input_data['form']
    assert get_data['submit_options'] == input_data['submit_options']

    # check saved for view
    response = await taxi_form_builder_web.get(
        '/v1/view/forms/', params={'code': input_data['form']['code']},
    )
    assert response.status == 200
    data = await response.json()
    assert data['form'] == {
        'code': input_data['form']['code'],
        'conditions': {},
        'stages': [
            {
                'fields': [
                    {
                        'template_id': 1,
                        'obligatory': True,
                        'visible': True,
                        'code': 'driver_email',
                        'can_be_filler': True,
                        'can_be_fillable': True,
                    },
                ],
                'title': {'translation': 'x'},
                'description': {'translation': 'x'},
            },
        ],
        'title': {'translation': 'x'},
        'description': {'translation': 'x'},
        'default_locale': 'ru',
        'supported_locales': ['ru', 'en'],
        'ya_metric_counter': 62138506,
    }
    field_template = {
        'is_array': False,
        'has_choices': False,
        'tags': [],
        'id': 1,
        'value_type': 'string',
        'personal_data_type': 'emails',
        'default_label': {'translation': 'e-mail'},
        'regex_pattern': r'^\S+@\S+$',
        'can_be_fillable': True,
        'can_be_filler': True,
    }
    assert data['field_templates'] == [field_template]

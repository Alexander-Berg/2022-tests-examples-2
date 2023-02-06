import pytest


FIELD_TEMPLATE_1 = {
    'id': 100,
    'name': 'field_template_1',
    'value_type': 'string',
    'is_array': False,
    'has_choices': False,
    'tags': [],
    'personal_data_type': 'emails',
    'default_label': {'tanker_key': '', 'static_value': 'e-mail'},
    'regex_pattern': r'^\S+@\S+$',
    'can_be_fillable': True,
    'can_be_filler': True,
}

FIELD_TEMPLATE_2 = {
    'id': 101,
    'name': 'field_template_2',
    'value_type': 'string',
    'is_array': False,
    'has_choices': False,
    'tags': [],
    'personal_data_type': 'emails',
    'default_label': {'tanker_key': '', 'static_value': 'e-mail'},
    'regex_pattern': r'^\S+@\S+$',
    'can_be_fillable': True,
    'can_be_filler': True,
}


@pytest.mark.parametrize(
    'params,expected_data',
    [
        (
            {},
            {
                'field_templates': [FIELD_TEMPLATE_2, FIELD_TEMPLATE_1],
                'min_id': 100,
            },
        ),
        ({'author': ''}, {'field_templates': []}),
        (
            {'author': 'author_1'},
            {'field_templates': [FIELD_TEMPLATE_1], 'min_id': 100},
        ),
        ({'limit': 1}, {'field_templates': [FIELD_TEMPLATE_2], 'min_id': 101}),
        (
            {'less_than_id': 101},
            {'field_templates': [FIELD_TEMPLATE_1], 'min_id': 100},
        ),
    ],
)
async def test_field_templates_list(
        taxi_form_builder_web, params, expected_data,
):
    response = await taxi_form_builder_web.get(
        '/v1/builder/field-templates/list/', params=params,
    )
    assert response.status == 200
    data = await response.json()
    if expected_data is not None:
        assert data == expected_data

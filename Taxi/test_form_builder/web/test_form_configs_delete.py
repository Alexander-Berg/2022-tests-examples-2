import pytest


@pytest.mark.parametrize(
    'form_code,expected_code,expected_data',
    [
        ('form_1', 200, {}),
        (
            'form_3',
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'form with code "form_3" is not found',
            },
        ),
        (
            'form_2',
            409,
            {
                'code': 'CONFLICT_ERROR',
                'message': (
                    'unable to delete form cause linked responses exist'
                ),
            },
        ),
    ],
)
async def test_forms_configs_delete(
        taxi_form_builder_web,
        form_code,
        expected_code,
        expected_data,
        web_context,
):
    response = await taxi_form_builder_web.delete(
        '/v1/builder/form-configs/', params={'code': form_code},
    )
    assert response.status == expected_code
    delete_data = await response.json()
    if expected_data is not None:
        assert delete_data == expected_data
    if expected_code != 200:
        return
    form_count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.forms;',
    )
    stage_count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.stages;',
    )
    field_count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.fields;',
    )
    assert form_count == 1
    assert stage_count == 0
    assert field_count == 0

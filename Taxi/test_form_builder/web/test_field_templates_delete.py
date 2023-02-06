import pytest


@pytest.mark.parametrize(
    'field_template_id,expected_code,expected_data',
    [
        (1, 200, {}),
        (
            3,
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'field template with id "3" is not found',
            },
        ),
        (
            2,
            409,
            {
                'code': 'CONFLICT_ERROR',
                'message': (
                    'unable to delete field template cause linked fields exist'
                ),
            },
        ),
    ],
)
async def test_field_templates_delete(
        taxi_form_builder_web,
        field_template_id,
        expected_code,
        expected_data,
        web_context,
):
    response = await taxi_form_builder_web.delete(
        '/v1/builder/field-templates/', params={'id': field_template_id},
    )
    assert response.status == expected_code
    delete_data = await response.json()
    if expected_data is not None:
        assert delete_data == expected_data
    if expected_code != 200:
        return
    count = await web_context.pg.primary.fetchval(
        'SELECT count(*) FROM form_builder.field_templates;',
    )
    assert count == 1

import pytest


DEFAULT_JSON_SCHEMA = {
    'title': 'Новый драфт создания серии',
    'type': 'object',
    'required': ['series_id', 'value', 'start', 'finish'],
    'properties': {
        'series_id': {'type': 'string', 'title': 'Series'},
        'country': {'type': 'string', 'title': 'Country'},
        'value': {
            'type': 'string',
            'title': 'Discount amount',
            'minLength': 10,
        },
        'percent': {
            'type': 'integer',
            'title': 'Percent',
            'minimum': 0,
            'maximum': 100,
        },
        'first_order': {
            'title': 'First order',
            'type': 'object',
            'properties': {
                'place_ids': {
                    'title': 'Places',
                    'type': 'array',
                    'items': {'type': 'string'},
                },
                'brand_ids': {
                    'title': 'Brands',
                    'type': 'array',
                    'items': {'type': 'string'},
                },
            },
        },
    },
}

DEFAULT_UI_SCHEMA = {
    'descr': {'ui:widget': 'textarea'},
    'description': {'ui:widget': 'textarea'},
}


@pytest.mark.config(
    COUPONS_SERVICE_MAP_SERIES_EDIT_FORM_SCHEMAS={
        'eats': {
            'json_schema': DEFAULT_JSON_SCHEMA,
            'ui_schema': DEFAULT_UI_SCHEMA,
        },
    },
)
async def test_get_json_schema_simple(taxi_config, taxi_coupons):
    response = await taxi_coupons.get(
        '/admin/get-json-schema', params={'service': 'eats'},
    )
    assert response.status_code == 200
    assert response.json()['ui_schema'] == DEFAULT_UI_SCHEMA
    assert response.json()['json_schema'] == DEFAULT_JSON_SCHEMA


async def test_no_such_service(taxi_config, taxi_coupons):
    expected_response_body = {'json_schema': {}, 'ui_schema': {}}

    response = await taxi_coupons.get(
        '/admin/get-json-schema', params={'service': 'eats'},
    )
    assert response.status_code == 200
    assert response.json() == expected_response_body

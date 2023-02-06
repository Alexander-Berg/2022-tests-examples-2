import pytest

from form_builder.models import external_suggest as es
from form_builder.utils import field_types as ftps


@pytest.mark.parametrize(
    'query_text, expected_result',
    [('bm', ['BMW']), ('з', ['ЗАЗ', 'ЗИЛ', 'ЗиС']), ('blah', [])],
)
@pytest.mark.usefixtures('mock_cars_catalog')
async def test_brand_suggest(
        mk_template, field, cars_brands_suggests, query_text, expected_result,
):
    _es = es.ExternalSource('brand', 'cars_brands_suggests', None, None, None)
    _es.check_state(fields_by_code={})

    values = await cars_brands_suggests.suggest(
        value=ftps.Value({'type': 'string', 'stringValue': query_text}),
        values={
            'field_code': ftps.Value(
                {'type': 'string', 'stringValue': query_text},
            ),
        },
        main_field=field(
            'field_code',
            external_source=_es,
            template=mk_template('short string'),
        ),
        dependent_fields=[],
        limit=10,
    )
    assert [x.value.get_raw_value() for x in values] == expected_result


@pytest.mark.usefixtures('mock_cars_catalog')
async def test_model_suggest(mk_template, field, cars_models_suggests):
    _brands_es = es.ExternalSource(
        'brand', 'cars_brands_suggests', None, None, None,
    )
    _brands_es.check_state(fields_by_code={})

    _es = es.ExternalSource(
        'model', 'cars_models_suggests', None, None, {'brand': 'brand_field'},
    )
    _es.check_state(
        fields_by_code={
            'brand_field': field(
                'brand_field',
                external_source=_brands_es,
                template=mk_template('short string'),
            ),
            'model_field': field(
                'model_field', template=mk_template('short string'),
            ),
        },
    )

    values = await cars_models_suggests.suggest(
        value=ftps.Value({'type': 'string', 'stringValue': 'i8'}),
        values={
            'model_field': ftps.Value({'type': 'string', 'stringValue': 'i'}),
            'brand_field': ftps.Value(
                {'type': 'string', 'stringValue': 'BMW'},
            ),
        },
        main_field=field(
            'model_field',
            external_source=_es,
            template=mk_template('short string'),
        ),
        dependent_fields=[],
        limit=10,
    )
    assert [x.value.get_raw_value() for x in values] == ['i3', 'i8']

import json

import pytest


PARTY_SUGGEST_ITEM_WITHOUT_ADDRESS: dict = {
    'value': 'ООО рогаИкопыта',
    'unrestricted_value': 'ООО рогаИкопыта',
    'data': {
        'hid': 'abc',
        'inn': '123',
        'kpp': '123',
        'ogrn': '123',
        'ogrn_date': 1469998800000,
        'type': 'LEGAL',
        'finance': {'tax_system': 'SRP'},
        'name': {
            'full': 'рогаИкопыта',
            'short': 'рогаИкопыта',
            'full_with_opf': (
                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ ' 'рогаИкопыта'
            ),
            'short_with_opf': 'ООО рогаИкопыта',
        },
        'okved': '123',
        'okved_type': '2014',
        'address': None,
        'state': {
            'actuality_date': 1469998800000,
            'registration_date': 1469998800000,
            'status': 'ACTIVE',
            'liquidation_date': None,
        },
    },
}
PARTY_SUGGEST_ITEM_WITH_ADDRESS: dict = {
    **PARTY_SUGGEST_ITEM_WITHOUT_ADDRESS,
    'data': {
        **PARTY_SUGGEST_ITEM_WITHOUT_ADDRESS['data'],
        'address': {
            'value': 'г Калуга, ул Вишневского, д 17, кв 55',
            'unrestricted_value': (
                '248007, Калужская обл, '
                'г Калуга, ул Вишневского, д 17, кв 55'
            ),
            'data': {
                'source': '',
                'qc': '0',
                'city': 'Калуга',
                'city_with_type': 'г Калуга',
                'street_with_type': 'ул Вишневского',
                'house': '17',
                'postal_code': None,
            },
        },
    },
}


def _array(*values):
    return {'arrayValue': values, 'type': 'array'}


def _string(value: str):
    return {'stringValue': value, 'type': 'string'}


def _integer(value: int):
    return {'integerValue': value, 'type': 'integer'}


@pytest.mark.parametrize(
    'with_address, description',
    [
        (
            True,
            (
                'ООО рогаИкопыта, 248007, Калужская обл, '
                'г Калуга, ул Вишневского, д 17, кв 55'
            ),
        ),
        (False, 'ООО рогаИкопыта'),
    ],
)
async def test_dadata(
        mock_dadata_suggestions,
        taxi_form_builder_web,
        with_address,
        description,
):
    @mock_dadata_suggestions('/suggestions/api/4_1/rs/suggest/party')
    def _suggest_handler(_):
        item = (
            PARTY_SUGGEST_ITEM_WITH_ADDRESS
            if with_address
            else PARTY_SUGGEST_ITEM_WITHOUT_ADDRESS
        )
        return {'suggestions': [item]}

    response = await taxi_form_builder_web.post(
        '/v1/external-sources/form/suggest/',
        json={
            'form_code': 'form_1',
            'field_code': 'field_1',
            'values': {'field_1': _string('abc')},
            'limit': 10,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'items': [
            {
                'text': 'ООО рогаИкопыта',
                'value': {'stringValue': 'ООО рогаИкопыта', 'type': 'string'},
                'description': description,
                'dependent_fields': {
                    'inn': {'stringValue': '123', 'type': 'string'},
                    'tax_system': {'stringValue': 'SRP', 'type': 'string'},
                    'registered_at': {
                        'datetimeValue': '2016-08-01T03:00:00+03:00',
                        'type': 'datetime',
                    },
                },
                'uniq_id': 'abc',
            },
        ],
    }


async def test_dadata_bank(
        load_json, mock_dadata_suggestions, taxi_form_builder_web,
):
    @mock_dadata_suggestions('/suggestions/api/4_1/rs/suggest/bank')
    def _handler(_):
        return load_json('dadata_find_bank_response.json')

    response = await taxi_form_builder_web.post(
        '/v1/external-sources/form/suggest/',
        json={
            'form_code': 'form_1',
            'field_code': 'field_dadata_bank',
            'values': {'field_dadata_bank': _string('abc')},
            'limit': 0,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'items': [
            {
                'text': 'ПАО СБЕРБАНК',
                'value': {'stringValue': 'ПАО СБЕРБАНК', 'type': 'string'},
                'description': '044525225, г Москва, ул Вавилова, д 19',
                'uniq_id': '044525225',
            },
        ],
    }


async def test_geodata(taxi_form_builder_web):
    response = await taxi_form_builder_web.post(
        '/v1/external-sources/form/suggest/',
        json={
            'form_code': 'form_1',
            'field_code': 'field_geo_name',
            'values': {'field_geo_name': _string('мо')},
            'limit': 10,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'items': [
            {
                'text': 'Москва',
                'value': {'stringValue': 'Москва', 'type': 'string'},
                'description': 'Москва, Московская Область, Россия',
                'dependent_fields': {
                    'field_geo_region': {'integerValue': 3, 'type': 'integer'},
                },
                'uniq_id': '3-ru',
            },
            {
                'text': 'Могилёв',
                'value': {'stringValue': 'Могилёв', 'type': 'string'},
                'description': 'Могилёв, Могилёвская область, Белорусь',
                'dependent_fields': {
                    'field_geo_region': {'integerValue': 6, 'type': 'integer'},
                },
                'uniq_id': '6-ru',
            },
        ],
    }


@pytest.mark.config(
    FORM_BUILDER_GEOSUGGEST_FILTER_BY_COUNTRY={'country_ids': [4, 225]},
)
@pytest.mark.parametrize(
    'field_extra_kwargs, countries_filter, found_values',
    [
        (
            {'country_ids': 'country_ids_filter'},
            {'country_ids_filter': _array(_integer(225))},
            [_string('Москва')],
        ),
        (
            {'country_ids': 'country_id_filter'},
            {'country_id_filter': _integer(225)},
            [_string('Москва')],
        ),
        (
            {'countries': 'country_filter'},
            {'country_filter': _array(_string('Russia'))},
            [_string('Москва')],
        ),
        (None, {}, [_string('Москва'), _string('Могилёв')]),
        pytest.param(
            {
                'country_ids': 'country_ids_filter',
                'countries': 'country_filter',
            },
            {},
            [_string('Москва')],
            marks=pytest.mark.config(
                FORM_BUILDER_GEOSUGGEST_FILTER_BY_COUNTRY={
                    'country_ids': [225],
                },
            ),
        ),
    ],
)
async def test_geodata_with_country_filter(
        web_context,
        taxi_form_builder_web,
        field_extra_kwargs,
        countries_filter,
        found_values,
):

    await web_context.pg.primary.fetch(
        """
    UPDATE form_builder.fields
    SET external_source = (
        'geo_suggests_city', NULL, 'name', NULL, $1::JSON
    )::form_builder.external_source_t
    WHERE code = 'field_geo_name'
    """,
        field_extra_kwargs and json.dumps(field_extra_kwargs),
    )

    response = await taxi_form_builder_web.post(
        '/v1/external-sources/form/suggest/',
        json={
            'form_code': 'form_1',
            'field_code': 'field_geo_name',
            'values': {'field_geo_name': _string('мо'), **countries_filter},
            'limit': 10,
        },
    )
    assert response.status == 200, await response.text()
    assert [
        x['value'] for x in (await response.json())['items']
    ] == found_values


@pytest.mark.usefixtures('mock_cars_catalog')
async def test_cars_brands(taxi_form_builder_web):
    response = await taxi_form_builder_web.post(
        '/v1/external-sources/form/suggest/',
        json={
            'form_code': 'form_1',
            'field_code': 'car_brand',
            'values': {'car_brand': _string('bm')},
            'limit': 10,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'items': [
            {
                'text': 'BMW',
                'value': _string('BMW'),
                'description': 'BMW',
                'uniq_id': 'BMW',
            },
        ],
    }


@pytest.mark.usefixtures('mock_cars_catalog')
async def test_cars_models(taxi_form_builder_web):
    response = await taxi_form_builder_web.post(
        '/v1/external-sources/form/suggest/',
        json={
            'form_code': 'form_1',
            'field_code': 'car_model',
            'values': {'car_brand': _string('BMW'), 'car_model': _string('i')},
            'limit': 10,
        },
    )
    assert response.status == 200, await response.text()
    assert await response.json() == {
        'items': [
            {
                'text': 'i3',
                'value': _string('i3'),
                'description': 'brand BMW, model i3',
                'uniq_id': 'BMW==|==i3',
            },
            {
                'text': 'i8',
                'value': _string('i8'),
                'description': 'brand BMW, model i8',
                'uniq_id': 'BMW==|==i8',
            },
        ],
    }

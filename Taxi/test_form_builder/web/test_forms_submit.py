import json

import pytest


def _int_value(value: int):
    return {'type': 'integer', 'integerValue': value}


def _number_value(value: float):
    return {'type': 'number', 'numberValue': value}


def _str_value(value: str):
    return {'type': 'string', 'stringValue': value}


def _dt_value(value: str):
    return {'type': 'datetime', 'datetimeValue': value}


def _array_value(*values):
    return {'type': 'array', 'arrayValue': list(values)}


def _file_value(value: str):
    return {'type': 'file', 'fileValue': value}


@pytest.mark.parametrize(
    'form_code,form_data,expected_code,expected_data,expected_db_data',
    [
        (
            'form_1',
            {
                'test_case': _int_value(1),
                'field_1': _str_value('test1'),
                'field_2': _dt_value('2020-03-02T14:00:00+03:00'),
                'field_3': _str_value('test2'),
                'field_4': _str_value('test3'),
                'field_5': _array_value(
                    _str_value('test4'), _str_value('test5'),
                ),
                'number_field': _number_value(1),
            },
            200,
            {},
            # A, B, C - ids of personal API docs
            {
                'field_1': _str_value('A'),
                'field_2': _dt_value('2020-03-02T14:00:00+03:00'),
                'field_3': _str_value('B'),
                'field_4': _str_value('C'),
                'test_case': _int_value(1),
                'field_5': _array_value(_str_value('D'), _str_value('E')),
                'multiselect_with_no_default': None,
                'multiselect_with_self_default': _array_value(_str_value('A')),
                'multiselect_with_template_default': None,
                'multiselect_with_template_default_and_self': None,
                'multiselect_with_template_default_and_value_default': (
                    _array_value(_str_value('A'))
                ),
                'multiselect_with_template_default_and_self_and_value_default': (  # noqa E501
                    _array_value(_str_value('C'))
                ),
                'number_field': _number_value(1),
            },
        ),
        (
            'form_1',
            {
                'test_case': _int_value(1),
                'field_1': _str_value('test1'),
                'field_2': _dt_value('test'),
                'field_3': _str_value('test2'),
                'field_4': _str_value('test3'),
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': '"test" is not instance of "datetime"',
            },
            None,
        ),
        (
            'form_1',
            {
                'test_case': _int_value(1),
                'field_1': _str_value('???'),
                'field_2': _dt_value('2020-03-02T14:00:00+03:00'),
                'field_3': _str_value('test2'),
                'field_4': _str_value('test3'),
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'value "???" does not match regular expression "^\\w+$"'
                ),
            },
            None,
        ),
        (
            'form_1',
            {
                'field_1': _str_value('test1'),
                'field_2': _dt_value('2020-03-02T14:00:00+03:00'),
                'field_3': _str_value('test2'),
                'field_4': _str_value('test3'),
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'field "test_case" is obligatory',
            },
            None,
        ),
        (
            'form_1',
            {
                'test_case': _int_value(1),
                'field_1': _str_value('test1'),
                'field_3': _str_value('test2'),
                'field_4': _str_value('test3'),
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'field "field_2" is obligatory',
            },
            None,
        ),
        (
            'form_1',
            {'test_case': _int_value(2), 'field_4': _str_value('test')},
            200,
            {},
            None,
        ),
        (
            'form_1',
            {
                'test_case': _int_value(5),
                'field_2': _dt_value('2020-03-02T14:00:00+03:00'),
            },
            200,
            {},
            None,
        ),
        (
            'form_1',
            {'test_case': _int_value(0)},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': 'value "0" is not corresponding to any choice',
            },
            None,
        ),
        (
            'form_2',
            {},
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'form "form_2" is not found',
            },
            None,
        ),
        (
            'form_1',
            {
                'test_case': _int_value(1),
                'field_1': _str_value('test1'),
                'field_2': _dt_value('2020-03-02T14:00:00+03:00'),
                'field_3': _str_value('test2'),
                'field_4': _str_value('test3'),
                'field_5': _array_value(
                    _str_value('test4'), _str_value('test5'),
                ),
                'multiselect_with_self_default': _array_value(
                    _str_value('A'), _str_value('C'),
                ),
            },
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'value "[\'A\', \'C\']" is not corresponding to any choice'
                ),
            },
            None,
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('mockserver_personal')
async def test_forms_submit(
        taxi_form_builder_web,
        web_context,
        form_code,
        form_data,
        expected_code,
        expected_data,
        expected_db_data,
):
    response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/',
        params={'code': form_code},
        json={'data': form_data},
    )
    assert response.status == expected_code, await response.text()
    data = await response.json()
    if expected_data is not None:
        assert data == expected_data
    if expected_db_data is not None:
        records = await web_context.pg.primary.fetch(
            'SELECT * FROM form_builder.response_values;',
        )
        assert expected_db_data == {
            record['key']: (
                json.loads(record['value']) if record['value'] else None
            )
            for record in records
        }
        queue_size = await web_context.pg.primary.fetchval(
            'SELECT count(*) FROM form_builder.request_queue;',
        )
        assert queue_size == (2 if form_code == 'form_1' else 0)


@pytest.mark.parametrize(
    'form_data, external_sources, expected_code, expected_data',
    [
        (
            {
                'suggest_source': _str_value('123'),
                'suggest_dependent_non_editable': _str_value('1234'),
                'suggest_dependent_non_editable_2': _dt_value(
                    '2016-08-01T03:00:00+03:00',
                ),
            },
            {'suggest_source': {'uniq_id': 'abc'}},
            200,
            {},
        ),
        (
            {
                'suggest_source': _str_value('123'),
                'suggest_dependent_non_editable': _str_value('1234'),
                'suggest_dependent_editable': _str_value('12345'),
                'suggest_dependent_non_editable_2': _dt_value(
                    '2016-08-01T03:00:00+03:00',
                ),
            },
            {'suggest_source': {'uniq_id': 'abc'}},
            200,
            {},
        ),
        (
            {
                'suggest_source': _str_value('123'),
                'suggest_dependent_non_editable': _str_value('123'),
                'suggest_dependent_non_editable_2': _dt_value(
                    '2016-08-01T03:00:00+03:00',
                ),
            },
            {'suggest_source': {'uniq_id': 'abc'}},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'Non editable value for field '
                    '"suggest_dependent_non_editable" changed'
                ),
            },
        ),
        (
            {
                'geosuggest_source': _str_value('Москва'),
                'geosuggest_dependent_non_editable': _int_value(3),
            },
            {'geosuggest_source': {'uniq_id': '3-ru'}},
            200,
            {},
        ),
        (
            {
                'geosuggest_source': _str_value('Москва'),
                'geosuggest_dependent_non_editable': _int_value(4),
            },
            {'geosuggest_source': {'uniq_id': '3-ru'}},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'Non editable value for field '
                    '"geosuggest_dependent_non_editable" changed'
                ),
            },
        ),
        (
            {
                'geosuggest_source': _str_value('Москва'),
                'geosuggest_dependent_non_editable': _int_value(3),
            },
            {'geosuggest_source': {'uniq_id': '3-ra'}},
            400,
            {
                'code': 'VALIDATION_ERROR',
                'message': (
                    'Non editable value for field '
                    '"geosuggest_source" changed'
                ),
            },
        ),
    ],
)
async def test_submit_check_edited(
        taxi_form_builder_web,
        mock_dadata_suggestions,
        form_data,
        external_sources,
        expected_code,
        expected_data,
):
    @mock_dadata_suggestions('/suggestions/api/4_1/rs/findById/party')
    def _handler(_):
        return {
            'suggestions': [
                {
                    'value': 'ООО рогаИкопыта',
                    'unrestricted_value': 'ООО рогаИкопыта',
                    'data': {
                        'hid': 'abc',
                        'inn': '123',
                        'kpp': '1234',
                        'ogrn': '123',
                        'ogrn_date': 1469998800000,
                        'type': 'LEGAL',
                        'name': {
                            'full': 'рогаИкопыта',
                            'short': 'рогаИкопыта',
                            'full_with_opf': (
                                'ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ '
                                'рогаИкопыта'
                            ),
                            'short_with_opf': 'ООО рогаИкопыта',
                        },
                        'okved': '123',
                        'okved_type': '2014',
                        'address': {
                            'value': 'г Калуга, ул Вишневского, д 17, кв 55',
                            'unrestricted_value': (
                                '248007, Калужская обл, '
                                'г Калуга, ул Вишневского, д 17, кв 55'
                            ),
                            'data': {
                                'source': '',
                                'qc': '0',
                                'city_with_type': 'г Калуга',
                                'street_with_type': 'ул Вишневского',
                                'house': '17',
                                'postal_code': '248007',
                            },
                        },
                        'state': {
                            'actuality_date': 1469998800000,
                            'registration_date': 1469998800000,
                            'status': 'ACTIVE',
                        },
                    },
                },
            ],
        }

    response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/',
        params={'code': 'form_3'},
        json={'data': form_data, 'external_sources': external_sources},
    )
    assert response.status == expected_code, await response.text()
    data = await response.json()
    if expected_data is not None:
        assert data == expected_data


@pytest.mark.parametrize(
    'form_code, form_data, expected_data',
    [
        (
            'form_1',
            {'user_phone': _str_value('+7999999999')},
            {
                'code': 'VALIDATION_ERROR',
                'message': '"sms_validator" verification not passed',
            },
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'src': 'form-builder', 'dst': 'personal'}])
@pytest.mark.usefixtures('cached_personal_mock')
async def test_failed_submit(
        taxi_form_builder_web, form_code, form_data, expected_data,
):
    response = await taxi_form_builder_web.post(
        '/v1/view/forms/submit/',
        params={'code': form_code},
        json={'data': form_data},
    )
    assert response.status == 400, await response.text()
    assert expected_data == await response.json()

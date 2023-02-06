import http
import json

import pytest

from test_document_templator import common


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    [
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'language': {
                        'type': 'string',
                        'value': 'ru',
                        'data_usage': 'OWN_DATA',
                    },
                    'keyset': {
                        'type': 'string',
                        'value': 'tariff',
                        'data_usage': 'OWN_DATA',
                    },
                    'key': {
                        'type': 'string',
                        'value': 'with_args',
                        'data_usage': 'OWN_DATA',
                    },
                    'num': {
                        'type': 'number',
                        'value': 10,
                        'data_usage': 'OWN_DATA',
                    },
                    'args': {
                        'type': 'array',
                        'value': [2],
                        'data_usage': 'OWN_DATA',
                    },
                    'operator': 'TRANSLATE',
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '12-через 2 минуты'},
        ),
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'language': {
                        'type': 'string',
                        'value': 'ru',
                        'data_usage': 'OWN_DATA',
                    },
                    'keyset': {
                        'type': 'string',
                        'value': 'tariff',
                        'data_usage': 'OWN_DATA',
                    },
                    'key': {
                        'type': 'string',
                        'value': 'with_kwargs',
                        'data_usage': 'OWN_DATA',
                    },
                    'kwargs': {
                        'type': 'array',
                        'value': {'minutes': 2},
                        'data_usage': 'OWN_DATA',
                    },
                    'operator': 'TRANSLATE',
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '12-через 2 минуты'},
        ),
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'language': {
                        'type': 'string',
                        'value': 'ru',
                        'data_usage': 'OWN_DATA',
                    },
                    'keyset': {
                        'type': 'string',
                        'value': 'tariff',
                        'data_usage': 'OWN_DATA',
                    },
                    'key': {
                        'type': 'string',
                        'value': 'with_kwargs',
                        'data_usage': 'OWN_DATA',
                    },
                    'kwargs': {
                        'type': 'array',
                        'value': {'invalid': 2},
                        'data_usage': 'OWN_DATA',
                    },
                    'operator': 'TRANSLATE',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_ARGUMENTS_FOR_TANKER_KEY',
                'message': 'Invalid arguments for tanker key',
            },
        ),
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'language': {
                        'type': 'string',
                        'value': 'ru',
                        'data_usage': 'OWN_DATA',
                    },
                    'keyset': {
                        'type': 'string',
                        'value': 'tariff',
                        'data_usage': 'OWN_DATA',
                    },
                    'operator': 'TRANSLATE',
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Some parameters are invalid',
            },
        ),
    ],
)
@pytest.mark.translations(
    tariff={
        'with_args': {'ru': 'через %d минуты'},
        'with_kwargs': {'ru': 'через %(minutes)d минуты'},
    },
)
async def test_generate_preview_translation_in_parameter(
        api_app_client, param, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}
    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {
                    'template_id': '000000000000000000000008',
                    'params': [
                        param,
                        {
                            'type': 'number',
                            'data_usage': 'OWN_DATA',
                            'name': 'number',
                            'value': 12,
                        },
                    ],
                },
            ],
        },
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    if response.status == http.HTTPStatus.BAD_REQUEST:
        content.pop('details')
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    [
        (
            {
                'name': 'number',
                'type': 'number',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'ROUND',
                    'ndigits': {
                        'value': 1,
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                    },
                    'value': {
                        'value': '1.05',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '1.0-value'},
        ),
        (
            {
                'name': 'number',
                'type': 'number',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'ROUND',
                    'ndigits': {
                        'value': 1,
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                    },
                    'value': {
                        'value': 'invalid',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'number', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. '
                    'Need: "number". Got: "invalid".'
                ),
            },
        ),
        (
            {
                'name': 'number',
                'type': 'number',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'ROUND',
                    'ndigits': {
                        'value': 1,
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                    },
                    'value': {
                        'value': '1.051',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '1.1-value'},
        ),
        (
            {
                'name': 'number',
                'type': 'number',
                'data_usage': 'CALCULATED',
                'value': {
                    'right': {
                        'type': 'number',
                        'value': {
                            'operator': 'TO_DECIMAL',
                            'value': {
                                'value': '3',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                        },
                        'data_usage': 'CALCULATED',
                    },
                    'left': {
                        'type': 'number',
                        'value': 5.0,
                        'data_usage': 'OWN_DATA',
                    },
                    'ndigits': {
                        'value': 2,
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                    },
                    'operator': 'DIV',
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '1.67-value'},
        ),
        (
            {
                'name': 'number',
                'type': 'number',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'TO_DECIMAL',
                    'value': {
                        'value': 'invalid_value',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'number', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. '
                    'Need: "number". Got: "invalid_value".'
                ),
            },
        ),
    ],
)
async def test_generate_preview_working_with_decimal_in_parameter(
        api_app_client, param, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}
    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {
                    'template_id': '000000000000000000000008',
                    'params': [
                        param,
                        {
                            'type': 'string',
                            'data_usage': 'OWN_DATA',
                            'name': 'string',
                            'value': 'value',
                        },
                    ],
                },
            ],
        },
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    [
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'NUMBER_TO_WORDS',
                    'number': {
                        'value': 12.0,
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                    },
                    'language': {
                        'value': 'ru',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '40-двенадцать'},
        ),
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'NUMBER_TO_WORDS',
                    'number': {
                        'value': 'invalid_number',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                    'language': {
                        'value': 'ru',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'number', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. '
                    'Need: "number". Got: "invalid_number".'
                ),
            },
        ),
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'NUMBER_TO_WORDS',
                    'number': {
                        'value': 12,
                        'data_usage': 'OWN_DATA',
                        'type': 'number',
                    },
                    'language': {
                        'value': 'invalid_language',
                        'data_usage': 'OWN_DATA',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_LANGUAGE_IN_NUMBER_TO_WORDS_PARAMETER',
                'details': {'template_name': 'name'},
                'message': 'Invalid language: "invalid_language".',
            },
        ),
    ],
)
async def test_generate_preview_number_to_words_in_parameter(
        api_app_client, param, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}

    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {
                    'template_id': '000000000000000000000008',
                    'params': [
                        param,
                        {
                            'type': 'number',
                            'data_usage': 'OWN_DATA',
                            'name': 'number',
                            'value': 40,
                        },
                    ],
                },
            ],
        },
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    (
        (
            {
                'name': 'string',
                'type': 'string',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'DATETIME',
                    'datetime': {
                        'data_usage': 'OWN_DATA',
                        'value': '2019-02-01T03:00:00+03:00',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '40-01.02.2019'},
        ),
        (
            {
                'data_usage': 'CALCULATED',
                'name': 'string',
                'type': 'string',
                'value': {
                    'operator': 'DATETIME',
                    'datetime': {
                        'data_usage': 'OWN_DATA',
                        'value': '2019-02-01T03:00:00+03:00',
                        'type': 'string',
                    },
                    'format': {
                        'data_usage': 'OWN_DATA',
                        'value': '%A, %d. %B %Y %I:%M',
                        'type': 'string',
                    },
                    'locale': {
                        'data_usage': 'OWN_DATA',
                        'value': 'ru',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '40-Пятница, 01. февраля 2019 03:00'},
        ),
        (
            {
                'data_usage': 'CALCULATED',
                'name': 'string',
                'type': 'string',
                'value': {
                    'operator': 'DATETIME',
                    'datetime': {
                        'data_usage': 'OWN_DATA',
                        'value': '2019-02-01T03:00:00+03:00',
                        'type': 'string',
                    },
                    'format': {
                        'data_usage': 'OWN_DATA',
                        'value': '%A, %d. %B %Y %I:%M',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '40-Пятница, 01. февраля 2019 03:00'},
        ),
        (
            {
                'data_usage': 'CALCULATED',
                'name': 'string',
                'type': 'string',
                'value': {
                    'operator': 'DATETIME',
                    'datetime': {
                        'data_usage': 'OWN_DATA',
                        'value': '2019-02-01T03:00:00+03:00',
                        'type': 'string',
                    },
                    'format': {
                        'data_usage': 'OWN_DATA',
                        'value': '%A, %d. %B %Y %I:%M',
                        'type': 'string',
                    },
                    'locale': {
                        'data_usage': 'OWN_DATA',
                        'value': 'en',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '40-Friday, 01. February 2019 03:00'},
        ),
        (
            {
                'data_usage': 'CALCULATED',
                'name': 'string',
                'type': 'string',
                'value': {
                    'operator': 'DATETIME',
                    'datetime': {
                        'data_usage': 'OWN_DATA',
                        'value': '2019-02-01T03:00:00+03:00',
                        'type': 'string',
                    },
                    'format': {
                        'data_usage': 'OWN_DATA',
                        'value': '%A, %d. %B %Y %I:%M',
                        'type': 'string',
                    },
                    'locale': {
                        'data_usage': 'OWN_DATA',
                        'value': 'invalid_locale',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '40-Пятница, 01. февраля 2019 03:00'},
        ),
        (
            {
                'data_usage': 'CALCULATED',
                'name': 'string',
                'type': 'string',
                'value': {
                    'operator': 'DATETIME',
                    'datetime': {
                        'data_usage': 'OWN_DATA',
                        'value': 'invalid_data',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'datetime', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. '
                    'Need: "datetime". Got: "invalid_data".'
                ),
            },
        ),
    ),
)
@pytest.mark.translations(
    notify={
        'helpers.month_1_part': {'en': 'January', 'ru': 'января'},
        'helpers.month_2_part': {'en': 'February', 'ru': 'февраля'},
        'helpers.month_3_part': {'en': 'March', 'ru': 'марта'},
        'helpers.month_4_part': {'en': 'April', 'ru': 'апреля'},
        'helpers.month_5_part': {'en': 'May', 'ru': 'мая'},
        'helpers.month_6_part': {'en': 'June', 'ru': 'июня'},
        'helpers.month_7_part': {'en': 'July', 'ru': 'июля'},
        'helpers.month_8_part': {'en': 'August', 'ru': 'августа'},
        'helpers.month_9_part': {'en': 'September', 'ru': 'сентября'},
        'helpers.month_10_part': {'en': 'October', 'ru': 'октября'},
        'helpers.month_11_part': {'en': 'November', 'ru': 'ноября'},
        'helpers.month_12_part': {'en': 'December', 'ru': 'декабря'},
        'helpers.weekday_1': {'en': 'Monday', 'ru': 'Понедельник'},
        'helpers.weekday_2': {'en': 'Tuesday', 'ru': 'Вторник'},
        'helpers.weekday_3': {'en': 'Wednesday', 'ru': 'Среда'},
        'helpers.weekday_4': {'en': 'Thursday', 'ru': 'Четверг'},
        'helpers.weekday_5': {'en': 'Friday', 'ru': 'Пятница'},
        'helpers.weekday_6': {'en': 'Saturday', 'ru': 'Суббота'},
        'helpers.weekday_7': {'en': 'Sunday', 'ru': 'Воскресенье'},
    },
)
@pytest.mark.usefixtures('requests_handlers')
@pytest.mark.config(**common.REQUEST_CONFIG)
async def test_generate_preview_with_datetime_parameter(
        api_app_client, param, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}

    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {
                    'template_id': '000000000000000000000008',
                    'params': [
                        param,
                        {
                            'type': 'number',
                            'data_usage': 'OWN_DATA',
                            'name': 'number',
                            'value': 40,
                        },
                    ],
                },
            ],
        },
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    (
        (
            {
                'name': 'object',
                'type': 'object',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'DICT_BUILD',
                    'values': [
                        {
                            'key': {
                                'value': 'key1',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                            'value': {
                                'value': 'val1',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                        },
                        {
                            'key': {
                                'value': 'key2',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                            'value': {
                                'value': 'val2',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                        },
                    ],
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': 'val1-val2'},
        ),
        (
            {
                'name': 'object',
                'type': 'object',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'DICT_BUILD',
                    'values': [
                        {
                            'key': {
                                'value': ['key1'],
                                'data_usage': 'OWN_DATA',
                                'type': 'array',
                            },
                            'value': {
                                'value': 'val1',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                        },
                    ],
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'key', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. '
                    'Need: "not array, object". Got: "[\'key1\']".'
                ),
            },
        ),
        (
            {
                'name': 'object',
                'type': 'object',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'DICT_BUILD',
                    'values': [
                        {
                            'key': {
                                'value': {'key1': 'val11'},
                                'data_usage': 'OWN_DATA',
                                'type': 'object',
                            },
                            'value': {
                                'value': 'val12',
                                'data_usage': 'OWN_DATA',
                                'type': 'string',
                            },
                        },
                    ],
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'DATA_TYPE_MATCHING_FAILED',
                'details': {'param_name': 'key', 'template_name': 'name'},
                'message': (
                    'Data type matching failed. '
                    'Need: "not array, object". Got: "{\'key1\': \'val11\'}".'
                ),
            },
        ),
    ),
)
async def test_generate_preview_dict_build_in_parameter(
        api_app_client, param, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}

    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {'template_id': '000000000000000000000010', 'params': [param]},
            ],
        },
    }
    response = await api_app_client.post(
        '/v1/templates/preview/generate/', json=body, headers=headers,
    )
    content = await response.text()
    assert response.status == expected_status, content
    content = json.loads(content)
    content.pop('id', None)
    content.pop('status', None)
    assert content == expected_content

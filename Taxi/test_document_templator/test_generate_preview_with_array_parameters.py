import http
import json

import pytest


@pytest.mark.parametrize(
    'param, expected_status, expected_content',
    (
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'REGEXP_FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'value': 'UPPER'},
                            {'value': 'not all UPPER'},
                            {'value': ''},
                            {'value': 2},
                            {'value': None, 'b': 4},
                            {},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.value',
                        'type': 'string',
                    },
                    'pattern': {
                        'data_usage': 'OWN_DATA',
                        'value': '^[A-Z]+$',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '[{\'value\': \'UPPER\'}]'},
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'REGEXP_FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'value': 'UPPER'},
                            {'value': 'not all UPPER'},
                            {'value': 'UPPER\nlower'},
                            {'value': ''},
                            {'value': 2},
                            {'value': None, 'b': 4},
                            {},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.value',
                        'type': 'string',
                    },
                    'pattern': {
                        'data_usage': 'OWN_DATA',
                        'value': '^[A-Z]+$',
                        'type': 'string',
                    },
                    'flags': {
                        'data_usage': 'OWN_DATA',
                        'value': ['MULTILINE'],
                        'type': 'array',
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'value\': \'UPPER\'}, {\'value\': \'UPPER\\nlower\'}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'REGEXP_FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.value',
                        'type': 'string',
                    },
                    'pattern': {
                        'data_usage': 'OWN_DATA',
                        'value': '[]',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_PATTERN',
                'details': {'pattern': '[]', 'template_name': 'name'},
                'message': 'unterminated character set at position 0',
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'REGEXP_FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.value',
                        'type': 'string',
                    },
                    'pattern': {
                        'data_usage': 'OWN_DATA',
                        'value': '[A-Z]',
                        'type': 'string',
                    },
                    'flags': {
                        'data_usage': 'OWN_DATA',
                        'value': ['INVALID'],
                        'type': 'array',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'INVALID_REGEXP_FLAG',
                'details': {'template_name': 'name'},
                'message': 'invalid regexp flag: "INVALID"',
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'MANY_FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                    'compared_value': {
                        'value': {
                            'data_usage': 'OWN_DATA',
                            'value': [1, 2],
                            'type': 'array',
                        },
                        'path': {
                            'data_usage': 'OWN_DATA',
                            'value': '#item',
                            'type': 'string',
                        },
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'a\': 1, \'b\': 1},'
                    ' {\'a\': 1, \'b\': 2}, '
                    '{\'a\': 2, \'b\': 1}, '
                    '{\'a\': 2, \'b\': 2}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'MANY_FILTER_NOT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '[]'},
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'MANY_FILTER_NOT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': ('[{\'b\': 4}, ' '{\'a\': None, \'b\': 4}]')},
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'MANY_FILTER_NOT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                    'compared_value': {
                        'value': {
                            'data_usage': 'OWN_DATA',
                            'value': [1, 2],
                            'type': 'array',
                        },
                        'path': {
                            'data_usage': 'OWN_DATA',
                            'value': '#item',
                            'type': 'string',
                        },
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'a\': 3, \'b\': 3}, '
                    '{\'a\': 3, \'b\': 4}, '
                    '{\'b\': 4}, '
                    '{\'a\': None, \'b\': 4}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                    'compared_value': {
                        'value': {
                            'data_usage': 'OWN_DATA',
                            'value': {'b': 1},
                            'type': 'array',
                        },
                        'path': {
                            'data_usage': 'OWN_DATA',
                            'value': '#item.b',
                            'type': 'string',
                        },
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '[{\'a\': 1, \'b\': 1}, {\'a\': 1, \'b\': 2}]'},
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'FILTER',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'a\': 1, \'b\': 1}, '
                    '{\'a\': 1, \'b\': 2}, '
                    '{\'a\': 2, \'b\': 1}, '
                    '{\'a\': 2, \'b\': 2}, '
                    '{\'a\': 3, \'b\': 3}, '
                    '{\'a\': 3, \'b\': 4}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'FILTER_NOT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': ('[{\'b\': 4}, ' '{\'a\': None, \'b\': 4}]')},
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'FILTER_NOT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                            {'b': 4},
                            {'a': None, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                    'compared_value': {
                        'value': {
                            'data_usage': 'OWN_DATA',
                            'value': {'b': 1},
                            'type': 'array',
                        },
                        'path': {
                            'data_usage': 'OWN_DATA',
                            'value': '#item.b',
                            'type': 'string',
                        },
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'a\': 2, \'b\': 1}, '
                    '{\'a\': 2, \'b\': 2}, '
                    '{\'a\': 3, \'b\': 3}, '
                    '{\'a\': 3, \'b\': 4}, '
                    '{\'b\': 4}, '
                    '{\'a\': None, \'b\': 4}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'SORT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 2, 'b': 1},
                            {'a': 1, 'b': 1},
                            {'a': 3, 'b': 3},
                            {'b': 4},
                            {'a': None, 'b': 5},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                    'sort': {
                        'data_usage': 'OWN_DATA',
                        'value': 'ASC',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'a\': 1, \'b\': 1}, '
                    '{\'a\': 2, \'b\': 1}, '
                    '{\'a\': 3, \'b\': 3}, '
                    '{\'b\': 4}, '
                    '{\'a\': None, \'b\': 5}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'SORT',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 2, 'b': 1},
                            {'a': [], 'b': 1},
                            {'a': 3, 'b': 3},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                    'sort': {
                        'data_usage': 'OWN_DATA',
                        'value': 'DESC',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'UNSUPPORTED_OPERATOR',
                'details': {
                    'left': 'list',
                    'operator': '<',
                    'right': 'int',
                    'template_name': 'name',
                },
                'message': 'Unsupported operator "<" for \'list\' and \'int\'',
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'UNIQUE',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 2, 'b': 2},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '[{\'a\': 1, \'b\': 1}, {\'a\': 2, \'b\': 2}]'},
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'UNIQUE',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 1, 'b': 2},
                            {'a': 2, 'b': 1},
                            {'a': 2, 'b': 2},
                            {'a': 3, 'b': 3},
                            {'a': 3, 'b': 4},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {
                'generated_text': (
                    '[{\'a\': 1, \'b\': 1}, '
                    '{\'a\': 2, \'b\': 1}, '
                    '{\'a\': 3, \'b\': 3}]'
                ),
            },
        ),
        (
            {
                'name': 'array',
                'type': 'array',
                'data_usage': 'CALCULATED',
                'value': {
                    'operator': 'MAP',
                    'array': {
                        'data_usage': 'OWN_DATA',
                        'value': [
                            {'a': 1, 'b': 1},
                            {'a': 2, 'b': 1},
                            {'a': 3, 'b': 3},
                        ],
                        'type': 'array',
                    },
                    'path': {
                        'data_usage': 'OWN_DATA',
                        'value': '#item.a',
                        'type': 'string',
                    },
                },
            },
            http.HTTPStatus.OK,
            {'generated_text': '[1, 2, 3]'},
        ),
    ),
)
async def test_generate_with_array_dynamic_parameter(
        api_app_client, param, expected_status, expected_content,
):
    headers = {'X-Yandex-Login': 'test_name'}

    body = {
        'template': {
            'name': 'name',
            'description': 'test',
            'items': [
                {'template_id': '000000000000000000000009', 'params': [param]},
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

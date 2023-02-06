GENERATED_TEXT = (
    '<p>OWN_DATA string [some string]</p>\n'
    '<p>OWN_DATA number\n'
    '0\n'
    '</p>\n'
    '<p>OWN_DATA boolean\n'
    'False\n'
    '</p>\n'
    '<p>OWN_DATA object: 100</p>\n'
    '<p>PARENT_TEMPLATE_DATA string: some string</p>\n'
    '<p>PARENT_TEMPLATE_DATA number: 100500</p>\n'
    '<p>PARENT_TEMPLATE_DATA boolean: True</p>\n'
    '<p>PARENT_TEMPLATE_DATA object: 42</p>\n'
    '<p>SERVER_DATA string: '
    'body: {\'a\': {\'b\': [], \'c\': 1}}; queries: q1=1, '
    'q2=string</p>\n'
    '<p>SERVER_DATA number: 10.0</p>\n'
    '<p>SERVER_DATA boolean: False</p>\n'
    '<p>SERVER_DATA object: '
    'body: {\'a\': {\'b\': [], \'c\': 1}}; queries: q1=1, '
    'q2=string</p>\n'
    '<p>SERVER_DATA string: 10.0</p><p>Some content</p>'
)

TEMPLATE_PARAMS = [
    {'name': 'template parameter1', 'type': 'object'},
    {'name': 'template parameter2', 'type': 'array'},
    {'name': 'template parameter3', 'type': 'string'},
    {'name': 'template parameter4', 'type': 'number'},
    {'name': 'template parameter5', 'type': 'boolean'},
]

PARAMS = [
    {
        'name': 'template parameter1',
        'value': {
            'v1': 'str1',
            'v2': 0,
            'v3': True,
            'v4': {'v4v1': [0, 1, 2], 'v4v2': 42},
        },
    },
    {'name': 'template parameter2', 'value': [2, 1, 0]},
    {'name': 'template parameter3', 'value': 'some string'},
    {'name': 'template parameter4', 'value': 100500},
    {'name': 'template parameter5', 'value': True},
]


REQUESTS_PARAMS = [
    {
        'id': '5ff4901c583745e089e55bd1',
        'name': 'req1',
        'query': {'q1': 1, 'q2': 'string'},
        'substitutions': {'zone': 'moscow', 'tariff': 'econom'},
        'body': {'a': {'b': [], 'c': 1}},
    },
    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2'},
    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3'},
]

ITEMS_PARAMS = [
    {
        'name': 'own array parameter',
        'description': 'contains array OWN_DATA',
        'type': 'array',
        'data_usage': 'OWN_DATA',
        'value': ['mama', 'papa'],
    },
    {
        'name': 'own string parameter',
        'description': 'contains string OWN_DATA',
        'type': 'string',
        'data_usage': 'OWN_DATA',
        'value': 'some string',
    },
    {
        'name': 'own number parameter',
        'description': 'contains number OWN_DATA',
        'type': 'number',
        'data_usage': 'OWN_DATA',
        'value': 0,
    },
    {
        'name': 'own boolean parameter',
        'description': 'contains boolean OWN_DATA',
        'type': 'boolean',
        'data_usage': 'OWN_DATA',
        'value': False,
    },
    {
        'name': 'own object parameter',
        'description': 'contains object OWN_DATA',
        'type': 'object',
        'data_usage': 'OWN_DATA',
        'value': {'own_obj_data': 100},
    },
    {
        'name': 'parent template array parameter',
        'description': 'contains array PARENT_TEMPLATE_DATA',
        'type': 'array',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'template parameter2',
    },
    {
        'name': 'parent template string parameter',
        'description': 'contains string PARENT_TEMPLATE_DATA',
        'type': 'string',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'template parameter3',
    },
    {
        'name': 'parent template number parameter',
        'description': 'contains number PARENT_TEMPLATE_DATA',
        'type': 'number',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'template parameter4',
    },
    {
        'name': 'parent template boolean parameter',
        'description': 'contains boolean PARENT_TEMPLATE_DATA',
        'type': 'boolean',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'template parameter5',
    },
    {
        'name': 'parent template object parameter',
        'description': 'contains object PARENT_TEMPLATE_DATA',
        'type': 'object',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'template parameter1.v4',
    },
    {
        'name': 'server array parameter',
        'description': 'contains array SERVER_DATA',
        'type': 'array',
        'data_usage': 'SERVER_DATA',
        'value': 'req2.arr',
    },
    {
        'name': 'server string parameter',
        'description': 'contains string SERVER_DATA',
        'type': 'string',
        'data_usage': 'SERVER_DATA',
        'value': 'req1.r1',
    },
    {
        'name': 'server number parameter',
        'description': 'contains number SERVER_DATA',
        'type': 'number',
        'data_usage': 'SERVER_DATA',
        'value': 'req3.num',
    },
    {
        'name': 'server boolean parameter',
        'description': 'contains boolean SERVER_DATA',
        'type': 'boolean',
        'data_usage': 'SERVER_DATA',
        'value': 'req3.bool',
    },
    {
        'name': 'server object parameter',
        'description': 'contains object SERVER_DATA',
        'type': 'object',
        'data_usage': 'SERVER_DATA',
        'value': 'req1',
    },
]

ITEMS = [
    {
        'params': ITEMS_PARAMS,
        'requests_params': [{'id': '5ff4901c583745e089e55bd3', 'name': 'req'}],
        'description': 'item1 description',
        'template_id': '5ff4901c583745e089e55be2',
        'enabled': True,
    },
    {'content': '<p>Some content</p>', 'enabled': True},
    {'content': '<p>Invisible content</p>', 'enabled': False},
]

REQUESTS = [
    {'id': '5ff4901c583745e089e55bd1', 'name': 'req1', 'enabled': True},
    {'id': '5ff4901c583745e089e55bd2', 'name': 'req2', 'enabled': True},
    {'id': '5ff4901c583745e089e55bd3', 'name': 'req3', 'enabled': True},
    {'id': '5ff4901c583745e089e55bd4', 'name': 'req4', 'enabled': False},
]

CONTENT_ITEMS_GENERATED_TEXT = (
    'First item wth just text <strong>bold</strong>\n'
    'Second item with variables Number -&nbsp;123456, '
    'String - testString, Object param - param1Value\n'
    'Third item with request variable&nbsp;moscow_activation\n'
    '<p>Fouth item with embedded template</p><p>With parent params</p>'
    'Simple text and resolved parent template parameter&nbsp;param1Value '
    '<p><br/></p><p>With request param</p><p></p>'
    'Simple text and resolved parent template '
    'parameter&nbsp;moscow_activation <p></p><p>With own data</p><p></p>'
    'Simple text and resolved parent template parameter&nbsp;'
    'OWN DATA STRING <p></p><p><br/></p>\n'
    '<p>Fifth&nbsp;item with embedded template with requests</p>'
    '<p>With parent params</p><p></p>Activation zone&'
    'nbsp;moscow_activation <p></p><p><br/></p><p>With request param</p>'
    '<p></p>Activation zone&nbsp;moscow_activation <p></p><p><br/></p>'
    '<p>With own data</p><p></p>Activation zone&nbsp;moscow_activation'
    ' <br/><p></p>\n'
)

CONTENT_ITEMS_REQUESTS = [
    {
        'id': '5d275bc3eb584657ebbf24b2',
        'name': 'tariff_request',
        'enabled': True,
    },
    {
        'id': '5d275bc3eb584657ebbf24d9',
        'name': 'disabled_request',
        'enabled': False,
    },
]

CONTENT_ITEMS_REQUESTS_PARAMS = [
    {
        'id': '5d275bc3eb584657ebbf24b2',
        'name': 'tariff_request',
        'substitutions': {'zone': 'moscow'},
    },
]

CONTENT_ITEMS_PARAMS_IN_TEMPLATE = [
    {'name': 'string', 'type': 'string'},
    {'name': 'number', 'type': 'number'},
    {'name': 'zone', 'type': 'string'},
    {'name': 'obj', 'type': 'object'},
]

CONTENT_ITEMS_PARAMS = [
    {'name': 'string', 'value': 'testString'},
    {'name': 'number', 'value': 123456},
    {'name': 'zone', 'value': 'moscow'},
    {
        'name': 'obj',
        'value': {'param1': 'param1Value', 'param2': 'param2Value'},
    },
]


CONTENT_ITEMS = [
    {
        'content': 'First item wth just text <strong>bold</strong>\n',
        'enabled': True,
    },
    {'content': 'Invisible content\n', 'enabled': False},
    {
        'content': (
            'Second item with variables Number -&nbsp;'
            '<span style=\"color: Coral;\" data-variable=\"number\">'
            '</span>, String - <span style=\"color: Coral;\" '
            'data-variable=\"string\"></span>, Object param - '
            '<span style=\"color: Coral;\" data-variable=\"'
            'obj.param1\">'
            '</span>\n'
        ),
        'enabled': True,
    },
    {
        'content': (
            'Third item with request variable&nbsp;'
            '<span data-request-id=\"5d275bc3eb584657ebbf24b2\" '
            'style=\"color: Coral;\" data-variable=\"'
            'tariff_request.activation_zone\">'
            't</span>\n'
        ),
        'enabled': True,
    },
]


BASE_ITEM1_CONTENT = (
    'BASE ITEM1 <p>Base PARENT_DATA string ['
    '<span data-variable=\"base template parameter1\">'
    '</span>]</p>\n'
    '<p>Base SERVER_DATA string: '
    '<span data-variable=\"req1.num\" '
    'data-request-id='
    '\"5ff4901c583745e089e55bd3\">'
    '</span></p>\n\n'
)

BASE_ITEM2_CONTENT = (
    'BASE ITEM2 <p>Base PARENT_DATA string '
    '[<span data-variable=\"base template parameter2\">'
    '</span>]</p>\n<p>Base '
    'SERVER_DATA string: <span '
    'data-variable=\"req2.r1\" data-request-id='
    '\"5ff4901c583745e089e55bd1\">'
    '</span></p>\n\n'
)

CHILD1_ITEM3_CONTENT = (
    'CHILD1 ITEM3 <p>Child1 PARENT_DATA number '
    '[<span data-variable=\"child1 template '
    'parameter1\">'
    '</span>]</p>\n<p>Child1 '
    'SERVER_DATA string: <span '
    'data-variable=\"req3.home_zone\" data-request-id='
    '\"5d275bc3eb584657ebbf24b2\">'
    '</span></p>\n\n'
)

CHILD2_ITEM3_CONTENT = 'CHILD2 ITEM3 Some text\n\n'

CHILD11_ITEM3_CONTENT = (
    'CHILD11 ITEM3 <p>Child11 PARENT_DATA string '
    '[<span data-variable=\"child11 template parameter1\">'
    '</span>]</p>\n\n'
)

CHILD1_GENERATED_TEXT = (
    'BASE ITEM1 <p>Base PARENT_DATA string [base text]'
    '</p>\n'
    '<p>Base SERVER_DATA string: 10.0</p>\n'
    'CHILD1 ITEM3 <p>Child1 PARENT_DATA number [1]</p>\n'
    '<p>Child1 SERVER_DATA string: moscow</p>\n'
)

ITEM_1_RESPONSE = {
    'id': '1ff4901c583745e089e55ba1',
    'content': BASE_ITEM1_CONTENT,
    'enabled': True,
    'inherited': True,
}

ITEM_2_RESPONSE = {
    'id': '1ff4901c583745e089e55ba2',
    'content': BASE_ITEM2_CONTENT,
    'enabled': False,
    'inherited': True,
}

PARAM_3_RESPONSE = {
    'name': 'child1 template parameter1',
    'description': 'child1 template parameter1 description',
    'type': 'number',
    'enabled': True,
    'inherited': False,
}


def _build_simple_obj_filter(condition: str, value: str, reference_value):
    return {
        'operator': 'AND',
        'filter': {
            'reference_value': reference_value,
            'value': value,
            'condition': condition,
        },
        'conditions': [],
    }


def _build_simple_properties(filter_desc_arr):
    filter_groups = []
    for filter_desc in filter_desc_arr:
        filter_groups.append(
            _build_simple_obj_filter(
                condition=filter_desc.get('condition'),
                value=filter_desc.get('value'),
                reference_value=filter_desc.get('reference_value'),
            ),
        )
    return filter_groups


PROPERTIES_ITEMS_PARAMS = [
    {
        'name': 'obj',
        'value': {'param1': 'param1Value', 'param2': 'param2Value'},
    },
    {
        'name': 'test',
        'value': {'param1': 'test1Value', 'param2': 'test2Value'},
    },
]
LIST_PROPERTIES_ITEMS_PARAMS_IN_TEMPLATE = [{'name': 'arr', 'type': 'array'}]

LIST_PROPERTIES_ITEMS_PARAMS = [
    {
        'name': 'arr',
        'value': [
            {'param1': 'param1Value', 'param2': 'first'},
            {'param1': 'param2Value', 'param2': 'second'},
            {'param1': 'param3Value', 'param2': 'first'},
        ],
    },
]

OBJ_VARIABLE_ITEM_CONTENT = (
    '<p>Object value variable '
    '<span style=\"color: Coral;\" '
    'data-variable=\"obj.param1\">'
    '</span></p>\n'
)

OBJ_VARIABLE_ITERABLE_ITEM_CONTENT = (
    '<p>Object value variable '
    '<span style=\"color: Coral;\" '
    'data-variable=\"#item.param1\">'
    '</span></p>\n'
)


def build_obj_items(groups):
    items = []
    for item in groups:
        content = item.get('content', OBJ_VARIABLE_ITEM_CONTENT)
        filters = item.get('filters')
        params = item.get('params', DEFAULT_PROPERTIES_ITEMS_ITEM_PARAMS)
        items.append(
            {
                'items': [{'content': content, 'enabled': True}],
                'properties': {
                    'filter_groups': _build_simple_properties(filters),
                },
                'params': params,
                'enabled': True,
                'custom_item_id': 'CONDITIONAL',
            },
        )
    return items


DEFAULT_PROPERTIES_ITEMS_ITEM_PARAMS = [
    {
        'name': '#item',
        'type': 'object',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'obj',
    },
]

LIST_PROPERTIES_ITEMS_ITEM_PARAMS = [
    {
        'name': '#items',
        'type': 'array',
        'data_usage': 'PARENT_TEMPLATE_DATA',
        'value': 'arr',
    },
]

LIST_PROPERTIES_ITEMS = [
    {
        'items': [
            {
                'template_id': '5d27219b73f3b64036c0a03a',
                'params': [
                    {
                        'name': 'str',
                        'type': 'string',
                        'data_usage': 'PARENT_TEMPLATE_DATA',
                        'value': '#item.param1',
                    },
                ],
                'enabled': True,
            },
        ],
        'params': LIST_PROPERTIES_ITEMS_ITEM_PARAMS,
        'enabled': True,
        'custom_item_id': 'ITERABLE',
    },
    {
        'items': [
            {'content': OBJ_VARIABLE_ITERABLE_ITEM_CONTENT, 'enabled': True},
        ],
        'params': LIST_PROPERTIES_ITEMS_ITEM_PARAMS,
        'enabled': True,
        'custom_item_id': 'ITERABLE',
    },
    {
        'items': [
            {'content': OBJ_VARIABLE_ITERABLE_ITEM_CONTENT, 'enabled': True},
        ],
        'properties': {
            'filter_groups': [
                {
                    'filter': {
                        'reference_value': '#item.param2',
                        'condition': 'unique',
                    },
                    'conditions': [],
                },
            ],
        },
        'params': LIST_PROPERTIES_ITEMS_ITEM_PARAMS,
        'enabled': True,
        'custom_item_id': 'ITERABLE',
    },
    {
        'items': [
            {
                'items': [
                    {
                        'content': OBJ_VARIABLE_ITERABLE_ITEM_CONTENT,
                        'enabled': True,
                    },
                ],
                'params': LIST_PROPERTIES_ITEMS_ITEM_PARAMS,
                'enabled': True,
                'custom_item_id': 'ITERABLE',
            },
        ],
        'params': [
            {
                'name': '#item',
                'type': 'array',
                'data_usage': 'PARENT_TEMPLATE_DATA',
                'value': 'arr',
            },
        ],
        'enabled': True,
        'custom_item_id': 'CONDITIONAL',
        'properties': {
            'filter_groups': [
                {
                    'filter': {
                        'reference_value': '#item',
                        'condition': 'not_empty',
                    },
                    'conditions': [],
                },
            ],
        },
    },
]

PROPERTIES_ITEMS = build_obj_items(
    [
        {
            'filters': [
                {
                    'condition': 'equal',
                    'value': 'test',
                    'reference_value': '#item.param1',
                },
            ],
        },
        {
            'filters': [
                {
                    'condition': 'equal',
                    'value': 'param2Value',
                    'reference_value': '#item.param2',
                },
            ],
        },
        {
            'filters': [
                {
                    'condition': 'not_equal',
                    'value': 'test',
                    'reference_value': '#item.param1',
                },
            ],
        },
        {
            'filters': [
                {
                    'condition': 'equal',
                    'value': 'test1Value',
                    'reference_value': '#item.param1',
                },
            ],
            'params': [
                {
                    'name': '#item',
                    'type': 'object',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    'value': 'test',
                },
            ],
            'content': (
                '<p>Object value variable '
                '<span style=\"color: Coral;\" '
                'data-variable=\"test.param1\">'
                '</span></p>\n'
            ),
        },
        {
            'filters': [
                {'condition': 'not_empty', 'reference_value': '#item.param3'},
            ],
            'content': (
                '<p>Object value variable '
                '<span style=\"color: Coral;\" '
                'data-variable=\"obj.param3\"></span></p>\n'
            ),
        },
        {
            'filters': [
                {'condition': 'empty', 'reference_value': '#item.param3'},
            ],
            'content': (
                '<p>Object value variable '
                '<span style=\"color: Coral;\" '
                'data-variable=\"obj.param2\"></span></p>\n'
            ),
            'params': [
                {
                    'name': '#item',
                    'type': 'object',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    'value': 'obj',
                },
            ],
        },
        {
            'filters': [
                {'condition': 'not_empty', 'reference_value': '#item.param1'},
            ],
            'content': (
                '<p>Object value variable '
                '<span style=\"color: Coral;\" '
                'data-variable=\"obj.param2\"></span></p>\n'
            ),
            'params': [
                {
                    'name': '#item',
                    'type': 'object',
                    'data_usage': 'PARENT_TEMPLATE_DATA',
                    'value': 'obj',
                },
            ],
        },
    ],
)

GENERATED_CONTENT_PROPERTIES_ITEMS = (
    '<p>Object value variable param1Value</p>\n'
    '<p>Object value variable param1Value</p>\n'
    '<p>Object value variable test1Value</p>\n'
    '<p>Object value variable param2Value</p>\n'
    '<p>Object value variable param2Value</p>\n'
)

GENERATED_CONTENT_NESTED_ITEMS = (
    'Simple text and resolved parent template parameter&nbsp;param1Value'
    'Simple text and resolved parent template parameter&nbsp;param2Value'
    'Simple text and resolved parent template parameter&nbsp;param3Value'
    '<p>Object value variable param1Value</p>\n'
    '<p>Object value variable param2Value</p>\n'
    '<p>Object value variable param3Value</p>\n'
    '<p>Object value variable param1Value</p>\n'
    '<p>Object value variable param2Value</p>\n'
    '<p>Object value variable param1Value</p>\n'
    '<p>Object value variable param2Value</p>\n'
    '<p>Object value variable param3Value</p>\n'
)

DOCUMENT_TEMPLATOR_REQUESTS = {
    'Tariff': {
        'method': 'POST',
        'url_pattern': '$mockserver/tariff/{zone}/{tariff}/',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    'Surge': {
        'method': 'GET',
        'url_pattern': '$mockserver/get_surge/',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    'Text': {
        'method': 'GET',
        'url_pattern': '$mockserver/pinstats/',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    'Second tariff': {
        'method': 'GET',
        'url_pattern': '$mockserver/tariff/{zone}',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
    'Double number': {
        'method': 'GET',
        'url_pattern': '$mockserver/double-number/',
        'timeout_in_ms': 100,
        'retries_count': 3,
    },
}
REQUEST_CONFIG = {'DOCUMENT_TEMPLATOR_REQUESTS': DOCUMENT_TEMPLATOR_REQUESTS}

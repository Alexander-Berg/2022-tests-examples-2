import pytest


async def test_get_suggests(web_app_client, web_context):
    filters = web_context.service_schemas.schemas['filters']['filters']
    suggests = [x['suggest_from'] for x in filters if 'suggest_from' in x]

    for name in suggests:
        response = await web_app_client.get(f'/v2/suggest/{name}/')
        assert response.status == 200


@pytest.mark.parametrize(
    'name,params,expected',
    [
        (
            'log_types',
            {},
            [
                {'value': 'some', 'label': 'some'},
                {'value': 'more', 'label': 'more'},
            ],
        ),
        ('log_types', {'limit': 1}, [{'value': 'more', 'label': 'more'}]),
        ('log_types', {'offset': 1}, [{'value': 'some', 'label': 'some'}]),
        (
            'stq_task_names',
            {},
            [
                {'value': 'send_report', 'label': 'send_report'},
                {
                    'value': 'processing_iteration',
                    'label': 'processing_iteration',
                },
            ],
        ),
        ('log_types', {'pattern': 'so'}, [{'value': 'some', 'label': 'some'}]),
        (
            'log_types',
            {'pattern': 'so*'},
            [{'value': 'some', 'label': 'some'}],
        ),
        (
            'log_types',
            {'pattern': 's*e'},
            [{'value': 'some', 'label': 'some'}],
        ),
        (
            'log_types',
            {'pattern': 'm'},
            [
                {'value': 'some', 'label': 'some'},
                {'value': 'more', 'label': 'more'},
            ],
        ),
        (
            'log_types',
            {'pattern': '*m*'},
            [
                {'value': 'some', 'label': 'some'},
                {'value': 'more', 'label': 'more'},
            ],
        ),
        ('log_types', {'pattern': '*a*'}, []),
        (
            'stq_task_names',
            {'pattern': 'SEND'},
            [{'value': 'send_report', 'label': 'send_report'}],
        ),
        (
            'tvm_source_names',
            {'pattern': 'tk'},
            [
                {'value': 'utka', 'label': 'utka'},
                {'value': 'utkanos', 'label': 'utkanos'},
            ],
        ),
        (
            'tvm_source_names',
            {'pattern': 'TK', 'limit': 1},
            [{'value': 'utka', 'label': 'utka'}],
        ),
        (
            'tvm_source_names',
            {'offset': 2, 'limit': 1},
            [{'value': 'tvm', 'label': 'tvm'}],
        ),
    ],
)
@pytest.mark.config(TVM_SERVICES={'utka': 111, 'utKAnos': 222, 'tVM': 333})
async def test_suggests(web_app_client, name, params, expected):
    response = await web_app_client.get(f'/v2/suggest/{name}/', params=params)
    assert response.status == 200
    data = await response.json()
    assert sorted(data['suggests'], key=str) == sorted(expected, key=str)

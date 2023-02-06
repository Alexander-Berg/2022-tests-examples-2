import pytest

CONFIG = {
    'example-replica': {
        'incremental_merge_time_limit_ms': 5000,
        'max_x_polling_delay_ms': 10,
        'min_x_polling_delay_ms': 0,
        'max_answer_data_size_bytes': 250,
        'updates_max_documents_count': 10,
        'is_dumper_enabled': False,
        'deleted_documents_ttl_seconds': 4294967294,
        'lagging_cursor_delay_seconds': 120,
    },
}


def deep_get(dictionary, keys):
    for key in keys:
        dictionary = dictionary.get(key)
    return dictionary


def deep_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def make_projection(doc, projection):
    result = {}
    for composite_field in projection:
        fields = composite_field.split('.')
        deep_set(result, fields, deep_get(doc, fields))
    return result


@pytest.mark.config(API_OVER_DATA_SERVICES=CONFIG)
async def test_examples_client(taxi_example_replica, mockserver):
    data = [
        {
            'example_id': 'example_1',
            'data': {
                'example_additional_field': 'example_1_additional_field',
                'example_main_field': 'example_1_main_field',
                'example_object_type_field': {'bool_field': True},
            },
        },
        {
            'example_id': 'example_2',
            'data': {
                'example_main_field': 'example_2_main_field',
                'example_object_type_field': {'bool_field': True},
            },
        },
    ]
    data_dict = {elem['example_id']: elem for elem in data}

    def _mock_common_retrieve(request):
        resp_array = []
        projection = request.json.get('projection')
        for id_ in request.json['id_in_set']:
            if id_ in data_dict:
                if projection:
                    doc = make_projection(data_dict[id_], projection)
                    doc['example_id'] = data_dict[id_]['example_id']
                else:
                    doc = data_dict[id_]
                resp_array.append(doc)
            else:
                resp_array.append({'example_id': id_})
        resp_json = {'examples': resp_array}
        return resp_json

    @mockserver.json_handler('/example-replica/v1/examples/proxy_retrieve')
    def _mock_proxy_retrieve(request):
        return _mock_common_retrieve(request)

    @mockserver.json_handler('/example-replica/v1/examples/retrieve')
    def _mock_retrieve(request):
        return _mock_common_retrieve(request)

    data_by_index = {
        'examples_by_main': [
            {
                'main_field': 'example_1_main_field',
                'examples': [
                    {
                        'example_id': 'example_1',
                        'revision': '0_1234567_1',
                        'data': {
                            'example_additional_field': (
                                'example_1_additional_field'
                            ),
                            'example_main_field': 'example_1_main_field',
                            'example_object_type_field': {'bool_field': True},
                        },
                    },
                ],
            },
            {'examples': [], 'main_field': 'unknown'},
        ],
    }

    @mockserver.json_handler('/example-replica/v1/examples/retrieve_by_main')
    def _mock_retrieve_by_index(request):
        return data_by_index

    response = await taxi_example_replica.get('v1/client/test')
    # actual tests are in
    # services/example-replica/src/views/v1/client/test/get/view.cpp
    # if this test fails,
    # make testsuite-example-replica 2>&1 | grep  'Assertion'
    # to find which assertion failed
    assert response.status_code == 200

import pytest


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'request_name',
    (
        'full_query',
        'full_query_english',
        'long_period',
        'without_period',
        'without_personal_data',
        'user_not_found',
    ),
)
@pytest.mark.now('2021-03-03T03:10:00+03:00')
async def test_v1_leads_csv(
        tvm_client,
        mockserver,
        taxi_hiring_partners_app_web,
        load_json,
        request_name,
        taxi_config,
):
    test_setting = load_json('requests.json')[request_name]

    @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
    async def leads(_request):  # pylint: disable=W0621,W0612
        assert _request.headers['X-Consumer-Id'] == tvm_client.service_name
        check_query_dict_equality(
            test_setting['CANDIDATES_REQUEST'], _request.json,
        )
        return load_json('candidates_response.json')['default']

    async def make_request(data=None, headers=None, status=None):
        _response = await taxi_hiring_partners_app_web.post(
            '/v1/leads/csv', json=data, headers=headers,
        )
        assert _response.status == status
        return _response

    request = test_setting['REQUEST']
    response = await make_request(**request)
    assert response

    if response.status == 200:
        text = await response.text()

        assert (
            text == 'name,phone,vacancy\r\nКукин Олег Евгеньевич,,Driver\r\n'
        )
        config = taxi_config.get('HIRING_PARTNERS_APP_CSV_FIELDS')
        expected_fields = config['__default__']['roles'][0]['fields']
        headers = text.split('\n')[0]
        csv_fields = headers.strip().split(',')
        assert csv_fields == expected_fields


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.now('2021-03-03T03:10:00+03:00')
async def test_v1_leads_csv_custom_consumer(
        tvm_client,
        mockserver,
        taxi_hiring_partners_app_web,
        load_json,
        taxi_config,
):
    """
    Test that correct consumer is used and status is converted
    when eats permission flag is set.
    """
    # arrange
    test_setting = load_json('requests.json')['full_query']
    request = test_setting['REQUEST']

    @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
    def leads_mock(_request):
        return load_json('candidates_response.json')['eats']

    @mockserver.json_handler('/experiments3/v1/configs')
    def mock_config3(_request):
        return load_json('config3.json')

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/leads/csv', json=request['data'], headers=request['headers'],
    )

    # assert
    assert mock_config3.has_calls
    assert leads_mock.has_calls
    call_request = leads_mock.next_call()['_request']
    assert call_request.headers['X-Consumer-Id'] == 'hiring-partners-app/eats'
    check_query_dict_equality(
        test_setting['CANDIDATES_REQUEST'], call_request.json,
    )

    assert response.status == 200
    text = await response.text()
    assert text == (
        'name,status,channel\r\nЕдовый Александр Дмитрьевич,'
        'Created,freelance\r\n'
    )

    config = taxi_config.get('HIRING_PARTNERS_APP_CSV_FIELDS')
    expected_fields = config['__default__']['roles'][0]['fields']
    headers = text.split('\n')[0]
    csv_fields = headers.strip().split(',')
    assert csv_fields == expected_fields


def check_query_dict_equality(target, actual):
    def _sort_lists_in_query(dict_):
        for value in dict_.values():
            if isinstance(value, list):
                value.sort()

    _sort_lists_in_query(target)
    _sort_lists_in_query(actual)
    assert target == actual

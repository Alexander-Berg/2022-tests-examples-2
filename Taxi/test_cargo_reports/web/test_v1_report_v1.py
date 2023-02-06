import copy


import pytest

CORP_CLIENT_ID = '00144b4a9ec44ca383ae3ed8ec4a230d'

YT_TABLE_PATH = '//home/unittests/unittests/services/cargo-reports/raw_reports'
YT_TABLE_DATA = [
    {
        'corp_client_id': CORP_CLIENT_ID,
        'updated_ts': 1603098627.691193,
        'uuid_id': 'e238265a8cdd4179b9505861c8719946',
        'final_price_without_vat': 2353000000,
        'distance_km': 13.13,
        'russian_text': 'привет, мир',
        'column_with_newline': 'foo\nbar',
        'created_date': '2020-10-19',
        'created_time': '12:10:27',
        'finished_date': '2020-10-19',
        'finished_time': '13:10:27',
        'finished_weekday': 2,
        'departure_time': '12:10:27',
        'arrival_time': '13:10:27',
        'dest_point_visited_time': '13:10:27',
    },
    {
        'corp_client_id': CORP_CLIENT_ID,
        'updated_ts': 1606833958.111,  # border date
        'uuid_id': 'e850d77875b94abd995e9ea20da56a32',
        'final_price_without_vat': 2210000000,
        'distance_km': 13.00,
        'russian_text': '',
        'column_with_newline': 'foo\nbar',
        'created_date': '2020-12-01',
        'created_time': '22:45:58',
        'finished_date': '2020-12-01',
        'finished_time': '23:45:58',
        'finished_weekday': 3,
        'departure_time': '22:45:58',
        'arrival_time': '23:45:58',
        'dest_point_visited_time': '23:40:58;;23:45:58',
    },
    {
        'corp_client_id': CORP_CLIENT_ID,
        'updated_ts': 1606920358.000,  # bad date
        'uuid_id': 'e850d77875b94abd995e9ea20da56a32',
        'final_price_without_vat': 2210000000,
        'distance_km': 13.00,
        'russian_text': '',
        'column_with_newline': 'foo\nbar',
    },
    {
        'corp_client_id': '10144b4a9ec44ca383ae3ed8ec4a230d',
        'updated_ts': 1603277035.542231,
        'uuid_id': 'e850d77875b94abd995e9ea20da56a33',
        'final_price_without_vat': 2210000000,
        'distance_km': 14.23443,
        'russian_text': 'привет, мир',
        'column_with_newline': 'foo\nbar',
    },
]

FIELD_NAMES = [
    'updated_ts',
    'uuid_id',
    'final_price_without_vat',
    'fake_column_name',
    'column_with_newline',
    'distance_km',
    'russian_text',
]

EXPECTED_RESULT = (
    '\ufeff' + '\t'.join(FIELD_NAMES) + '\r\n'
    '1603098627.691193\t'
    'e238265a8cdd4179b9505861c8719946\t2353000000\t'
    '\t"foo\nbar"\t13,13\tпривет, мир\r\n'
    '1606833958.111\t'
    'e850d77875b94abd995e9ea20da56a32\t'
    '2210000000\t\t"foo\nbar"\t13,0\t\r\n'
)

FIELDS_WITH_TIME = [
    'created_date_utc',
    'created_time_utc',
    'created_date',
    'created_time',
    'finished_date',
    'finished_time',
    'finished_weekday',
    'departure_time',
    'arrival_time',
    'dest_point_visited_time',
]


def get_request_headers(corp_client_id=CORP_CLIENT_ID):
    return {
        'X-B2B-Client-Id': corp_client_id,
        'Accept-Language': 'ru-RU',
        'X-Yandex-Login': 'me',
        'X-Yandex-Uid': '05780',
    }


@pytest.fixture(name='create_table_with_schema')
def _create_table_with_schema(yt_client, load_json):
    yt_client.create_table(
        YT_TABLE_PATH,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': load_json('raw_report_v1_schema.json'),
        },
    )


@pytest.fixture(name='call_v1_report')
def _call_v1_report(taxi_cargo_reports_web):
    async def _call(json=None, corp_client_id=CORP_CLIENT_ID):
        if json is None:
            json = {'since_date': '2020-10-01', 'till_date': '2020-12-01'}
        response = await taxi_cargo_reports_web.post(
            '/v1/report',
            json=json,
            headers=get_request_headers(corp_client_id=corp_client_id),
        )
        return response

    return _call


@pytest.fixture(name='mock_v1_clients')
def _mock_v1_clients(mockserver):
    @mockserver.json_handler('/corp-clients/v1/clients')
    def _get_contracts_handler(request):
        assert request.query['client_id'] == CORP_CLIENT_ID
        assert request.query['fields'] == 'country'
        return mockserver.make_response(
            status=200, json={'id': 'id', 'country': 'norway'},
        )


@pytest.fixture(autouse=True)
def taxi_cargo_reports_mocks(mockserver):
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_cargo_reports_mocks')
@pytest.mark.config(
    CARGO_REPORTS_REPORT_HANDLER_SETTINGS={
        'field_names': FIELD_NAMES,
        'chunk_size': 10000,
    },
)
async def test_report_bad(
        call_v1_report, yt_apply, yt_client, mock_v1_clients,
):
    response = await call_v1_report(
        json={'since_date': '2020-10-01'}, corp_client_id='123',
    )
    assert response.status == 400  # wrong X-B2B-Client-Id length

    response = await call_v1_report(json={'since_date': '2020-10-01'})
    assert response.status == 404  # no report table data for CORP_CLIENT_ID


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_cargo_reports_mocks')
@pytest.mark.parametrize(
    ('field_names', 'expected_result'),
    [
        pytest.param(FIELD_NAMES, EXPECTED_RESULT, id='simple'),
        pytest.param(
            FIELDS_WITH_TIME,
            (
                '\ufeff' + '\t'.join(FIELDS_WITH_TIME) + '\r\n'
                '2020-10-19\t12:10:27\t2020-10-19\t15:10:27\t'
                '2020-10-19\t16:10:27\t'
                'Понедельник\t15:10:27\t16:10:27\t16:10:27\r\n'
                '2020-12-01\t22:45:58\t2020-12-02\t01:45:58\t'
                '2020-12-02\t02:45:58\t'
                'Среда\t01:45:58\t02:45:58\t02:40:58;;02:45:58\r\n'
            ),
            id='check timezones',
        ),
    ],
)
@pytest.mark.translations(
    cargo={
        'report.sunday': {'ru': 'Воскресенье'},
        'report.monday': {'ru': 'Понедельник'},
        'report.tuesday': {'ru': 'Вторник'},
        'report.wednesday': {'ru': 'Среда'},
        'report.thursday': {'ru': 'Четверг'},
        'report.friday': {'ru': 'Пятница'},
        'report.saturday': {'ru': 'Суббота'},
    },
)
async def test_report_ok(
        call_v1_report,
        yt_apply,
        yt_client,
        taxi_config,
        create_table_with_schema,
        field_names,
        expected_result,
        mock_v1_clients,
):
    taxi_config.set_values(
        {
            'CARGO_REPORTS_REPORT_HANDLER_SETTINGS': {
                'field_names': field_names,
                'chunk_size': 10000,
            },
        },
    )
    yt_client.write_table(YT_TABLE_PATH, YT_TABLE_DATA)
    response = await call_v1_report()
    assert response.status == 200
    result = await response.text()
    assert result == expected_result


def _gen_big_reports(amount):
    report = copy.deepcopy(YT_TABLE_DATA[0])
    report['column_with_newline'] = 'Lorem ipsum' * 20 + '\n' + 'Lorem ipsum'
    return [report.copy() for _ in range(amount)]


@pytest.mark.servicetest
@pytest.mark.parametrize('data_size', [1000, 5000, 10005, 20005])
@pytest.mark.config(
    CARGO_REPORTS_REPORT_HANDLER_SETTINGS={
        'field_names': FIELD_NAMES,
        'chunk_size': 10000,
    },
)
@pytest.mark.usefixtures('taxi_cargo_reports_mocks')
async def test_big_data(
        call_v1_report,
        yt_apply,
        yt_client,
        create_table_with_schema,
        data_size,
        mock_v1_clients,
):
    yt_client.write_table(YT_TABLE_PATH, _gen_big_reports(data_size))
    response = await call_v1_report()
    assert response.status == 200
    result = await response.text()
    assert result.count(YT_TABLE_DATA[0]['uuid_id']) == data_size


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_cargo_reports_mocks')
@pytest.mark.translations(
    cargo={
        'report.sunday': {'ru': 'Воскресенье'},
        'report.monday': {'ru': 'Понедельник'},
        'report.tuesday': {'ru': 'Вторник'},
        'report.wednesday': {'ru': 'Среда'},
        'report.thursday': {'ru': 'Четверг'},
        'report.friday': {'ru': 'Пятница'},
        'report.saturday': {'ru': 'Суббота'},
    },
)
@pytest.mark.client_experiments3(
    consumer='cargo-reports/make_report',
    config_name='cargo_reports_report_settings',
    args=[
        {'name': 'corp_client_id', 'type': 'string', 'value': CORP_CLIENT_ID},
        {'name': 'country', 'type': 'string', 'value': 'norway'},
        {'name': 'api_version', 'type': 'string', 'value': '__admin__'},
    ],
    value={'field_names': FIELD_NAMES, 'chunk_size': 10000},
)
@pytest.mark.config(
    CARGO_REPORTS_REPORT_SETTINGS={
        'default_report_version': 'v1',
        'default_chunk_size': 10000,
    },
)
async def test_report_exp3(
        call_v1_report,
        yt_apply,
        yt_client,
        create_table_with_schema,
        mock_v1_clients,
):
    yt_client.write_table(YT_TABLE_PATH, YT_TABLE_DATA)
    response = await call_v1_report()
    result = await response.text()
    assert response.status == 200, result
    assert result == EXPECTED_RESULT

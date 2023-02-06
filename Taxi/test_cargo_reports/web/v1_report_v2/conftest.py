import pytest

CORP_CLIENT_ID = '00144b4a9ec44ca383ae3ed8ec4a230d'

YT_TABLE_PATH = (
    '//home/unittests/unittests/services/cargo-reports/raw_reports_v2'
)

YT_TARIFFS_TABLE_PATH = (
    '//home/unittests/unittests/services/cargo-reports/raw_report_tariffs_v2'
)


@pytest.fixture(name='create_raw_table_with_names')
def _create_raw_table_with_names(yt_client, load_json):
    def _create(raw_report_table_name, raw_tariffs_table_name):
        yt_client.create_table(
            raw_report_table_name,
            ignore_existing=True,
            recursive=True,
            attributes={
                'dynamic': False,
                'optimize_for': 'scan',
                'schema': load_json('raw_report_v2_schema.json'),
            },
        )
        yt_client.create_table(
            raw_tariffs_table_name,
            ignore_existing=True,
            recursive=True,
            attributes={
                'dynamic': False,
                'optimize_for': 'scan',
                'schema': load_json('raw_report_tariffs_v2_schema.json'),
            },
        )

    return _create


@pytest.fixture(name='call_v1_report')
def _call_v1_report(taxi_cargo_reports_web):
    async def _call(json=None, corp_client_id=CORP_CLIENT_ID):
        if json is None:
            json = {'since_date': '2020-10-01', 'till_date': '2020-12-01'}
        response = await taxi_cargo_reports_web.post(
            '/v1/report',
            json=json,
            headers={
                'X-B2B-Client-Id': corp_client_id,
                'Accept-Language': 'ru-RU',
                'X-Yandex-Login': 'me',
                'X-Yandex-Uid': '05780',
            },
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


@pytest.fixture(name='lazy_exp_report_settings')
def _lazy_exp_report_settings(client_experiments3, taxi_cargo_reports_web):
    async def _call(field_names, country='norway'):
        client_experiments3.add_record(
            consumer='cargo-reports/make_report',
            config_name='cargo_reports_report_settings',
            args=[
                {
                    'name': 'corp_client_id',
                    'type': 'string',
                    'value': CORP_CLIENT_ID,
                },
                {'name': 'country', 'type': 'string', 'value': country},
                {
                    'name': 'api_version',
                    'type': 'string',
                    'value': '__admin__',
                },
            ],
            value={'field_names': field_names},
        )
        await taxi_cargo_reports_web.invalidate_caches()

    return _call


@pytest.fixture(name='cfg_cargo_reports_report_settings')
def _cfg_cargo_reports_report_settings(taxi_config):
    taxi_config.set_values(
        {
            'CARGO_REPORTS_REPORT_SETTINGS': {
                'default_report_version': 'v2',
                'default_chunk_size': 10000,
            },
        },
    )


@pytest.fixture(name='call_v1_report_v2')
def _call_v1_report_v2(call_v1_report, cfg_cargo_reports_report_settings):
    async def _call(json=None, corp_client_id=CORP_CLIENT_ID):
        result = await call_v1_report(json=json, corp_client_id=corp_client_id)
        return result

    return _call


@pytest.fixture(name='write_yt_tables_data')
def _write_yt_tables_data(yt_client, load_json):
    def _call(
            raw_report_table_path=YT_TABLE_PATH,
            raw_tariffs_table_path=YT_TARIFFS_TABLE_PATH,
    ):
        yt_client.write_table(
            raw_report_table_path, load_json('raw_report_v2_data.json'),
        )
        yt_client.write_table(
            raw_tariffs_table_path,
            load_json('raw_report_tariffs_v2_data.json'),
        )

    return _call


@pytest.fixture(name='create_yt_tables_with_data')
def _create_yt_tables_with_data(
        create_raw_table_with_names, write_yt_tables_data,
):
    create_raw_table_with_names(
        raw_report_table_name=YT_TABLE_PATH,
        raw_tariffs_table_name=YT_TARIFFS_TABLE_PATH,
    )
    write_yt_tables_data()


@pytest.fixture(name='lazy_cfg_v2_report_extractors')
def _lazy_cfg_v2_report_extractors(taxi_config, taxi_cargo_reports_web):
    async def _call(json):
        taxi_config.set_values(
            {'CARGO_REPORTS_V2_REPORT_DATA_EXTRACTORS': json},
        )
        await taxi_cargo_reports_web.invalidate_caches()

    return _call


def parse_tsv(raw_result):
    raw_result = raw_result.replace('\ufeff', '')
    result = []
    for row in raw_result.splitlines():
        result.append(row.split('\t'))
    return result

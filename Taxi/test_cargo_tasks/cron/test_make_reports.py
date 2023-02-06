# pylint: disable=redefined-outer-name
import pytest

from cargo_tasks.generated.cron import run_cron

FIELD_NAMES = [
    'updated_ts',
    'uuid_id',
    'final_price_without_vat',
    'fake_column_name',
    'column_with_newline',
    'distance_km',
    'russian_text',
]

EXPECTED_ROW = {
    'finished_ts': '13:21:12',
    'boarding_price': 0.0,
    'cargo_loaders': None,
    'cargo_type': None,
    'city': 'Санкт-Петербург',
    'order_comment': None,
    'corp_client_id': '00129f6d3d814fb3a1d7fb263d71dcd3',
    'created_date': '2020-06-02',
    'created_time': '12:12:44',
    'dest_point_address': (
        'Россия, Санкт-Петербург, '
        'Большая Подьяческая улица, 22;Россия, '
        'Санкт-Петербург, Большая Подьяческая улица, 22'
    ),
    'dest_point_comment': None,
    'dest_point_coordinates': '59.923279,30.305789;59.923279,30.305789',
    'declared_price': '0;0',
    'external_order_id': '№ 202006-112;№ 202006-112',
    'has_payment': 'false;false',
    'dest_point_phone': (
        'ca20ba99d3ad4e5497731761dc67ed90;ca20ba99d3ad4e5497731761dc67ed90'
    ),
    'dest_point_status': 'visited;visited',
    'dest_point_visited_time': '13:20:58;13:20:58',
    'size': None,
    'weight': None,
    'vat_price': 529.2,
    'no_vat_price': 441.0,
    'payment_sum': None,
    'finished_date': '2020-06-02',
    'finished_weekday': 2,
    'finished_time': '13:21:12',
    'calculated_price': 480.0,
    'paid_waiting_in_destination_total_price': 0.0,
    'paid_waiting_total_price': 0.0,
    'pickup_arroved_time': '12:24:36',
    'departure_time': '12:29:37;12:29:37',
    'source_point_address': (
        'Россия, Санкт-Петербург, Коломяжский проспект, 10А'
    ),
    'source_point_comment': None,
    'source_point_coordinates': '59.99365313,30.29858452',
    'source_point_email': 'fd097e5978714ffeafc1cdfd54876490',
    'source_point_phone': 'a4bb4117d1a4492d897e6d0a49a03e75',
    'claim_status': 'delivered_finish',
    'tariff': 'express',
    'total_distance_price': 0.0,
    'total_surge_price': 0.0,
    'total_time_price': 0.0,
    'last_status_change_ts': 1591781111.314135,
    'uuid': '63250f1f52064e4889d5107d07d3d79a',
    'order_login': 'kmstil40521',
}


@pytest.fixture
def patch_yql(patch, load_json, mockserver):
    class YqlSqlOperationRequest:
        def run(self):
            pass

        @property
        def web_url(self):
            return 'mocked_web_url'

        @property
        def share_url(self):
            return 'mocked_share_url'

        @property
        def status(self):
            return 'COMPLETED'

        @property
        def operation_id(self):
            return 'operation_id'

    # pylint: disable=unused-variable
    @patch('yql.api.v1.client.YqlClient.query')
    def patch_yql_query(*args, **kwargs):
        return YqlSqlOperationRequest()

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlSqlOperationRequest')
    def patch_operation_request(*args, **kwargs):
        return YqlSqlOperationRequest()

    # pylint: disable=unused-variable
    @patch('yql.client.operation.YqlOperationStatusRequest')
    def patch_status_request(*args, **kwargs):
        return YqlSqlOperationRequest()


@pytest.mark.config(
    CARGO_TASKS_REPORTS_JOB_SETTINGS={
        'parallel_queries': 50,
        'chunk_size': 100000,
    },
)
async def test_make_reports_v1(yt_apply, yt_client, patch_yql, load_json):
    table = '//home/unittests/unittests/services/cargo-reports/raw_reports_tmp'
    yt_client.create_table(
        table,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': load_json('schema.json'),
        },
    )
    yt_client.write_table(table, load_json('test_reports.json'))
    await run_cron.main(['cargo_tasks.crontasks.make_reports', '-t', '0'])
    assert 'raw_reports' in set(
        yt_client.list('//home/unittests/unittests/services/cargo-reports'),
    )
    result_table_name = (
        '//home/unittests/unittests/services/cargo-reports/' 'raw_reports'
    )
    assert next(yt_client.read_table(result_table_name)) == EXPECTED_ROW

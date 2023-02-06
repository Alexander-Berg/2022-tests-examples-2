# pylint: disable=redefined-outer-name
import pytest

from cargo_tasks.generated.cron import run_cron

EXPECTED_ROW = {
    'contract_eid': '12345/12',
    'order_id': None,
    'claim_id': 'aae1f5fd10a945db848236120a15473f',
    'city': 'Екатеринбург',
    'status': 'delivered_finish',
    'created_date': '2021-10-06',
    'source_point_address': 'Екатеринбург, ул. Хохрякова, д. 63',
    'dest_point_address': 'Екатеринбург улица Черепанова 24',
    'tariff': 'courier',
    'external_order_id': '10348059',
    'vat_price': 10.8,
    'no_vat_price': 10.3,
}

TABLE_DIR = '//home/unittests/unittests/services/cargo-tasks/detalizations'


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
    CARGO_TASKS_ACTS_DETALIZATIONS_SETTINGS={
        'enabled': True,
        'tables_limit': 2,
        'acts_table': (
            '//home/taxi-internal-control/external-data'
            '/decomposition/acts/{month}'
        ),
        'tariffs': ['cargo', 'cargocorp', 'courier', 'express'],
    },
)
@pytest.mark.now('2021-09-07T05:00:00+00:00')
async def test_make_detalizations(yt_apply, yt_client, patch_yql, load_json):
    month_to_make = '2021-08'  # table should appear
    preceding_month = '2021-07'  # table should remain
    old_months = ('2021-06', '2021-05')  # tables should be removed
    bad_table_name = 'non-month-like-name'  # to check exception handling
    table_schema = load_json('schema.json')

    for month in [*old_months, preceding_month, bad_table_name]:
        create_table(yt_client, table_schema, f'{TABLE_DIR}/{month}')

    tmp_table_name = f'{TABLE_DIR}/{month_to_make}_tmp'
    create_table(yt_client, table_schema, tmp_table_name)
    yt_client.write_table(tmp_table_name, load_json('test_detalizations.json'))

    await run_cron.main(
        ['cargo_tasks.crontasks.make_detalizations', '-t', '0'],
    )
    assert set(yt_client.list(TABLE_DIR)) == {
        month_to_make,
        preceding_month,
        bad_table_name,
    }

    result_table_name = f'{TABLE_DIR}/{month_to_make}'
    assert next(yt_client.read_table(result_table_name)) == EXPECTED_ROW


def create_table(yt_client, schema, table_name):
    yt_client.create_table(
        table_name,
        ignore_existing=True,
        recursive=True,
        attributes={
            'dynamic': False,
            'optimize_for': 'scan',
            'schema': schema,
        },
    )

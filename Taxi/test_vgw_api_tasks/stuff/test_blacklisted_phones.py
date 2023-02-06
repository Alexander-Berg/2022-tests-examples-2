import pytest

from vgw_api_tasks.generated.cron import run_cron


@pytest.fixture()
def common_fixtures(mockserver, patch, patch_aiohttp_session, response_mock):
    @patch('taxi.clients.taxi_exp.TaxiExpClient')
    def _experiments(*args, **kwargs):
        class Experiments:
            async def load_file(
                    self, data, file_name, experiment_name, transform,
            ):
                return {'id': 'new_file'}

            async def get_exp(self, experiment_name):
                return {
                    'last_modified_at': 100,
                    'clauses': [
                        {
                            'query': 'query',
                            'predicate': {
                                'type': 'in_file',
                                'init': {'file': 'old_file'},
                            },
                        },
                    ],
                }

            async def update_exp(self, *args, **kwargs):
                pass

        return Experiments()

    @patch('taxi.util.cleaners.clean_international_phones')
    async def _cleaners(phones, *args, **kwargs):
        return phones


@pytest.fixture
def _patch_yql_operations(patch):
    @patch('yql.api.v1.client.YqlClient')
    def _yql_client(*args, **kwargs):
        class YqlClient:
            class YQLRequest:
                _operation_id = 'test_operation_id'
                json = {}

                @classmethod
                def run(cls):
                    pass

                @property
                def operation_id(self):
                    return self._operation_id

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

            def query(self, *args, **kwarg):
                return self.YQLRequest()

        return YqlClient()

    @patch('yql.client.operation.YqlOperationStatusRequest')
    def _yql_operation_status_request(operation_id):
        class YQLRequest:
            status = 'COMPLETED'
            json = {}

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlAbortOperationRequest')
    def _yql_operation_abort_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationShareIdRequest')
    def _yql_operation_share_id_request(op_id):
        class YQLRequest:
            json = 'public_link'

            def run(self):
                pass

        return YQLRequest()

    @patch('yql.client.operation.YqlOperationResultsRequest')
    def _yql_operation_results_request(operation_id):
        class YQLRequest:
            json = {}

            def run(self):
                pass

            def get_results(self):
                class Result:
                    def __init__(self, phones):
                        self.rows = [
                            {'PhoneNumber': phone} for phone in phones
                        ]
                        self.column_names = ['PhoneNumber']

                    def fetch_full_data(self):
                        return self.rows

                return [Result(['+79166173068'])]

        return YQLRequest()


@pytest.mark.usefixtures('_patch_yql_operations')
@pytest.mark.usefixtures('common_fixtures')
async def test_insert(pgsql):
    await run_cron.main(
        ['vgw_api_tasks.stuff.update_blacklisted_phones', '-t', '0'],
    )

    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        'file_id, phones_hash, phones_count, clean_phones_count '
        'FROM vgw_api.blacklisted_meta;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == 'new_file'
    assert row[2] == 1
    assert row[3] == 1


@pytest.mark.usefixtures('_patch_yql_operations')
@pytest.mark.usefixtures('common_fixtures')
@pytest.mark.pgsql('vgw_api', files=('blacklisted_meta.sql',))
async def test_update(pgsql):
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        'file_id, phones_hash, phones_count, clean_phones_count '
        'FROM vgw_api.blacklisted_meta;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == 'old_file'

    await run_cron.main(
        ['vgw_api_tasks.stuff.update_blacklisted_phones', '-t', '0'],
    )
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        'file_id, phones_hash, phones_count, clean_phones_count '
        'FROM vgw_api.blacklisted_meta;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == 'new_file'
    assert row[2] == 1
    assert row[3] == 1


@pytest.mark.usefixtures('_patch_yql_operations')
@pytest.mark.usefixtures('common_fixtures')
@pytest.mark.pgsql('vgw_api', files=('blacklisted_meta_hash.sql',))
async def test_not_update(pgsql):
    await run_cron.main(
        ['vgw_api_tasks.stuff.update_blacklisted_phones', '-t', '0'],
    )
    cursor = pgsql['vgw_api'].cursor()
    cursor.execute(
        'SELECT '
        'file_id, phones_hash, phones_count, clean_phones_count '
        'FROM vgw_api.blacklisted_meta;',
    )
    assert cursor.rowcount == 1
    row = cursor.fetchone()
    assert row[0] == 'old_file'

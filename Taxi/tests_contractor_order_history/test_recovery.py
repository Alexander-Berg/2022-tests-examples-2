import pytest


@pytest.fixture(name='mock_yql')
def _mock_yql(mockserver, load):
    class Context:
        _results_data = None

        @property
        def results_data(self):
            if self._results_data is not None:
                return self._results_data
            return load('yql_response_data.txt')

        def set_results_data(self, path):
            self._results_data = load(path)

    context = Context()

    @mockserver.json_handler('/yql/api/v2/operations')
    def _new_operation(request):
        return {'id': 'abcde12345'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results', regex=True,
    )
    def _operation_status(request, operation_id):
        return {'id': operation_id, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/share_id', regex=True,
    )
    def _operation_url(request, operation_id):
        return 'this_is_share_url'

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results_data',
        regex=True,
    )
    def _operation_results_data(request, operation_id):
        return mockserver.make_response(context.results_data, status=200)

    return context


@pytest.mark.parametrize(
    'response_path, inserts, updates',
    [
        ('yql_response_data.txt', 1, 2),
        ('yql_response_data_no_insert.txt', 1, 1),
        ('yql_response_data_with_truncated.txt', 1, 1),
    ],
)
@pytest.mark.config(
    CONTRACTOR_ORDER_HISTORY_YQL_POLLING_PARAMETERS={
        'polling_interval_seconds': 1,
        'max_attempts': 10,
    },
)
async def test_recover_order(
        taxi_contractor_order_history,
        testpoint,
        mock_yql,
        mock_contractor_order_history,
        response_path,
        inserts,
        updates,
):
    @testpoint('recover_order')
    def restore_order(data):
        assert data['success']

    mock_yql.set_results_data(response_path)
    response = await taxi_contractor_order_history.post(
        'recovery/order/create',
        json={'alias_id': 'alias1', 'order_time': 1636383000000},
    )
    assert response.status_code == 200
    assert response.json() == {}
    await restore_order.wait_call()
    assert restore_order.times_called == 0
    assert mock_contractor_order_history.insert.times_called == inserts
    assert mock_contractor_order_history.update.times_called == updates

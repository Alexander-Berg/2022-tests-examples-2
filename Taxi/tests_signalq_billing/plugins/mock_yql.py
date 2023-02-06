import pytest


@pytest.fixture(name='yql', autouse=True)
def _mock_yql(mockserver, load):
    class YqlContext:
        def __init__(self):
            self.operations_request_num = 1
            self.results_data = load('yql_response_data.txt')

        def set_results_data_empty(self, response):
            self.results_data = ''

    context = YqlContext()

    @mockserver.json_handler('/yql/api/v2/operations/1')
    def _mock_status1(request):
        assert request.method == 'GET'
        if context.operations_request_num >= 2:
            return {'id': '1', 'status': 'COMPLETED'}

        context.operations_request_num += 1
        return {'id': '1', 'status': 'RUNNING'}

    @mockserver.json_handler('/yql/api/v2/operations')
    def _mock_operations(request):
        assert request.method == 'POST'
        return {'id': '1'}

    @mockserver.json_handler('/yql/api/v2/operations/1/results_data')
    def _results_data_handler(request):
        assert request.method == 'GET'
        return mockserver.make_response(context.results_data, status=200)

    return context

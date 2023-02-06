import pytest


@pytest.fixture
def mock_stq_agent(mockserver):
    @mockserver.json_handler('/stq-agent/queues/api/take')
    def _mock_take_ready(request):
        return {'tasks': []}

    @mockserver.json_handler('/stq-agent/queues/config')
    def _mock_fetch_configs(request):
        return {'queues': []}

    @mockserver.json_handler('/stq-agent/workers/stats')
    def _mock_send_workers_stats(request):
        return {}

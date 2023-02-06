# encoding=utf-8
import pytest


@pytest.fixture(name='billing_replication', autouse=True)
def _mock_billing_replication(mockserver):
    @mockserver.json_handler('/billing-replication/contract/')
    def _mock_v1_contract(request):
        if request.query['client_id'] == 'bci_id2':
            return [{'ID': 22, 'SERVICES': [128, 123]}]
        return [{'ID': 228, 'SERVICES': [1255, 12211313]}]

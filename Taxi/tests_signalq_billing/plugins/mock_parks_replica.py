import pytest


@pytest.fixture(name='parks_replica', autouse=True)
def _mock_parks_replica(mockserver):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _mock_billing_client_id_retrieve(request):
        assert request.query['park_id'] in ('clid2', 'clid3')
        if request.query['park_id'] == 'clid2':
            return {'billing_client_id': 'bci_id2'}
        return {'billing_client_id': 'bci_id3'}

import pytest


@pytest.fixture(name='mock_billing_replication_ctx')
async def _mock_billing_replication_ctx(mockserver):
    class Response:
        def __init__(self, status, json):
            self.json = json
            self.status = status

    class Context:
        def __init__(self):
            self.context_dict = {}

        def upsert(self, uri, status, json):
            self.context_dict[uri] = Response(status, json)

        def response(self, uri):
            value = self.context_dict.get(uri)
            if value:
                return value
            return Response(200, {})

    return Context()


@pytest.fixture(name='mock_billing_replication')
async def _mock_billing_replication(
        mockserver, load_json, mock_billing_replication_ctx,
):

    uri = '/billing-replication/v1/clients/by_revision/'
    clients = load_json('clients.json')
    mock_billing_replication_ctx.upsert(uri, 200, clients)

    @mockserver.json_handler(uri)
    async def _mock_clients_by_revision(request):
        revision = int(request.query['revision'])
        if revision != 0:
            return mockserver.make_response(
                status=200, json={'max_revision': revision, 'clients': []},
            )
        response = mock_billing_replication_ctx.response(
            '/billing-replication/v1/clients/by_revision/',
        )
        return mockserver.make_response(
            status=response.status, json=response.json,
        )

    uri = '/billing-replication/v1/contracts/by_revision/'

    contracts = load_json('contracts.json')
    mock_billing_replication_ctx.upsert(uri, 200, contracts)

    @mockserver.json_handler(uri)
    async def _mock_contracts_by_revision(request):
        revision = int(request.query['revision'])
        if revision != 0:
            return mockserver.make_response(
                status=200, json={'max_revision': revision, 'contracts': []},
            )
        response = mock_billing_replication_ctx.response(
            '/billing-replication/v1/contracts/by_revision/',
        )
        return mockserver.make_response(
            status=response.status, json=response.json,
        )

    uri = '/billing-replication/v1/balances/by_revision/'

    balances = load_json('balances.json')
    mock_billing_replication_ctx.upsert(uri, 200, balances)

    @mockserver.json_handler(uri)
    async def _mock_balances_by_revision(request):
        revision = int(request.query['revision'])
        if revision != 0:
            return mockserver.make_response(
                status=200, json={'max_revision': revision, 'balances': []},
            )
        response = mock_billing_replication_ctx.response(
            '/billing-replication/v1/balances/by_revision/',
        )
        return mockserver.make_response(
            status=response.status, json=response.json,
        )

    uri = '/billing-replication/v2/balances/by_revision/'

    balances = load_json('balances_v2.json')
    mock_billing_replication_ctx.upsert(uri, 200, balances)

    @mockserver.json_handler(uri)
    async def _mock_v2_balances_by_revision(request):
        revision = int(request.json['revision'])
        if revision != 0:
            return mockserver.make_response(
                status=200, json={'max_revision': revision, 'balances': []},
            )
        response = mock_billing_replication_ctx.response(
            '/billing-replication/v2/balances/by_revision/',
        )
        return mockserver.make_response(
            status=response.status, json=response.json,
        )


@pytest.fixture(name='park_sync_jobs')
async def _park_sync_jobs(
        taxi_parks_activation, mock_billing_replication, mock_territories,
):
    await taxi_parks_activation.run_periodic_task('synchronize-parks')
    await taxi_parks_activation.run_periodic_task('activate-parks')
    await taxi_parks_activation.invalidate_caches()

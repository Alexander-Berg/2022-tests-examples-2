import pytest


@pytest.fixture(name='replication')
def mock_replication(mockserver):
    class Context:
        def __init__(self):
            self.store_handler = {}
            self.stored = []

    context = Context()

    @mockserver.json_handler(
        '/replication/data/subvention_order_context_archive',
    )
    def _store_handler(request):
        context.stored.extend(request.json['items'])
        return {
            'items': [
                {'id': itm['id'], 'status': 'ok'}
                for itm in request.json['items']
            ],
        }

    context.store_handler = _store_handler

    return context

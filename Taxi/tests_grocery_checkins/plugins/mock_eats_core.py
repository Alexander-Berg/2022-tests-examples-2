import pytest


@pytest.fixture(name='eats_core', autouse=True)
def mock_eats_core(mockserver):
    class Context:
        def __init__(self):
            self.payload = []

        def add_logistic_group(self, *, logistic_group_id: int, depot_id: int):
            self.payload.append(
                {
                    'id': logistic_group_id,
                    'places': [depot_id],
                    'metaGroupId': None,
                },
            )

    context = Context()

    @mockserver.json_handler('/eats-core/v1/surge/logistic-groups')
    def _mock_logistic_groups(request):
        return {'payload': context.payload, 'meta': {'count': 1}}

    return context

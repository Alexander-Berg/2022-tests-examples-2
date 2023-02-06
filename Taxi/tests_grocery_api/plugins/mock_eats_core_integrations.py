import pytest


@pytest.fixture(name='eats_core_integrations', autouse=True)
def mock_eats_core_integrations(mockserver):
    class Context:
        def __init__(self):
            self.uid = None
            self.bound_uid = None
            self.addresses = None

        def set_data(self, uid=None, bound_uid=None, addresses=None):
            self.uid = uid
            self.bound_uid = bound_uid
            self.addresses = addresses

        @property
        def times_called(self):
            return addresses.times_called

    context = Context()

    @mockserver.json_handler('/eats-core-integrations/users/addresses')
    def addresses(request):
        assert request.json['user_identity']['yandex_uid'] == context.uid
        assert set(request.json['user_identity']['bound_yandex_uids']) == set(
            [context.uid, context.bound_uid],
        )

        return mockserver.make_response(
            json={'addresses': context.addresses}, status=200,
        )

    return context

# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture(name='mock_direct_internal')
def mock_direct_internal(mockserver):
    class Context:
        def __init__(self):
            self.status_code = 200

        def set_status_code(self, status_code: int):
            self.status_code = status_code

        @property
        def check_client_state_times_called(self) -> int:
            return check_client_state.times_called

        @property
        def add_or_get_times_called(self) -> int:
            return add_or_get.times_called

    ctx = Context()

    @mockserver.json_handler('/direct-internal/clients/checkClientState')
    def check_client_state(request):
        assert request.json['with_balance'] is True
        if request.json['uid'] == 1:
            return mockserver.make_response(
                status=200,
                json={
                    'success': True,
                    'client_state': 'API_ENABLED',
                    'balance': 11,
                },
            )
        return mockserver.make_response(
            status=200,
            json={
                'success': True,
                'client_state': 'API_ENABLED',
                'balance': 10,
            },
        )

    @mockserver.json_handler('/direct-internal/clients/addOrGet')
    def add_or_get(request):
        return mockserver.make_response(
            status=200, json={'success': True, 'client_id': 111},
        )

    return ctx

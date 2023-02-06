# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import pytest


@pytest.fixture(name='mock_driver_tags_v1_match_profile')
def _mock_driver_tags_v1_match_profile(mockserver):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def mock(request):
        return mockserver.make_response(
            status=200, json={'tags': ['eats_courier_from_region_1']},
        )

    return mock


@pytest.fixture(name='robocall_actions')
def _robocall_actions(mockserver, request):
    class Context:
        def __init__(self):
            self.response = {
                'actions': [
                    {
                        'type': 'robocall',
                        'title': 'some_title',
                        'robocall_reason': 'client_not_responding',
                        'free_conditions': [],
                    },
                ],
            }
            self.times_called = 0

    context = Context()

    @mockserver.json_handler(
        '/cargo-orders/internal/cargo-orders/v1/robocall/actions',
    )
    def _mock_robocall_actions():
        return context.response

    return context

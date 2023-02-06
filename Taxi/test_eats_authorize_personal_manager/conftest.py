# pylint: disable=redefined-outer-name
import pytest

import eats_authorize_personal_manager.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301


pytest_plugins = [
    'eats_authorize_personal_manager.generated.service.pytest_plugins',
]


@pytest.fixture(name='eats_restapp_authorizer_mock')
def _eats_restapp_authorizer_mock(
        mock_eats_restapp_authorizer, mockserver, status_restapp,
):
    @mock_eats_restapp_authorizer('/v1/user-access/check')
    async def _v1_user_access_check_post(request):
        data = {'status': status_restapp}
        if status_restapp != 200:
            data = {
                'status': '403',
                'json': {'code': '403', 'message': 'message'},
            }
        return mockserver.make_response(**data)


@pytest.fixture(name='eats_place_subscriptions_mock')
def _eats_place_subscriptions_mock(
        mock_eats_place_subscriptions, mockserver, place_ids, disabled_ids,
):
    @mock_eats_place_subscriptions(
        '/internal/eats-place-subscriptions/v1/feature/enabled-for-places',
    )
    async def _v1_feature_enabled_for_places_post(request):
        return mockserver.make_response(
            status=200,
            json={
                'feature': 'personal_manager',
                'places': {
                    'with_enabled_feature': place_ids,
                    'with_disabled_feature': disabled_ids,
                },
            },
        )

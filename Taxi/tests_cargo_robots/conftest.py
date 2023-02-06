# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from cargo_robots_plugins import *  # noqa: F403 F401


@pytest.fixture(name='oauth_handler_ctx')
def _oauth_handler_ctx(mockserver):
    class Ctx:
        def __init__(self):
            self.response = (200, {})

    return Ctx()


@pytest.fixture(name='oauth_handler')
def _oauth_handler(mockserver, oauth_handler_ctx):
    @mockserver.json_handler('/yandex-oauth/token')
    def handler(request):
        return mockserver.make_response(
            status=oauth_handler_ctx.response[0],
            json=oauth_handler_ctx.response[1],
        )

    return handler


@pytest.fixture(name='passport_internal_handler_ctx')
def _passport_internal_handler_ctx(mockserver):
    class Ctx:
        def __init__(self):
            self.response = (200, {})
            self.alternative_response = None

    return Ctx()


@pytest.fixture(name='passport_internal_handler')
def _passport_internal_handler(mockserver, passport_internal_handler_ctx):
    @mockserver.json_handler('/passport-internal/1/bundle/account/register/')
    def handler(request):
        if passport_internal_handler_ctx.alternative_response:
            tmp = passport_internal_handler_ctx.response
            passport_internal_handler_ctx.response = (
                passport_internal_handler_ctx.alternative_response
            )
            passport_internal_handler_ctx.alternative_response = None
            return mockserver.make_response(status=tmp[0], json=tmp[1])
        return mockserver.make_response(
            status=passport_internal_handler_ctx.response[0],
            json=passport_internal_handler_ctx.response[1],
        )

    return handler


@pytest.fixture(name='create_robot')
def _create_robot(
        taxi_cargo_robots,
        mockserver,
        passport_internal_handler_ctx,
        passport_internal_handler,
        pgsql,
):
    async def func(uid, external_ref, is_registered=True):
        passport_internal_handler_ctx.response = (
            200,
            {'uid': uid, 'status': 'ok'},
        )
        response = await taxi_cargo_robots.post(
            'v1/robot/create',
            params={'external_ref': external_ref, 'user_ip': 'user_ip'},
        )
        assert passport_internal_handler.times_called == 1
        assert response.status == 200
        response_json = response.json()
        assert response_json['external_ref'] == external_ref
        assert response_json['yandex_uid'] == str(uid)
        if not is_registered:
            cursor = pgsql['cargo_robots'].cursor()
            cursor.execute(
                'UPDATE cargo_robots.robots SET yandex_uid = NULL '
                'WHERE external_ref = \'{}\''.format(external_ref),
            )
        return response_json

    return func

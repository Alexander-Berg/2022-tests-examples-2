import pytest


# pylint: disable=wildcard-import, unused-wildcard-import, import-error,
# pylint: disable=redefined-outer-name
from eats_place_rating_plugins import *  # noqa: F403 F401


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_place_rating'].dict_cursor()

    return create_cursor


@pytest.fixture()
def get_answer_log(get_cursor):
    def do_get_answer_log():
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_place_rating.feedback_answer_log;', [],
        )
        return cursor.fetchall()

    return do_get_answer_log


@pytest.fixture
def mock_authorizer_allowed(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_authorizer_403(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'place_ids': request.json['place_ids'],
            },
        )


@pytest.fixture
def mock_authorizer_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Пользователь не найден'},
        )


@pytest.fixture()
def mock_eats_place_subscription(mockserver, request, mocked_time):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/eats-place-subscriptions/v1/'
        'feature/enabled-for-places',
    )
    def _place_subscription(request):
        return mockserver.make_response(
            status=200,
            json={
                'feature': request.json['feature'],
                'places': {
                    'with_enabled_feature': request.json['place_ids'],
                    'with_disabled_feature': [],
                },
            },
        )

    return _place_subscription


@pytest.fixture()
def mock_eats_place_subscription_no(mockserver, request, mocked_time):
    @mockserver.json_handler(
        '/eats-place-subscriptions/internal/eats-place-subscriptions/v1/'
        'feature/enabled-for-places',
    )
    def _eats_place_subscription_no(request):
        return mockserver.make_response(
            status=200,
            json={
                'feature': request.json['feature'],
                'places': {
                    'with_disabled_feature': request.json['place_ids'],
                    'with_enabled_feature': [],
                },
            },
        )

    return _eats_place_subscription_no

import pytest


# root conftest for service eats-layout-constructor
pytest_plugins = ['eats_layout_constructor_plugins.pytest_plugins']


@pytest.fixture(name='zen_mock')
def zen_mock(mockserver):
    @mockserver.json_handler('/eats-places-description/v1/articles/zen/list')
    def _zen_list_handler(request):
        return {
            'articles': {
                'zenArticles': [
                    {
                        'id': 0,
                        'brandId': 1,
                        'title': 'заголовок',
                        'description': 'описание',
                        'url': 'http://url',
                        'authorAvatarUrl': 'iurl',
                    },
                ],
            },
        }


@pytest.fixture(autouse=True)
def offers_mock(mockserver):
    @mockserver.handler('/eats-offers/v1/offer/match')
    def _offer_match(request):
        return mockserver.make_response(json={}, status=500)

    @mockserver.handler('/eats-offers/v1/offer/set')
    def _offer_set(request):
        return mockserver.make_response(json={}, status=500)

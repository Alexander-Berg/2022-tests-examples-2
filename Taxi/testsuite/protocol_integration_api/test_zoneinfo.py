import pytest


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(TARIFF_CATEGORIES_ENABLED_BY_VERSION={})
@pytest.mark.config(
    WELCOME_SCREEN={
        'pool': {
            'image': 'welcome_pool_image',
            'items': [
                {'image': 'welcome_pool_image1', 'text': 'welcome.pool.text1'},
                {'image': 'welcome_pool_image2', 'text': 'welcome.pool.text2'},
                {'image': 'welcome_pool_image3', 'text': 'welcome.pool.text3'},
                {'image': 'welcome_pool_image4', 'text': 'welcome.pool.text4'},
            ],
            'subtitle': 'welcome.pool.subtitle',
            'title': 'welcome.pool.title',
        },
    },
)
def test_simple(taxi_integration, load_json):

    """
    All tests are in protocol's zoneinfo!
    As at the curent time int-api's zoneinfo is protocols's zoneinfo
    (just a proxy in fastcgi)
    """
    request = {
        'id': 'a01d0000000000000000000000000000',
        'point': [37.560827, 55.786958],
        'size_hint': 640,
        'options': True,
    }

    response = taxi_integration.post(
        'v1/zoneinfo',
        request,
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        },
    )

    assert response.status_code == 200
    data = response.json()

    expected_result = load_json('zoneinfo_simple_response.json')

    assert data == expected_result

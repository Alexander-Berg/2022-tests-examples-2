import pytest

from protocol.yauber import yauber


@pytest.mark.now('2017-06-16T12:00:00+0300')
@pytest.mark.config(
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
    LOCALES_UBER_OVERRIDE_KEYSETS={'client_messages': 'override_uber'},
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
@pytest.mark.parametrize(
    'sorted_categories,expected_categories',
    [
        (['uberblack', 'uberx'], ['uberblack', 'uberx']),
        (['uberx', 'uberblack'], ['uberx', 'uberblack']),
        (['uberblack'], ['uberblack', 'uberx']),
        ([], ['uberx', 'uberblack']),
    ],
)
@pytest.mark.parametrize('use_choices_handler', [False, True])
def test_zoneinfo_simple(
        taxi_protocol,
        load_json,
        config,
        sorted_categories,
        expected_categories,
        use_choices_handler,
        dummy_choices,
):
    config.set_values(
        dict(USE_FEEDBACK_RETRIEVE_CHOICES_HANDLER=use_choices_handler),
    )

    config.set_values(dict(UBER_PREFERRED_CATEGORIES_ORDER=sorted_categories))
    taxi_protocol.invalidate_caches()

    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': 'a01d0000000000000000000000000000',
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers={
            'Accept-Language': 'ru',
            'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
            'User-Agent': yauber.user_agent,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data['copyright'] == 'Yauber llc copyright placeholder'
    help_url = 'https://support-uber.com/help'
    assert data['support_page']['url'] == help_url
    assert data['support_phone'] == '+1111111111'
    tariffs_url = 'https://support-uber.com/webview/tariff/moscow'
    assert data['tariffs_url'] == tariffs_url
    assert data['tariffs_url_parts'] == {
        'key': 'MYAUBER',
        'path': '/webview/tariff/moscow',
    }
    assert 'contact_options' not in data

    categories_order = [x['class'] for x in data['max_tariffs']]
    assert categories_order == expected_categories
    assert dummy_choices.was_called() == use_choices_handler


def test_override_translations(taxi_protocol):
    taxi_protocol.invalidate_caches()
    headers = {
        'Accept-Language': 'ru',
        'If-Modified-Since': 'Fri, 16 Jun 2017 07:00:00 GMT',
        'User-Agent': yauber.user_agent,
    }
    response = taxi_protocol.post(
        '3.0/zoneinfo',
        {
            'id': 'a01d0000000000000000000000000000',
            'zone_name': 'moscow',
            'size_hint': 640,
            'options': True,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data['copyright'] == 'Yauber llc copyright placeholder'

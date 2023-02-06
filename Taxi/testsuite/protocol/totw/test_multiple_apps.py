import pytest


USER_ID = 'b300bda7d41b4bae8d58dfa93221ef16'
ORDER_ID = '8c83b49edb274ce0992f337061047375'

YATAXI_USER_AGENT = 'yandex-taxi/3.18.0.7675 android/6.0'
YAUBER_USER_AGENT = 'yandex-uber/3.18.0.7675 android/6.0'

ROUTE_SHARING_KEY = 'a5709ce56c2740d9a536650f5390de01'
ROUTE_SHARING_URL_TEMPLATES_DEFAULT = {
    'yandex': 'https://taxi.yandex.ru/route/{key}?lang={lang}',
    'yataxi': 'https://taxi.yandex.ru/route/{key}?lang={lang}',
    'yauber': 'https://support-uber.com/route/{key}?lang={lang}',
}


@pytest.mark.now('2016-12-15T11:30:00+0300')
@pytest.mark.filldb(orders='driving', order_proc='driving')
@pytest.mark.config(
    ROUTE_SHARING_URL_TEMPLATES=ROUTE_SHARING_URL_TEMPLATES_DEFAULT,
    APPLICATION_MAP_BRAND={
        '__default__': 'yataxi',
        'android': 'yataxi',
        'uber_android': 'yauber',
    },
)
@pytest.mark.parametrize(
    'user_agent, app_brand',
    [
        pytest.param(YATAXI_USER_AGENT, 'yataxi', id='yataxi_app'),
        pytest.param(YAUBER_USER_AGENT, 'yauber', id='yauber_app'),
    ],
)
def test_tow_route_sharing_url(
        taxi_protocol,
        mockserver,
        tracker,
        now,
        db,
        maps_router,
        config,
        user_agent,
        app_brand,
):
    tracker.set_position(
        '999012_a5709ce56c2740d9a536650f5390de0b',
        now,
        55.73341076871702,
        37.58917997300821,
    )

    db.order_proc.update(
        {'_id': ORDER_ID}, {'$set': {'order.rsk': ROUTE_SHARING_KEY}},
    )

    headers = {'User-Agent': user_agent}

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {'format_currency': True, 'id': USER_ID, 'orderid': ORDER_ID},
        headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    assert 'route_sharing_url' in content
    assert content['route_sharing_url'] == (
        ROUTE_SHARING_URL_TEMPLATES_DEFAULT[app_brand].format(
            key=ROUTE_SHARING_KEY, lang='en',
        )
    )

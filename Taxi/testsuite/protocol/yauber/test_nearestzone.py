import pytest


@pytest.mark.parametrize(
    'user_agent,link',
    [
        (
            'yandex-uber/3.78.1.15753 Android/7.1.2 (Xiaomi; Mi A1)',
            'https://play.google.com/store/apps/details?id=com.ubercab&hl=ru',
        ),
        (
            'ru.yandex.uber/4.45.11463 '
            '(iPhone; iPhone5,2; iOS 10.3.3; Darwin)',
            'https://itunes.apple.com/ru/app/uber/id368677368?mt=8',
        ),
    ],
)
@pytest.mark.config(YAUBER_COVERAGE_ZONES=['moscow_activation'])
def test_simple(taxi_protocol, user_agent, link):
    response = taxi_protocol.post(
        '3.0/nearestzone',
        {'id': 'user_id_1', 'point': [0.588144, 0.733842]},
        headers={'User-Agent': user_agent},
    )
    assert response.status_code == 404

    assert {'uber_link': link} == response.json()

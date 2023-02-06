import pytest


@pytest.mark.now('2017-07-19T17:15:15+0000')
def test_launch2x(taxi_protocol):
    response = taxi_protocol.post('2.x/launch', {})
    assert response.status_code == 200
    data = response.json()
    assert data['authorized'] == '0'
    assert data['coupon'] == '0'
    assert data['loyal'] == '0'
    assert data['orders'] == []
    assert data['server_time'] == '2017-07-19T20:15:15'
    assert data['yamoney'] == '0'
    assert data['info']['header'] == 'Обновите приложение'
    assert data['info']['message'] == (
        'Ваша версия приложения устарела и не поддерживается. '
        'Пожалуйста, обновите приложение.'
    )
    assert data['info']['time'] == '2017-07-19T20:05:15'

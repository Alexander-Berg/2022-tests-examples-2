
def test_routestats(client_maker):
    client = client_maker(locale='en')
    client.init_phone(phone='random')
    client.launch()
    response = client.set_source([37.619099, 55.621984])
    _check_fixed_price_disabled(response)
    assert 'offer' not in response

    response = client.set_destinations([client.source])
    _check_fixed_price_enabled(response)
    assert response['offer']
    assert client.offer == response['offer']


def _check_fixed_price_enabled(response):
    if response.get('is_fixed_price'):
        return
    for cls_info in response['service_levels']:
        assert cls_info.get('is_fixed_price')


def _check_fixed_price_disabled(response):
    assert 'is_fixed_price' not in response
    for cls_info in response['service_levels']:
        assert 'is_fixed_price' not in cls_info

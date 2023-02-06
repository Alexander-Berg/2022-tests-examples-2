import pytest


def test_simple(taxi_protocol):
    response = taxi_protocol.post('3.0/nearestparks', {'ll': [37.5, 55.7]})
    assert response.status_code == 200
    data = response.json()
    assert data == {'objects': []}


# field ll is needed
def test_bad_request(taxi_protocol):
    response = taxi_protocol.post('3.0/nearestparks', {'results': 5})
    assert response.status_code == 400
    assert response.reason == 'Bad request'


@pytest.mark.parametrize(
    'pin_point, has_result',
    [
        ([37.5, 55.7], True),  # ru
        ([30.0, 50.0], False),  # ua
        ([-37.5, 55.7], False),  # ocean
    ],
)
@pytest.mark.config(PARTNERS_ALLOWED_COUNTRIES=['ru'])
def test_countries(
        pin_point, has_result, mockserver, load_json, taxi_protocol,
):
    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        return load_json('yamaps_search.json')

    response = taxi_protocol.post('3.0/nearestparks', {'ll': pin_point})
    assert response.status_code == 200
    data = response.json()
    if has_result:
        assert data == {
            'objects': [{'name': 'SuperTaxi', 'phone': '+7(000)222-22-22'}],
        }
    else:
        assert data == {'objects': []}

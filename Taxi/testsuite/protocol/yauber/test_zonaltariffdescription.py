from protocol.yauber import yauber


def test_zonaltariffdescription(taxi_protocol):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post(
        '3.0/zonaltariffdescription', request, headers=yauber.headers,
    )
    assert response.status_code == 200
    data = response.json()
    classes = [tariff['class'] for tariff in data['max_tariffs']]
    assert set(classes) == set(['uberx', 'uberblack'])

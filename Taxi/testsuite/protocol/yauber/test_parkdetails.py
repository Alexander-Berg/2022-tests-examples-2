from protocol.yauber import yauber


def test_parkdetails_ok(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/parkdetails', json={'parkid': '999011'}, headers=yauber.headers,
    )
    assert response.status_code == 200
    content = response.json()
    classes = [tariff['class'] for tariff in content['tariffs']]
    assert set(classes) == set(['uberx', 'uberblack'])

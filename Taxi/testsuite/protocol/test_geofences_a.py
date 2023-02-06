import pytest


@pytest.mark.now('2017-07-06T14:15:16+0300')
def test_geofences_emptydb(taxi_protocol, mockserver, db):
    response = taxi_protocol.post(
        '3.0/geofences', json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['points'] == []

    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': response.headers['Last-Modified']},
    )
    assert response.status_code == 200
    assert data['points'] == []

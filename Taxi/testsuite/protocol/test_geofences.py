import datetime

import bson
import pytest


def test_geofences_simple(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/geofences', json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
    )
    assert response.status_code == 200


@pytest.mark.config(GEOFENCES_ENABLED=False)
def test_geofences_disabled(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 24 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 200
    assert response.json()['points'] == []


def test_geofences_regulardb(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 24 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['points'] == [
        {
            'point': [3.1451596, 3.141596],
            'radius': 120,
            'message': 'qweqweqwe',
        },
    ]

    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 28 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 304


def test_geofences_changeddb(taxi_protocol, db):
    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 24 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['points'] == [
        {
            'point': [3.1451596, 3.141596],
            'radius': 120,
            'message': 'qweqweqwe',
        },
    ]

    db.geofences.update(
        {'_id': bson.ObjectId('c18ef4392ec74a70b1aa2d21')},
        {'$set': {'updated': datetime.datetime(2017, 4, 30, 0, 0, 0)}},
    )

    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 28 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['points'] == [
        {
            'point': [3.1451596, 3.141596],
            'radius': 120,
            'message': 'qweqweqwe',
        },
    ]

    db.geofences.update(
        {'_id': bson.ObjectId('c18ef4392ec74a70b1aa2d21')},
        {
            '$set': {
                'updated': datetime.datetime(2017, 5, 30, 0, 0, 0),
                'zones': [],
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 28 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['points'] == []


@pytest.mark.filldb(geofences='new_fields')
def test_geofences_new_fields(taxi_protocol, db):
    response = taxi_protocol.post(
        '3.0/geofences',
        json={'id': 'c18ef4392ec74a70b1aa2d21751546bd'},
        headers={'If-Modified-Since': 'Tue, 24 Apr 2017 02:00:00 GMT'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['points'] == [
        {
            'point': [3.1451596, 3.141596],
            'radius': 120,
            'message': 'message_1',
            'phantom_flg': True,
            'ban_expire_sec': 604800,
            'communication_id': 'communication_id_1',
            'ban_id': 'ban_id_1',
            'point_tag': 'point_tag_1',
        },
    ]

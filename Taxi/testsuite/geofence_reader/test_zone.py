zero_geometry = {'type': 'MultiPolygon', 'coordinates': []}
svo_geometry = {'name': 'SVO', 'geometry': zero_geometry}
svo_name = svo_geometry['name']
svu_geometry = {'name': 'SVU', 'geometry': zero_geometry}
svu_name = svu_geometry['name']


def test_all(taxi_geofence, mockserver, load, db):
    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert response.json() == []

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svo_name), svo_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == 'SVO'
    assert response.json()[0]['geometry'] == zero_geometry

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svu_name), svu_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200

    assert len(response.json()) == 2
    assert response.json()[0]['name'] == 'SVO'
    assert response.json()[0]['geometry'] == zero_geometry

    assert response.json()[1]['name'] == 'SVU'
    assert response.json()[1]['geometry'] == zero_geometry

    response = taxi_geofence.delete('/monitoring-areas/{}'.format(svo_name))
    assert response.status_code == 200
    response = taxi_geofence.delete('/monitoring-areas/{}'.format(svu_name))
    assert response.status_code == 200


def test_by_id_double(taxi_geofence, mockserver, load, db):
    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert response.json() == []

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svu_name), svu_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svu_name), svu_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = taxi_geofence.delete('/monitoring-areas/{}'.format(svu_name))
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas/{}'.format(svu_name))
    assert response.status_code == 404


def test_by_name(taxi_geofence, mockserver, load, db):
    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert response.json() == []

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svo_name), svo_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas/12')
    assert response.status_code == 404

    response = taxi_geofence.get('/monitoring-areas/{}'.format(svo_name))
    assert response.status_code == 200
    assert response.json()['name'] == 'SVO'
    assert response.json()['geometry'] == zero_geometry

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svo_name), svu_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas')
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = taxi_geofence.get('/monitoring-areas/{}'.format(svu_name))
    assert response.status_code == 200
    assert response.json()['name'] == 'SVU'
    assert response.json()['geometry'] == zero_geometry

    response = taxi_geofence.delete('/monitoring-areas/{}'.format(svu_name))
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas/{}'.format(svu_name))
    assert response.status_code == 404


def test_remove(taxi_geofence, mockserver, load, db):
    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svo_name), svo_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.delete('/monitoring-areas/{}'.format(svo_name))
    assert response.status_code == 200

    response = taxi_geofence.put(
        '/monitoring-areas/{}'.format(svo_name), svo_geometry,
    )
    assert response.status_code == 200

    response = taxi_geofence.get('/monitoring-areas/{}'.format(svo_name))
    assert response.status_code == 200
    assert response.json()['name'] == svo_name
    assert response.json()['geometry'] == zero_geometry

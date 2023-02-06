def test_get_versions(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/whatsnew/versions', params={},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['has_more'] is False
    assert resp_json['versions'][0] == {
        'authors': ['melon-aerial'],
        'created': '2016-12-19T08:26:20.000000Z',
        'taximeter_version': '8.73',
    }
    resp_json['versions'][1]['authors'].sort()
    assert resp_json['versions'][1] == {
        'authors': ['melon-aerial', 'not-melon-aerial'],
        'created': '2016-12-19T08:26:00.000000Z',
        'taximeter_version': '8.71',
    }


def test_get_versions_offset(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/whatsnew/versions', params={'limit': 1, 'cursor': 8.71},
    )
    assert response.status_code == 200
    resp_json = response.json()
    resp_json['versions'][0]['authors'].sort()
    assert resp_json == {
        'has_more': False,
        'versions': [
            {
                'authors': ['melon-aerial', 'not-melon-aerial'],
                'created': '2016-12-19T08:26:00.000000Z',
                'taximeter_version': '8.71',
            },
        ],
    }


def test_get_versions_more_than_last_offset(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/whatsnew/versions', params={'limit': 1, 'cursor': '8.70'},
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {'has_more': False, 'versions': []}


def test_get_versions_bad_offset(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/whatsnew/versions', params={'limit': 1, 'cursor': 'id'},
    )
    assert response.status_code == 400


def test_get_versions_bad_limit(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        '/service/whatsnew/versions', params={'limit': -1},
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.get(
        '/service/whatsnew/versions', params={'limit': 0},
    )
    assert response.status_code == 400

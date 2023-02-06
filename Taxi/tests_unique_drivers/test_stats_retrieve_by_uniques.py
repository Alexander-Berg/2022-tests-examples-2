async def test_stats_retrieve_by_uniques(taxi_unique_drivers):
    response = await taxi_unique_drivers.post(
        'v1/driver/stats/retrieve-by-uniques',
        params={'consumer': 'order-search-status'},
        json={
            'id_in_set': [
                '000000000000000000000001',
                '000000000000000000000002',
                '000000000000000000000003',
                '000000000000000000000004',
                '000000000000000000000005',
                'unique_driver_non',
            ],
        },
    )

    assert response.status_code == 200
    r_json = response.json()
    r_json['stats'].sort(key=lambda x: x['unique_driver_id'])
    assert r_json == {
        'stats': [
            {
                'trips_count': 10,
                'unique_driver_id': '000000000000000000000001',
            },
            {'trips_count': 3, 'unique_driver_id': '000000000000000000000002'},
            {'unique_driver_id': '000000000000000000000003'},
            {
                'trips_count': 15,
                'unique_driver_id': '000000000000000000000004',
            },
            {'unique_driver_id': '000000000000000000000005'},
            {'unique_driver_id': 'unique_driver_non'},
        ],
    }

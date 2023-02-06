def test_subvention_rules(taxi_protocol):
    response = taxi_protocol.get(
        '/utils/1.0/subvention-rules',
        params={
            'latitude': '55.733863',
            'longitude': '37.590533',
            'kind': 'once_bonus',
        },
        headers={'YaTaxi-Api-Key': 'supersecret'},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['rules']) == 1
    actual_rule = data['rules'][0]
    expected_rule = {
        'id': 'moscow_rule_id',
        'zone': 'moscow',
        'tariff': 'econom',
        'kind': 'once_bonus',
        'sum': 500,
        'days': 1,
        'days_is_for_any_category': False,
        'min_num_rides': 23,
        'max_num_rides': 99,
        'brandings': ['lightbox', 'sticker'],
    }
    assert actual_rule == expected_rule

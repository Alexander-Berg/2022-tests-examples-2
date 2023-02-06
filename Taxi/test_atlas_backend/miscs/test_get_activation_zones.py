ACTIVATION_ZONE_DICT = {
    '_id': 'aa6a7a4e0e0843d1a3586d4e384beef8',
    'name': 'korolev_district_activation',
    'geometry': {
        'type': 'Polygon',
        'coordinates': [
            [
                [37.73788657692306, 55.87804134713532],
                [37.773549227985114, 55.880357247695855],
                [37.77736198809973, 55.883392133875695],
                [37.772867276343035, 55.896481024814406],
                [37.81283286121718, 55.90136890908522],
                [37.89949503448835, 55.90520825616452],
                [37.910084395679156, 55.909414826225444],
                [37.934009700092, 55.90587121309627],
                [37.90632930305831, 55.88875122428627],
                [37.910706668170626, 55.87495326391752],
                [37.82238688972822, 55.833626434488274],
                [37.73788657692306, 55.87804134713532],
            ],
        ],
    },
}


async def test_get_activation_zones(web_app_client):
    response = await web_app_client.post(
        '/api/get_activation_zones',
        json={
            'tl': [55.840023128724425, 37.72396087646485],
            'br': [55.7937754850138, 37.849445343017585],
        },
    )
    assert response.status == 200

    content = await response.json()
    assert len(content) == 1

    assert content[0] == ACTIVATION_ZONE_DICT


async def test_get_activation_zones_empty(web_app_client):
    response = await web_app_client.post(
        '/api/get_activation_zones',
        json={
            'tl': [45.840023128724425, 37.72396087646485],
            'br': [45.7937754850138, 37.849445343017585],
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == []

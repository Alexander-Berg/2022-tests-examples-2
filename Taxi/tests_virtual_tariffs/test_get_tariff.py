async def test_get_all_tariffs(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get('/v1/tariffs/list')
    assert response.status_code == 200
    assert response.json() == {
        'tariffs': [
            {
                'coverages': [{'class': 'business', 'zone': 'moscow'}],
                'description': 'Description2',
                'id': 'comfort_pj',
                'special_requirements_ids': ['good_driver'],
            },
            {
                'coverages': [
                    {
                        'corp_client_id': 'b04a64bb1d0147258337412c01176fa1',
                        'zone': 'moscow',
                    },
                    {
                        'class': 'comfort',
                        'corp_client_id': '01234567890123456789012345678912',
                        'zone': 'moscow',
                    },
                ],
                'description': 'Description1',
                'id': 'econom_pj',
                'special_requirements_ids': ['food_delivery'],
            },
        ],
    }


async def test_tariff_by_id(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get('/v1/tariff/?id=comfort_pj')
    assert response.status_code == 200
    assert response.json() == {
        'revision': 2,
        'tariff': {
            'coverages': [{'class': 'business', 'zone': 'moscow'}],
            'description': 'Description2',
            'id': 'comfort_pj',
            'special_requirements_ids': ['good_driver'],
        },
    }


async def test_tariff_by_corp_client_id(taxi_virtual_tariffs, pgsql):
    cursor = pgsql['virtual_tariffs'].conn.cursor()
    cursor.execute(
        """
INSERT INTO virtual_tariffs.tariff_coverage
(tariff_id, corp_client_id, zone_id, class_id)
VALUES
(\'comfort_pj\', \'01234567890123456789012345678912\', \'moscow\', \'econom\'),
(\'comfort_pj\', \'01234567890123456789012345678912\', \'erevan\', \'econom\');
        """,
    )
    cursor.execute(
        """
INSERT INTO virtual_tariffs.special_requirement
(id, description, revision, updated)
VALUES ('some_req', '', 12, '2020-01-01 11:57:50+0000'::timestamptz);
        """,
    )
    cursor.execute(
        """
INSERT INTO virtual_tariffs.tariff_special_requirement
(tariff_id, special_requirement_id)
VALUES ('econom_pj', 'some_req'), ('comfort_pj', 'some_req');
        """,
    )
    response = await taxi_virtual_tariffs.get(
        '/v1/tariffs/list',
        params={'corp_client_id': '01234567890123456789012345678912'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'tariffs': [
            {
                'coverages': [
                    {
                        'class': 'econom',
                        'corp_client_id': '01234567890123456789012345678912',
                        'zone': 'moscow',
                    },
                    {
                        'class': 'econom',
                        'corp_client_id': '01234567890123456789012345678912',
                        'zone': 'erevan',
                    },
                ],
                'description': 'Description2',
                'id': 'comfort_pj',
                'special_requirements_ids': ['good_driver', 'some_req'],
            },
            {
                'coverages': [
                    {
                        'class': 'comfort',
                        'corp_client_id': '01234567890123456789012345678912',
                        'zone': 'moscow',
                    },
                ],
                'description': 'Description1',
                'id': 'econom_pj',
                'special_requirements_ids': ['food_delivery', 'some_req'],
            },
        ],
    }

async def test_matrix_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/compensation/matrix/list/',
    )
    assert response.json() == {
        'matrices': [
            {
                'id': 1,
                'published': False,
                'version_code': 'v.1.0',
                'approved': True,
            },
            {
                'id': 2,
                'published': False,
                'version_code': 'v.2.0',
                'approved': False,
            },
            {
                'id': 3,
                'published': False,
                'version_code': 'v.3.0',
                'approved': True,
            },
            {
                'id': 4,
                'published': False,
                'version_code': 'v.4.0',
                'approved': False,
            },
        ],
    }

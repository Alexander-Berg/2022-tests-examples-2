async def test_matrix_list_get(taxi_eats_compensations_matrix, mockserver):
    response = await taxi_eats_compensations_matrix.get(
        '/eats-compensations-matrix/v1/admin/cancel/matrix/list/',
    )
    assert len(response.json()['matrices']) == 4
    assert response.json() == {
        'matrices': [
            {
                'id': 1,
                'version_code': 'cancel_v.1.0',
                'approved': False,
                'published': False,
            },
            {
                'id': 2,
                'version_code': 'cancel_v.2.0',
                'approved': True,
                'published': False,
            },
            {
                'id': 3,
                'version_code': 'cancel_v.3.0',
                'approved': False,
                'published': False,
            },
            {
                'id': 5,
                'version_code': 'cancel_v.5.0',
                'approved': True,
                'published': False,
            },
        ],
    }

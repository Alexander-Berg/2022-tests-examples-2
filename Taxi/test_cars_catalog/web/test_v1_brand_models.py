import pytest


OK_PARAMS = [
    (
        'Toyota',
        'land cruiser',
        {
            'aliases': ['тойоту', 'тойоте', 'toyota'],
            'code': 'TOYOTA',
            'models': [
                {
                    'aliases': [
                        'королу',
                        'corolla t sport',
                        'corolla wwt',
                        'corolla comfort',
                        'coolla',
                        'corolla д',
                        'corolla',
                    ],
                    'code': 'COROLLA',
                    'name': 'Corolla',
                },
                {
                    'aliases': [
                        'камри',
                        'camry t sport',
                        'camry wwt',
                        'camry comfort',
                        'camry',
                    ],
                    'code': 'CAMRY',
                    'name': 'Camry',
                },
                {
                    'aliases': ['land cruiser'],
                    'code': 'LAND_CRUISER',
                    'name': 'land cruiser',
                },
            ],
            'name': 'Toyota',
        },
    ),
    (
        'Toyota',
        'Prius',
        {
            'aliases': ['тойоту', 'тойоте', 'toyota'],
            'code': 'TOYOTA',
            'models': [
                {
                    'aliases': [
                        'королу',
                        'corolla t sport',
                        'corolla wwt',
                        'corolla comfort',
                        'coolla',
                        'corolla д',
                        'corolla',
                    ],
                    'code': 'COROLLA',
                    'name': 'Corolla',
                },
                {
                    'aliases': [
                        'камри',
                        'camry t sport',
                        'camry wwt',
                        'camry comfort',
                        'camry',
                    ],
                    'code': 'CAMRY',
                    'name': 'Camry',
                },
                {'aliases': ['prius'], 'code': 'PRIUS', 'name': 'Prius'},
            ],
            'name': 'Toyota',
        },
    ),
    (
        'TOYOTA',
        'land cruiser prado',
        {
            'aliases': ['тойоту', 'тойоте', 'toyota'],
            'code': 'TOYOTA',
            'models': [
                {
                    'aliases': [
                        'королу',
                        'corolla t sport',
                        'corolla wwt',
                        'corolla comfort',
                        'coolla',
                        'corolla д',
                        'corolla',
                    ],
                    'code': 'COROLLA',
                    'name': 'Corolla',
                },
                {
                    'aliases': [
                        'камри',
                        'camry t sport',
                        'camry wwt',
                        'camry comfort',
                        'camry',
                    ],
                    'code': 'CAMRY',
                    'name': 'Camry',
                },
                {
                    'aliases': ['land cruiser prado'],
                    'code': 'LAND_CRUISER_PRADO',
                    'name': 'land cruiser prado',
                },
            ],
            'name': 'Toyota',
        },
    ),
    (
        'bmw',
        'X1',
        {
            'code': 'BMW',
            'models': [
                {'code': '7ER', 'name': '7er'},
                {'code': 'X6', 'name': 'X6'},
                {'aliases': ['x1'], 'code': 'X1', 'name': 'X1'},
            ],
            'name': 'BMW',
        },
    ),
    (
        'BMW',
        'X5',
        {
            'code': 'BMW',
            'models': [
                {'code': '7ER', 'name': '7er'},
                {'code': 'X6', 'name': 'X6'},
                {'aliases': ['x5'], 'code': 'X5', 'name': 'X5'},
            ],
            'name': 'BMW',
        },
    ),
    (
        'KIA',
        'Rio',
        {
            'aliases': ['kia'],
            'code': 'KIA',
            'models': [{'aliases': ['rio'], 'code': 'RIO', 'name': 'Rio'}],
            'name': 'KIA',
        },
    ),
    (
        'Toyota',
        'Corolla',
        {
            'aliases': ['тойоту', 'тойоте', 'toyota'],
            'code': 'TOYOTA',
            'models': [
                {
                    'aliases': [
                        'королу',
                        'corolla t sport',
                        'corolla wwt',
                        'corolla comfort',
                        'coolla',
                        'corolla д',
                        'corolla',
                    ],
                    'code': 'COROLLA',
                    'name': 'Corolla',
                },
                {
                    'aliases': [
                        'камри',
                        'camry t sport',
                        'camry wwt',
                        'camry comfort',
                        'camry',
                    ],
                    'code': 'CAMRY',
                    'name': 'Camry',
                },
            ],
            'name': 'Toyota',
        },
    ),
    (
        'Toyota',
        'COROLLA',
        {
            'aliases': ['тойоту', 'тойоте', 'toyota'],
            'code': 'TOYOTA',
            'models': [
                {
                    'aliases': [
                        'королу',
                        'corolla t sport',
                        'corolla wwt',
                        'corolla comfort',
                        'coolla',
                        'corolla д',
                        'corolla',
                    ],
                    'code': 'COROLLA',
                    'name': 'Corolla',
                },
                {
                    'aliases': [
                        'камри',
                        'camry t sport',
                        'camry wwt',
                        'camry comfort',
                        'camry',
                    ],
                    'code': 'CAMRY',
                    'name': 'Camry',
                },
            ],
            'name': 'Toyota',
        },
    ),
]


@pytest.mark.parametrize('brand, model, data', OK_PARAMS)
async def test_ok(web_app_client, mongo, brand, model, data):
    response = await web_app_client.post(
        '/v1/brand-models', json={'brand': brand, 'model': model},
    )

    assert response.status == 200

    existed = await mongo.secondary.auto_dictionary.find(
        {'name': data['name']},
    ).to_list(None)

    assert len(existed) == 1
    stored = existed[0]
    del stored['_id']
    assert stored == data

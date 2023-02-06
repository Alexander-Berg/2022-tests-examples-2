import pytest


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_add_tariff(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs',
        params={'classifier_id': 'classifier_id_1'},
        json={'tariff_id': 'vip', 'is_allowing': False},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'tariff_id': 'vip', 'is_allowing': False}

    cursor = pgsql['classifier'].cursor()
    cursor.execute(
        (
            f'SELECT classifier_id, tariff_id, is_allowing '
            f'FROM classifier.tariffs '
            f'WHERE classifier_id = \'classifier_id_1\''
        ),
    )

    assert cursor.fetchall() == [
        ('classifier_id_1', 'tariff_id_1', True),
        ('classifier_id_1', 'vip', False),
    ]


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_tariff_already_exists(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs',
        params={'classifier_id': 'classifier_id_1'},
        json={'tariff_id': 'tariff_id_1', 'is_allowing': False},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'tariff_already_exists',
        'message': (
            'Tariff  tariff_id_1 in classifier classifier_id_1 already exists'
        ),
    }


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_unavailable_tariff(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs',
        params={'classifier_id': 'classifier_id_1'},
        json={'tariff_id': 'bad_tariff', 'is_allowing': False},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'unavailable_tariff',
        'message': 'Tariff bad_tariff doesn\'t exist',
    }

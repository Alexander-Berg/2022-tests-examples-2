import pytest


@pytest.mark.now('2020-08-12T00:00:00+0000')
@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classifier_clone(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers/clone',
        params={'classifier_id': 'classifier_id_1'},
        json={'classifier_id': 'Piter', 'is_allowing': True},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'classifier_id': 'Piter', 'is_allowing': True}

    cursor = pgsql['classifier'].cursor()
    inserted_classifier_id = 'Piter'
    # select classifier
    cursor.execute(
        (
            f'SELECT classifier_id, is_allowing '
            f'FROM classifier.classifiers '
            f'WHERE classifier_id = \'{inserted_classifier_id}\''
        ),
    )

    assert cursor.fetchall() == [('Piter', True)]

    # select tariffs
    cursor.execute(
        (
            f'SELECT classifier_id, tariff_id, is_allowing '
            f'FROM classifier.tariffs '
            f'WHERE classifier_id = \'{inserted_classifier_id}\''
        ),
    )

    assert cursor.fetchall() == [('Piter', 'tariff_id_1', True)]

    # select rules
    cursor.execute(
        (
            f'SELECT classifier_id, tariff_id, is_allowing, brand, model, '
            f' year_from, year_to, price_from, price_to '
            f'FROM classifier.rules '
            f'WHERE classifier_id = \'{inserted_classifier_id}\''
        ),
    )

    assert cursor.fetchall() == [
        ('Piter', 'tariff_id_1', True, 'BMW', 'X6', None, None, None, None),
        ('Piter', 'tariff_id_1', True, 'Audi', 'TT', None, None, None, None),
        ('Piter', 'tariff_id_1', True, 'Audi', 'A8', None, None, None, None),
        (
            'Piter',
            'tariff_id_1',
            True,
            'Pagani',
            'Zonda',
            0,
            3,
            3000000,
            6000000,
        ),
    ]


@pytest.mark.now('2020-08-12T00:00:00+0000')
@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_clone_existed_classifier(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers/clone',
        params={'classifier_id': 'classifier_id_1'},
        json={'classifier_id': 'classifier_id_2', 'is_allowing': True},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'classifier_already_exists',
        'message': 'Classifier classifier_id_2 already exists',
    }

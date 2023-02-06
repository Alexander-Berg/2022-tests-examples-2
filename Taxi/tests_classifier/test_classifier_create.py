import pytest


@pytest.mark.pgsql('classifier', files=['classifiers.sql'])
async def test_classifier_create(taxi_classifier, pgsql):
    response = await taxi_classifier.post(
        '/v1/classifiers',
        json={'classifier_id': 'Moscow', 'is_allowing': True},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'classifier_id': 'Moscow', 'is_allowing': True}

    cursor = pgsql['classifier'].cursor()
    inserted_classifier_id = 'Moscow'
    cursor.execute(
        (
            f'SELECT classifier_id, is_allowing '
            f'FROM classifier.classifiers '
            f'WHERE classifier_id = \'{inserted_classifier_id}\''
        ),
    )

    assert cursor.fetchall() == [('Moscow', True)]


@pytest.mark.pgsql('classifier', files=['classifiers.sql'])
async def test_classifier_already_exists(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifiers',
        json={'classifier_id': 'classifier_id_1', 'is_allowing': True},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'classifier_already_exists',
        'message': 'Classifier classifier_id_1 already exists',
    }

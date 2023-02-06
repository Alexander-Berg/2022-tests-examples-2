import pytest


@pytest.mark.pgsql('classifier', files=['classifiers.sql'])
async def test_all_classifiers(taxi_classifier):
    response = await taxi_classifier.post('/v1/classifiers/list', json={})

    assert response.status_code == 200
    assert response.json() == {
        'classifiers': [
            {'classifier_id': 'classifier_id_1', 'is_allowing': True},
            {'classifier_id': 'classifier_id_2', 'is_allowing': False},
            {'classifier_id': 'classifier_id_3', 'is_allowing': False},
            {'classifier_id': 'classifier_id_4', 'is_allowing': True},
            {'classifier_id': 'Москва', 'is_allowing': True},
        ],
    }


@pytest.mark.pgsql('classifier', files=['classifiers.sql'])
async def test_query_text(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/classifiers/list', json={'query': {'text': 'КВ'}},
    )

    assert response.status_code == 200
    assert response.json() == {
        'classifiers': [{'classifier_id': 'Москва', 'is_allowing': True}],
    }

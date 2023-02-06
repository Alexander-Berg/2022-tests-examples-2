import pytest


@pytest.mark.pgsql('classifier', files=['classifiers.sql'])
@pytest.mark.parametrize(
    ['classifier', 'tariff_zones'],
    [
        ('classifier_id_1', ['mitino', 'podmoskovie', 'moscow']),
        ('classifier_id_2', ['bryansk']),
    ],
)
async def test_ok(
        taxi_classifier, classifier, tariff_zones, mock_tariff_settings,
):
    response = await taxi_classifier.get(
        '/v1/classifiers/tariff-zones', params={'classifier': classifier},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'tariff_zones': tariff_zones}


@pytest.mark.pgsql('classifier', files=['classifiers.sql'])
async def test_classifier_not_found(taxi_classifier, mock_tariff_settings):
    response = await taxi_classifier.get(
        '/v1/classifiers/tariff-zones',
        params={'classifier': 'unknwon_classifier_id'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'classifier_not_found',
        'message': 'Classifier unknwon_classifier_id was not found',
    }

import pytest


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classification_rule_delete(taxi_classifier, pgsql):
    response = await taxi_classifier.delete(
        '/v1/classifiers/tariffs/classification-rules',
        params={'rule_id': '1'},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {}

    cursor = pgsql['classifier'].cursor()
    cursor.execute(
        (
            f'SELECT classifier_id, tariff_id, is_allowing, '
            f'brand, model, price_from, price_to, year_from, year_to, '
            f'vehicle_before, started_at, ended_at '
            f'FROM classifier.rules '
            f'WHERE id = 1 AND is_deleted = FALSE;'
        ),
    )

    assert cursor.fetchall() == []


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classification_rule_not_found(taxi_classifier, pgsql):
    response = await taxi_classifier.delete(
        '/v1/classifiers/tariffs/classification-rules',
        params={'rule_id': '228'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'rule_not_found',
        'message': 'Rule with id 228 was not found',
    }

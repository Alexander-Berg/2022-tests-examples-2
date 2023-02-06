import pytest


CLASSIFIER_ITEMS_COUNT_QUERY = """
                SELECT SUM(cnt)::INTEGER FROM (
                    SELECT COUNT(*) as cnt FROM classifier.classifiers
                    WHERE classifier_id = 'classifier_id_3'
                    AND is_deleted = FALSE
                    UNION ALL
                    SELECT COUNT(*) as cnt FROM classifier.tariffs
                    WHERE classifier_id = 'classifier_id_3'
                    AND is_deleted = FALSE
                    UNION ALL
                    SELECT COUNT(*) as cnt FROM classifier.rules
                    WHERE classifier_id = 'classifier_id_3'
                    AND is_deleted = FALSE
                ) all_items_count;
            """


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classifier_delete(taxi_classifier, pgsql):
    cursor = pgsql['classifier'].cursor()

    # check classifier related items amount before
    # delete request
    cursor.execute(CLASSIFIER_ITEMS_COUNT_QUERY)
    assert cursor.fetchone()[0] == 3

    response = await taxi_classifier.delete(
        '/v1/classifiers',
        params={'classifier_id': 'classifier_id_3'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 204

    # check amount after delete
    cursor.execute(CLASSIFIER_ITEMS_COUNT_QUERY)
    assert cursor.fetchone()[0] == 0


async def test_classifier_not_found(taxi_classifier):
    response = await taxi_classifier.delete(
        '/v1/classifiers',
        params={'classifier_id': 'classifier_id_3'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'classifier_not_found',
        'message': 'Classifier classifier_id_3 not found',
    }


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
async def test_classifier_used(taxi_classifier):
    response = await taxi_classifier.delete(
        '/v1/classifiers',
        params={'classifier_id': 'classifier_id_1'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'classifier_is_used_in_tariff_zone',
        'message': 'Classifier classifier_id_1 is used in tariff zone',
    }

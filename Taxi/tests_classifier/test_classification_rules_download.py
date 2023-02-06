import pytest


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_download_rules(taxi_classifier, pgsql):

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/download',
        json={
            'classifier_names': [
                'classifier_id_1',
                'classifier_id_2',
                'classifier_id_3',
                'classifier_id_4',
                'Москва',
            ],
        },
    )

    expected_header = (
        'classifier_id;tariff_id;started_at;ended_at;is_allowing;'
        'brand;model;price_from;price_to;year_from;year_to;vehicle_before;'
        'is_tariff_allowing;is_classifier_allowing'
    )

    expected_rules = [
        'classifier_id_1;tariff_id_1;;;1;BMW;X6;;;;;;1;1',
        'classifier_id_1;tariff_id_1;;;1;Audi;TT;;;;;;1;1',
        'classifier_id_1;tariff_id_1;;;1;Audi;A8;;;;;;1;1',
        (
            'classifier_id_1;tariff_id_1;2019-12-27;2020-12-27;1;'
            'Pagani;Zonda;3000000;6000000;0;3;2018-01-01;1;1'
        ),
        'classifier_id_2;tariff_id_2;;;1;;;;;;;;0;0',
        'classifier_id_2;tariff_id_2_1;;;1;;;;;;;;1;0',
        'classifier_id_3;tariff_id_3;;;0;Mercedes;McLaren SLR;;;;;;0;0',
    ]

    assert response.status == 200, response.text

    rules = response.text.split('\n')
    assert rules[0] == expected_header, rules[0]
    for rule in rules[1:]:
        assert rule in expected_rules, rule

    assert 'Content-Disposition' in response.headers
    assert (
        response.headers['Content-Disposition']
        == 'attachment; filename=classification_rules_2019-12-28.csv'
    )


@pytest.mark.pgsql(
    'classifier', files=['classifiers.sql', 'tariffs.sql', 'rules.sql'],
)
@pytest.mark.now('2019-12-27T23:37:00+0000')
async def test_unknown_classifier_id(taxi_classifier, pgsql):

    response = await taxi_classifier.post(
        '/v1/classifiers/tariffs/rules/download',
        json={
            'classifier_names': [
                'classifier_id_1',
                'classifier_id_2',
                'classifier_id_3',
                'UnknownClassifier',
                'Москва',
            ],
        },
    )

    assert response.status == 400, response.text
    assert response.json() == {
        'code': 'classifier_not_found',
        'message': 'Classifier UnknownClassifier not found',
    }

NOT_FRAUDER_RESPONSE = {'decision': 'not_frauder'}
FRAUDER_RESPONSE = {'decision': 'frauder'}
REQUEST_CHECKOUT = {
    'order_nr': 'order_nr',
    'request_uuid': 'request_uuid',
    'user_phone': '+79161234567',
    'user_email': 'user@mail.ru',
    'app_metrica_device_id': 'app_metrica_device_id',
    'appmetric_device_id': 'amdi',
    'yandex_uid': 'yandex_uid',
    'passport_uid': 'passport_uid',
    'client_ip': '212.19.2.1',
    'user_agent': 'user_agent',
    'service_name': 'grocery',
    'order_amount': '100.500',
    'order_currency': 'RUB',
    'promocode': {
        'id': 'promocode_id1',
        'type': 'promocode_type1',
        'constraints': """
        [
            {
                "date": "2020-04-20T23:59:00+03:00",
                "type": "expired_at"
            },
            {
                "type": "minimal_cart",
                "value": 500
            },
            {
                "apps": ["taxi"],
                "type": "app"
            },
            {
                "code": "RU",
                "type": "country"
            },
            {
                "type": "brand",
                "brand_ids": [20369, 39128]
            },
            {
                "type": "max_usages",
                "max_usages": 350000
            },
            {
                "type": "max_usages_by_user",
                "max_usages": 1
            },
            {
                "type": "personal"
            }
        ]
        """,
    },
    'short_address': 'short_address',
    'address_comment': 'address_comment',
    'city': {'id': 'id', 'name': 'moscow'},
    'app_metrica_uuid': 'app_metrica_uuid',
    'appmetric_uuid': 'amu',
    'application_type': 'superapp',
    'order_coordinates': {'lat': 55.761509, 'lon': 37.866500},
    'device_coordinates': {'lat': 55.749531, 'lon': 37.555287},
    'payment_method': 'taxi',
}


def make_old_response(frauder):
    return {'decision': 'frauder' if frauder else 'not_frauder'}


def check_base(taxi_antifraud, testpoint, path, request, expected_response):
    @testpoint('test_rule_triggered')
    def test_rule_triggered(_):
        pass

    @testpoint('rule_triggered')
    def rule_triggered(_):
        pass

    response = taxi_antifraud.post(path, json=request)
    assert response.status_code == 200
    assert response.json() == expected_response

    assert not test_rule_triggered.has_calls
    assert not rule_triggered.has_calls


def check_fraud(
        taxi_antifraud,
        testpoint,
        path,
        request,
        expected_response,
        expected_fraud_rules=None,
):
    rules_triggered = []

    @testpoint('test_rule_triggered')
    def test_rule_triggered(_):
        pass

    @testpoint('rule_triggered')
    def rule_triggered(json):
        rules_triggered.append(json['rule'])

    response = taxi_antifraud.post(path, json=request)
    assert response.status_code == 200
    assert response.json() == expected_response

    assert not test_rule_triggered.has_calls

    assert sorted(rules_triggered) == sorted(
        expected_fraud_rules
        if expected_fraud_rules is not None
        else ['fraud_rule{}'.format(i) for i in range(1, 15)],
    )


def check_new_schema(
        taxi_antifraud,
        testpoint,
        request,
        expected_response,
        expected_rules=None,
        path=None,
):
    rules = {'test_triggered': [], 'triggered': [], 'passed': []}

    @testpoint('test_rule_triggered')
    def test_rule_triggered(_):
        pass

    @testpoint('rule_triggered')
    def rule_triggered(json):
        rules['triggered'].append(json)

    @testpoint('rule_passed')
    def rule_passed(json):
        rules['passed'].append(json)

    response = taxi_antifraud.post(
        'v1/eda/check' if path is None else path, json=request,
    )
    assert response.status_code == 200
    assert response.json() == expected_response

    if expected_rules is not None:
        for t in ['test_triggered', 'triggered', 'passed']:
            if expected_rules.get(t) is not None:
                assert rules[t] == expected_rules[t]

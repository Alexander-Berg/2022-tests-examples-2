import pytest


@pytest.mark.parametrize(
    'query_json, status, expected , data',
    [
        ('request.json', 200, {}, True),
        ('full_request.json', 200, {}, True),
        (
            'different_sizes.json',
            400,
            {
                'code': '400',
                'message': 'Size of example templates is not equal to generated templates size',
            },
            False,
        ),
        (
            'mismatch.json',
            400,
            {
                'code': '400',
                'message': 'Example is not equal to generated entry',
                'details': {
                    'mismatching': [
                        {
                            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                            'amount': '100.0000',
                            'currency': 'RUB',
                            'details': {'alias_id': 'some_alias_id'},
                            'entity_external_id': 'taximeter_driver_id/some_park_id/some_driver_uuid',
                            'event_at': '2020-01-01T00:00:00+00:00',
                            'sub_account': 'tips/googlepay',
                        },
                        {
                            'agreement_id': 'taxi/yandex_ride/mode/driver_fix',
                            'amount': '200.000',
                            'currency': 'EU',
                            'details': {'alias_id': 'some_alias_id'},
                            'entity_external_id': 'taximeter_driver_id/some_park_id/some_driver_uuid',
                            'event_at': '2020-01-01T00:00:00+00:00',
                            'sub_account': 'tips/googlepay',
                        },
                    ],
                },
            },
            False,
        ),
        (
            'missing_field.json',
            400,
            {'code': '400', 'message': 'Field \'amount\' is missing'},
            False,
        ),
        (
            'unclosed_brace.json',
            400,
            {'code': '400', 'message': ' \'}\' is missing '},
            False,
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings')
async def test_templates_check(
        taxi_billing_settings, load_json, query_json, status, expected, data,
):
    entry_template_query = load_json(query_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/create/check', json=entry_template_query,
    )
    assert response.status_code == status
    if not data:
        assert response.json() == expected

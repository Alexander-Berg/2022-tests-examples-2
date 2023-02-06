import pytest


@pytest.mark.parametrize(
    'query, status, expected_json',
    [
        (
            {'name': 'empty_template', 'as_of': '2020-06-01T00:00:00+00:00'},
            200,
            'expected_empty_template_v1.json',
        ),
        (
            {'name': 'empty_template', 'as_of': '2022-01-01T00:00:00+00:00'},
            200,
            'expected_empty_template_v2.json',
        ),
        (
            {
                'name': 'test_store_remittance_purchase',
                'as_of': '2022-01-01T00:00:00+00:00',
            },
            200,
            'expected_test_store_remittance_purchase.json',
        ),
        (
            {
                'some_wrong_param': 'some_wrong_data',
                'as_of': '2022-01-01T00:00:00+00:00',
            },
            400,
            'expected_400.json',
        ),
        (
            {
                'name': 'some_non_exist_config_name',
                'as_of': '2022-02-01T00:00:00+00:00',
            },
            404,
            'expected_404.json',
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings', files=['entry_templates.sql'])
async def test_select_by_name(
        taxi_billing_settings, load_json, query, status, expected_json,
):
    response = await taxi_billing_settings.get(
        'v1/entry_templates/by_name', params=query,
    )
    assert response.status_code == status
    assert response.json() == load_json(expected_json)


@pytest.mark.parametrize(
    'query, status, expected',
    [
        (
            {
                'name': 'some_broken_config_name',
                'as_of': '2022-02-01T00:00:00+00:00',
            },
            500,
            {'code': '500', 'message': 'Internal Server Error'},
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings', files=['broken_template.sql'])
async def test_failed_select_by_name(
        taxi_billing_settings, query, status, expected,
):
    response = await taxi_billing_settings.get(
        'v1/entry_templates/by_name', params=query,
    )
    assert response.status_code == status
    assert response.json() == expected

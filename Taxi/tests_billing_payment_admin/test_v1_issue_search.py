import pytest


@pytest.mark.ydb(files=['fill_issues.sql'])
@pytest.mark.parametrize('test_data_json', ['request.json'])
async def test_search_issue(
        taxi_billing_payment_admin, test_data_json, ydb, load_json,
):
    test_data = load_json(test_data_json)
    response = await taxi_billing_payment_admin.post(
        'v1/issue/search', json=test_data['request'],
    )
    assert response.status_code == 200
    assert response.json() == test_data['expected']

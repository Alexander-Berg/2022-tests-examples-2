import pytest

from tests_cargo_corp import utils

MOCK_NOW = '2021-05-31T19:00:00+00:00'
DATETIME_STRING = '2021-06-30T19:00:00+00:00'
TARIFF_PLAN_SERIES_ID = '123456'
TARIFF_PLANS = [
    {
        'id': '12345',
        'client_id': utils.CORP_CLIENT_ID,
        'tariff_plan_series_id': TARIFF_PLAN_SERIES_ID,
        'date_from': MOCK_NOW,
        'date_to': DATETIME_STRING,
    },
    {
        'id': '123456',
        'client_id': utils.CORP_CLIENT_ID,
        'tariff_plan_series_id': TARIFF_PLAN_SERIES_ID[::-1],
        'date_from': DATETIME_STRING,
    },
]
CORP_ADMIN_ERROR_DETAILS = {
    'id': ['Client plan not found'],
    'date_to': ['date_to must be greater then date_from'],
}


def get_headers():
    return {'X-B2B-Client-Id': utils.CORP_CLIENT_ID}


@pytest.mark.parametrize(
    ('corp_admin_code', 'corp_admin_json', 'date_from', 'date_to'),
    [
        pytest.param(200, {}, None, None, id='no_dates'),
        pytest.param(200, {}, DATETIME_STRING, None, id='date_from'),
        pytest.param(200, {}, MOCK_NOW, DATETIME_STRING, id='both_dates'),
        pytest.param(
            400,
            {
                'status': 'error',
                'code': 'invalid-input',
                'message': 'Invalid input',
                'details': CORP_ADMIN_ERROR_DETAILS,
            },
            None,
            None,
            id='corp_admin_error',
        ),
    ],
)
@pytest.mark.now(MOCK_NOW)
async def test_assign_tariff_plan(
        taxi_cargo_corp,
        mocked_corp_admin,
        corp_admin_code,
        corp_admin_json,
        date_from,
        date_to,
):
    mocked_corp_admin.assign_tariff_plan.set_response(
        corp_admin_code, corp_admin_json,
    )
    mocked_corp_admin.assign_tariff_plan.set_expected_data(
        {'date_from': date_from, 'date_to': date_to},
    )

    request = {'tariff_plan_series_id': TARIFF_PLAN_SERIES_ID}
    if date_from:
        request.update(date_from=date_from)
    if date_to:
        request.update(date_to=date_to)

    response = await taxi_cargo_corp.post(
        '/internal/cargo-corp/v1/client/tariff-plans/assign',
        headers=get_headers(),
        json=request,
    )
    assert response.status_code == (500 if corp_admin_code == 400 else 200)
    if corp_admin_code == 400:
        assert response.json() == {
            'code': 'invalid-input',
            'message': 'Invalid input',
        }


async def test_get_tariff_plans(taxi_cargo_corp, mocked_corp_admin):
    mocked_corp_admin.get_tariff_plans.set_response(
        200, {'items': TARIFF_PLANS},
    )

    response = await taxi_cargo_corp.get(
        '/internal/cargo-corp/v1/client/tariff-plans/info',
        headers=get_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'tariff_plans': TARIFF_PLANS}

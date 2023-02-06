# pylint: disable=redefined-outer-name
import pytest

from test_taxi_corp_integration_api import utils

USER_OPTIONAL = {'uid': '12345678', 'phone_id': '1a1a1a1a1a1a1a1a1a1a1a1a'}
DB_FIELDS_REQUIRED = pytest.mark.filldb(corp_cost_center_options='required')
TEST_CASES_BY_USER_ID = [
    pytest.param(
        'by_user_id',
        {'corp_user_id': 'user_id_1'},
        {'can_use': False, 'reason': 'Не указан центр затрат'},
        200,
        marks=DB_FIELDS_REQUIRED,
        id='by_user-check-error-client-with-new-cost-centers-required',
    ),
    pytest.param(
        'by_user_id',
        {
            'corp_user_id': 'user_id_1',
            'cost_centers': [
                {
                    'id': 'cost_center',
                    'title': 'Центр затрат',
                    'value': 'командировка',
                },
            ],
        },
        {'can_use': True},
        200,
        marks=DB_FIELDS_REQUIRED,
        id='by_user-check-ok-client-with-new-cost-centers-required',
    ),
    pytest.param(
        'by_user_id',
        {},
        {
            'code': 'REQUEST_VALIDATION_ERROR',
            'details': {'reason': 'corp_user_id is required property'},
            'message': 'Some parameters are invalid',
        },
        400,
        id='by_user-api-error-corp_user_id-required',
    ),
]
TEST_PARAMS = dict(
    argnames=[
        'handle_tail',
        'request_data',
        'expected_response',
        'expected_code',
    ],
    argvalues=TEST_CASES_BY_USER_ID,
)


@pytest.mark.config(**utils.CONFIG)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.parametrize(**TEST_PARAMS)
async def test_cost_centers(
        db,
        taxi_config,
        taxi_corp_integration_api,
        handle_tail,
        request_data,
        expected_response,
        expected_code,
):
    response = await taxi_corp_integration_api.post(
        f'/v1/cost_centers/check/{handle_tail}', json=request_data,
    )
    assert await response.json() == expected_response
    assert response.status == expected_code

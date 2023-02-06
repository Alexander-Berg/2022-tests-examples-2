import pytest

from tests_cargo_crm import const

TARIFF_PLAN = {'tariff_plan_series_id': const.TARIFF_PLAN_SERIES_ID}


@pytest.mark.parametrize(
    [
        'tariff_plans_config',
        'tariff_plan_series_id',
        'cargo_corp_response',
        'expected_response',
    ],
    (
        pytest.param(
            {'rus': TARIFF_PLAN},
            None,
            {'status': 200, 'json': {}},
            {'status': 200, 'json': {}},
            id='OK',
        ),
        pytest.param(
            {'isr': TARIFF_PLAN},
            None,
            {'status': 200, 'json': {}},
            {
                'status': 404,
                'json': {
                    'code': 'not_found',
                    'details': {},
                    'message': 'Unknown default_tariff_plan.',
                },
            },
            id='no_default_tariff_plan',
        ),
        pytest.param(
            {'isr': TARIFF_PLAN},
            const.TARIFF_PLAN_SERIES_ID,
            {
                'status': 500,
                'json': {
                    'code': 'not_found',
                    'message': 'Unknown tariff_plan_series_id',
                },
            },
            {
                'status': 500,
                'json': {
                    'code': 'not_found',
                    'details': {},
                    'message': 'Unknown tariff_plan_series_id',
                },
            },
            id='cargo_corp_fail',
        ),
    ),
)
async def test_assign_tariff_plan(
        taxi_cargo_crm,
        mockserver,
        taxi_config,
        tariff_plans_config,
        tariff_plan_series_id,
        cargo_corp_response,
        expected_response,
):
    taxi_config.set_values(
        {'CORP_CARGO_DEFAULT_TARIFF_PLANS': tariff_plans_config},
    )

    @mockserver.json_handler(
        '/cargo-corp/internal/cargo-corp/v1/client/tariff-plans/assign',
    )
    def _handler(request):
        assert (
            request.json['tariff_plan_series_id']
            == const.TARIFF_PLAN_SERIES_ID
        )
        return mockserver.make_response(
            status=cargo_corp_response['status'],
            json=cargo_corp_response['json'],
        )

    request = {
        'corp_client_id': const.CORP_CLIENT_ID,
        'company_country': 'rus',
    }
    if tariff_plan_series_id:
        request['tariff_plan_series_id'] = tariff_plan_series_id

    response = await taxi_cargo_crm.post(
        '/functions/assign-cargo-tariff-plan', json=request,
    )
    assert response.status_code == expected_response['status']
    assert response.json() == expected_response['json']

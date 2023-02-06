import pytest


def get_balance_logout_experiment(enabled: bool):
    """
    Возвращает эксперимент eats_restapp_marketing_balance_logout.
    """

    return pytest.mark.experiments3(
        name='eats_restapp_marketing_balance_logout',
        consumers=['eats_restapp_marketing/ad/balance'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=True,
    )


@pytest.mark.parametrize(
    'status_code',
    [
        pytest.param(400, id='experiment not found'),
        pytest.param(
            400,
            marks=(get_balance_logout_experiment(False)),
            id='experiment disabled',
        ),
        pytest.param(
            403,
            marks=(get_balance_logout_experiment(True)),
            id='experiment enabled',
        ),
    ],
)
async def test_experiment_to_control_auth_error(
        taxi_eats_restapp_marketing, mockserver, status_code,
):
    """
    EDACAT-1285: тест проверяет, что при включении эксперимента
    eats_restapp_marketing_balance_logout, сервис будет возвращать ошибку с
    кодом 403 в случае невалидного токена.
    """

    @mockserver.json_handler('/direct/live/v4/json')
    def direct_live_4_json(request):
        return {}

    response = await taxi_eats_restapp_marketing.get(
        '/4.0/restapp-front/marketing/v1/ad/balance',
        headers={
            'Authorization': 'invalid-oauth-token',
            'X-YaEda-PartnerId': '1',
            'X-Remote-IP': 'localhost',
        },
    )
    assert response.status_code == status_code
    assert direct_live_4_json.times_called == 1

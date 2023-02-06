import pytest

LAUNCH_URL_LIST = '/eats/v1/launch/v1/url-list'


def build_headers(common_values):
    return {'X-Ya-Service-Ticket': common_values['mock_service_ticket']}


CONFIG30_VALUE = {'blocks': [{'url': '123'}]}

CONFIG30 = pytest.mark.experiments3(
    is_config=True,
    name='eats_launch_url_list',
    consumers=['eats-launch/url-list'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value=CONFIG30_VALUE,
)


@CONFIG30
async def test_happy_path(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.post(
        LAUNCH_URL_LIST, headers=build_headers(common_values),
    )
    assert response.status_code == 200
    assert response.json() == CONFIG30_VALUE


async def test_empty_config(taxi_eats_launch, common_values):
    response = await taxi_eats_launch.post(
        LAUNCH_URL_LIST, headers=build_headers(common_values),
    )
    assert response.status_code == 200
    assert response.json() == {}

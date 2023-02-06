import pytest

from test_hiring_taxiparks_gambling import conftest


@conftest.main_configuration
@pytest.mark.parametrize(
    'name',
    [
        'rent_deaf_relation_true',
        'rent_deaf_relation_false',
        'not_rent_false',
        'private_workflow_true',
        'private_workflow_false',
        'not_private_false',
        'not_city_false',
        'medium_true',
        'medium_false',
    ],
)
async def test_verify(
        web_app_client,
        load_json,
        hiring_oldparks_mockserver,
        run_update_parks,
        name,
):
    hiring_oldparks_mockserver(load_json('new_parks.json'))
    await run_update_parks()
    request = load_json('requests.json')[name]
    response = await web_app_client.post(
        '/taxiparks/verify',
        json=request['request'],
        headers={'X-External-Service': 'taximeter'},
    )
    response_body = await response.json()
    assert response.status == 200
    assert response_body == request['expected']

import pytest

HEADERS = {'Accept-language': 'ru', 'User-Agent': 'Taximeter 9.61 (1234)'}


@pytest.mark.parametrize(
    'available_flow_list, city, expected_response',
    [
        (
            {
                'available_flows': [
                    {'code': 'eats-courier', 'url': 'https://eda'},
                    {'code': 'driver-without-auto'},
                    {'code': 'driver-with-auto'},
                    {'code': 'courier'},
                ],
            },
            'Moscow',
            'all_flows_available_response.json',
        ),
        (
            {'available_flows': []},
            'Moscow',
            'no_available_flows_response.json',
        ),
        (
            {
                'available_flows': [
                    {'code': 'driver-without-auto'},
                    {'code': 'driver-with-auto'},
                ],
            },
            'Moscow',
            'no_tabs_drivers_only.json',
        ),
    ],
)
@pytest.mark.experiments3(filename='flows_ordering.json')
@pytest.mark.experiments3(filename='parameters.json')
@pytest.mark.experiments3(filename='tabs_config.json')
async def test_selfreg_v3_proressions(
        taxi_contractor_profession,
        load_json,
        mockserver,
        available_flow_list,
        expected_response,
        city,
):
    response = await taxi_contractor_profession.post(
        '/internal/v1/selfreg/professions',
        headers=HEADERS,
        json={
            'city': city,
            'phone_pd_id': '123',
            'token': 'token1',
            'flows_info': available_flow_list,
        },
    )
    assert response.status_code == 200
    assert response.json() == load_json(expected_response)

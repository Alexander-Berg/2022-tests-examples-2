import pytest

from test_hiring_selfreg_forms import conftest


EXPECTED_FORM_DATA_FILE = 'expected_response_eda_form_data.json'

EXPECTED_FORM_DATA = {
    'hiring_supply_checked': True,
    'requires_hiring_supply_response': False,
    'vacancy': 'Some',
}


@pytest.mark.parametrize('request_name', ['default', 'priority_vacancies'])
@conftest.main_configuration
async def test_internal_eda_vacancy_choose(
        load_json, make_request, request_name,
):
    request = load_json('requests.json')[request_name]

    response = await make_request(
        conftest.ROUTE_INTERNAL_EDA_VACANCY_CHOOSE, data=request,
    )
    assert response['success']
    assert response['vacancy'] == 'eda_car'
    assert response['service'] == 'eda'
    assert response['vehicle_type'] == 'car'
    assert response['form_data'] == EXPECTED_FORM_DATA


@conftest.main_configuration
async def test_internal_eda_vacancy_new_profile(
        load_json, make_request, taxi_hiring_selfreg_forms_web, pgsql,
):

    expected_data = load_json(EXPECTED_FORM_DATA_FILE)['new_profile']
    request = load_json('requests.json')['default']

    await make_request(
        conftest.ROUTE_INTERNAL_EDA_VACANCY_CHOOSE, data=request,
    )

    profile = await taxi_hiring_selfreg_forms_web.get(
        '/v1/eda/form/data',
        params={'form_completion_id': 'f171183b8d6b4e50b1560a7e1f0490b9'},
    )

    form_data = await profile.json()
    assert form_data['data'] == expected_data


@conftest.main_configuration
async def test_internal_eda_vacancy_profile_exists(
        load_json, make_request, taxi_hiring_selfreg_forms_web, pgsql,
):

    expected_data = load_json(EXPECTED_FORM_DATA_FILE)['profile_exists']
    request = load_json('requests.json')['default']

    await taxi_hiring_selfreg_forms_web.post(
        '/internal/v1/eda/data',
        json=dict(
            form_completion_id='f171183b8d6b4e50b1560a7e1f0490b9',
            phone_id='aaaaaaaabbbb4cccddddeeeeeeeeeeee',
            external_id='61fdabf83a0940d0b199768689b3ae31',
            form_data={'key_1': 'value1'},
        ),
    )

    await make_request(
        conftest.ROUTE_INTERNAL_EDA_VACANCY_CHOOSE, data=request,
    )

    profile = await taxi_hiring_selfreg_forms_web.get(
        '/v1/eda/form/data',
        params={'form_completion_id': 'f171183b8d6b4e50b1560a7e1f0490b9'},
    )
    form_data = await profile.json()

    assert form_data['data'] == expected_data

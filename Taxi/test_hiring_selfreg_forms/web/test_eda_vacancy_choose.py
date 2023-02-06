import pytest

from test_hiring_selfreg_forms import conftest


@pytest.mark.parametrize('request_name', ['default', 'priority_vacancies'])
@conftest.main_configuration
async def test_eda_vacancy_choose(
        load_json, make_request, perform_auth, request_name,
):
    request = load_json('requests.json')[request_name]
    id_ = await perform_auth()
    request['form_completion_id'] = id_

    response = await make_request(
        conftest.ROUTE_EDA_VACANCY_CHOOSE, data=request,
    )
    assert response['success']
    assert response['vacancy'] == 'eda_car'
    assert response['service'] == 'eda'
    assert response['vehicle_type'] == 'car'

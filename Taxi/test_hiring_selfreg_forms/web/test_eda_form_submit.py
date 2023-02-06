import pytest

from test_hiring_selfreg_forms import conftest


@pytest.mark.parametrize('request_name', ['default', 'invalid_email'])
@conftest.main_configuration
async def test_eda_form_submit(
        load_json, make_request, perform_auth, request_name,
):
    id_ = await perform_auth()
    data = load_json('requests.json')[request_name]
    await make_request(
        conftest.ROUTE_EDA_FORM_SUBMIT, data=data, status_code=400,
    )

    data['form_completion_id'] = id_

    if request_name == 'invalid_email':
        await make_request(
            conftest.ROUTE_EDA_FORM_SUBMIT, data=data, status_code=400,
        )
        return
    await make_request(
        conftest.ROUTE_EDA_FORM_SUBMIT, data=data, status_code=200,
    )

    invalid_data = data.copy()
    invalid_data['data'] = [{'id': 'some_missed_field', 'value': 'some'}]
    await make_request(
        conftest.ROUTE_EDA_FORM_SUBMIT, data=invalid_data, status_code=404,
    )

    vc_request = load_json('vacancy_choose_requests.json')['default']
    vc_request['form_completion_id'] = id_
    await make_request(conftest.ROUTE_EDA_VACANCY_CHOOSE, data=vc_request)

    response_data = await make_request(
        conftest.ROUTE_EDA_FORM_DATA,
        method='get',
        params={'form_completion_id': id_},
    )
    assert not response_data['is_finished']

    data['is_finished'] = True
    await make_request(
        conftest.ROUTE_EDA_FORM_SUBMIT, data=data, status_code=200,
    )

    await make_request(
        conftest.ROUTE_EDA_FORM_SUBMIT, data=data, status_code=404,
    )

    response_data = await make_request(
        conftest.ROUTE_EDA_FORM_DATA,
        method='get',
        params={'form_completion_id': id_},
    )
    assert response_data['is_finished']

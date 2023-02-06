import pytest

from test_hiring_selfreg_forms import conftest

TVM_RULES = [{'src': 'hiring-selfreg-forms', 'dst': 'personal'}]
DATA = {
    'form_completion_id': conftest.DEFAULT_FORM_COMPLETION_ID,
    'phone': conftest.DEFAULT_PHONE_PHONE_ID_PAIR[0],
    'country': 'Российская Федерация',
    'city': 'Москва',
}


@pytest.mark.config(TVM_RULES=TVM_RULES)
@pytest.mark.client_experiments3(
    consumer='hiring_selfreg_forms/pro_web',
    experiment_name='hiring_sefreg_forms_pro_web',
    args=[
        {
            'name': 'phone_pd_id',
            'type': 'string',
            'value': 'aaaaaaaabbbb4cccddddeeeeeeeeeeee',
        },
        {'name': 'country', 'type': 'string', 'value': 'Российская Федерация'},
        {'name': 'city', 'type': 'string', 'value': 'Москва'},
    ],
    value={'flow': 'web'},
)
async def test_eda_experiment_web(
        load_json, make_request, personal, perform_auth,
):
    response = await make_request(
        conftest.ROUTE_EDA_EXPERIMENT_PRO_WEB, data=DATA, status_code=200,
    )

    assert response['flow'] == 'web'


@pytest.mark.config(TVM_RULES=TVM_RULES)
@pytest.mark.client_experiments3(
    consumer='hiring_selfreg_forms/pro_web',
    experiment_name='hiring_sefreg_forms_pro_web',
    args=[
        {
            'name': 'phone_pd_id',
            'type': 'string',
            'value': 'aaaaaaaabbbb4cccddddeeeeeeeeeeee',
        },
        {'name': 'country', 'type': 'string', 'value': 'Российская Федерация'},
        {'name': 'city', 'type': 'string', 'value': 'Москва'},
    ],
    value={'flow': 'pro'},
)
@pytest.mark.parametrize('parameters', ['without_params', 'with_params'])
async def test_eda_experiment_pro(
        load_json, make_request, personal, parameters,
):
    params = load_json('parameters.json')[parameters]
    data = {**DATA, **params['params']}

    response = await make_request(
        conftest.ROUTE_EDA_EXPERIMENT_PRO_WEB,
        data=data,
        status_code=200,
        headers={'User-Agent': 'iphone'},
    )

    assert response['flow'] == 'pro'
    assert response['link'] == params['link']

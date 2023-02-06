# pylint: disable=redefined-outer-name

import pytest

from test_hiring_candidates import conftest


ROUTE = '/v1/eda/retention/submit'


@pytest.mark.usefixtures('fill_initial_data')
@pytest.mark.parametrize(
    ['request_name', 'eda_core_response'],
    [
        ('default', 'two_couriers_updated_gte_60'),
        ('default', 'one_couriers_updated_gte_60'),
        ('default', 'empty'),
        ('default', 'lost_work_status_updated_at'),
        ('default', 'empty_work_status_updated_at'),
    ],
)
@conftest.main_configuration
async def test_eda_retention_submit_via_data_markup(
        taxi_hiring_candidates_web,
        web_context,
        load_json,
        eda_core_mock,
        request_name,
        eda_core_response,
        mock_data_markup_perform,
):
    async def make_request(data, code=200):
        response = await taxi_hiring_candidates_web.post(ROUTE, json=data)
        assert response.status == code
        return response

    id_ = 'df26389528dd429a903d59f731ccf6b4'
    eda_url = '/eda_core/api/v1/general-information/couriers/catalog/search'

    eda_response = load_json('eda_core.json')[eda_core_response]
    request = load_json('requests.json')[request_name]

    eda_core_mock[eda_url][id_] = eda_response
    await make_request(data=request)
    assert mock_data_markup_perform.has_calls

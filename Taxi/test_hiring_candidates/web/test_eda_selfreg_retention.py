# pylint: disable=redefined-outer-name

import pytest

from generated.models import eda_core as eda_core_models

from hiring_candidates.internal import retention
from test_hiring_candidates import conftest


ROUTE = '/v1/eda/selfreg-retention'


@pytest.mark.usefixtures('fill_initial_data')
@pytest.mark.parametrize(
    ['request_name', 'eda_core_response'],
    [
        ('default', 'two_couriers_updated_gte_60'),
        ('default', 'one_couriers_updated_gte_60'),
        ('default', 'empty'),
        ('default', 'lost_work_status_updated_at'),
        ('default', 'empty_work_status_updated_at'),
        ('deactivated', 'one_courier_deactivated'),
        ('no_ticket_id', 'two_couriers_updated_gte_60'),
        ('hiring_partner_app_consumer', 'two_couriers_updated_gte_60'),
    ],
)
@conftest.main_configuration
async def test_eda_selfreg_retention(
        taxi_hiring_candidates_web,
        web_context,
        load_json,
        eda_core_mock,
        request_name,
        eda_core_response,
        mock_data_markup_perform_response,
        stq,
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
    markup_mock = mock_data_markup_perform_response(
        load_json('data_markup.json')[request_name],
    )

    response = await make_request(data=request)
    assert markup_mock.has_calls
    assert stq.hiring_infranaim_api_updates.times_called == 0
    expected_response = load_json('responses.json')[request_name]
    assert await response.json() == expected_response


@pytest.mark.parametrize(
    ['request_name', 'courier_id'],
    [
        ('priority_primary_blocked', 11111),
        ('priority_primary_deactivated', 22222),
        ('priority_secondary_ill', 11111),
        ('priority_last_candidate', 11111),
    ],
)
async def test_choose_right_courier(
        web_context, load_json, request_name, courier_id,
):
    couriers_ = load_json('couriers.json')[request_name]
    couriers = []
    for courier in couriers_:
        courier_obj = (
            eda_core_models.ResponseCouriersCatalogSearchItem().deserialize(
                courier,
            )
        )
        couriers.append(courier_obj)

    chosen_courier = retention.choose_right_courier(couriers, web_context)

    assert chosen_courier.id == courier_id

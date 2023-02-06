import json

import pytest

from tests_eats_order_revision import helpers

ORDER_ID = 'test_order'
REVISION_ID = 'test_revision'
DEAL_ID_RESPONSE = {'deal_id': 'test_deal_id'}
EXPECTED_MIXIN = {'personal_tin_id': '11111', 'balance_client_id': '22222'}


@pytest.mark.config(
    EATS_ORDER_REVISION_FEATURE_FLAGS={'post_processing_stq_enabled': True},
)
@pytest.mark.parametrize(
    'customer_service_id, billing_data_response',
    [
        ('composition-products', 'native_restaurant'),
        ('delivery-1', 'native_restaurant'),
        ('place-tips-1111', 'native_restaurant'),
        ('tips-1111', 'native_restaurant'),
        ('service_fee-1', 'native_restaurant'),
        ('retail-product', 'native_retail'),
        ('assembly-1', 'native_retail'),
    ],
)
@pytest.mark.parametrize('add_expected_mixin', [False, True])
async def test_one_customer_service_deal_id_correct(
        taxi_eats_order_revision,
        mock_order_billing_data,
        mock_eats_billing_processor,
        stq_runner,
        pgsql,
        load_json,
        customer_service_id,
        billing_data_response,
        add_expected_mixin,
):
    billing_response = load_json(
        'billing_data_responses/{}.json'.format(billing_data_response),
    )
    mock_billing_data = mock_order_billing_data(ORDER_ID, billing_response)

    mock_deal_id = mock_eats_billing_processor(DEAL_ID_RESPONSE)

    doc = load_json(
        'one_customer_service_revisions/{}.json'.format(customer_service_id),
    )
    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=REVISION_ID,
        document=json.dumps(doc),
    )
    if add_expected_mixin:
        helpers.insert_revision_mixin(
            pgsql, ORDER_ID, customer_service_id, json.dumps(EXPECTED_MIXIN),
        )

    await stq_runner.eats_order_revision_creation_post_process.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': REVISION_ID},
    )

    assert mock_billing_data.times_called == 1
    assert mock_deal_id.times_called == 1

    expected_mixin = {'deal_id': DEAL_ID_RESPONSE['deal_id']}
    if add_expected_mixin:
        expected_mixin.update(EXPECTED_MIXIN)
    mixin = helpers.fetch_revision_mixin_payload(
        pgsql, ORDER_ID, customer_service_id,
    )
    assert expected_mixin == mixin

    response = await taxi_eats_order_revision.post(
        'v1/revision/latest/customer-services/details',
        json={'order_id': ORDER_ID},
    )
    assert (
        response.json()['customer_services'][0]['deal_id']
        == DEAL_ID_RESPONSE['deal_id']
    )


@pytest.mark.config(
    EATS_ORDER_REVISION_FEATURE_FLAGS={'post_processing_stq_enabled': True},
)
async def test_complex_service_deal_id_correct(
        mock_order_billing_data,
        mock_eats_billing_processor,
        stq_runner,
        pgsql,
        load_json,
):
    billing_response = load_json('billing_data_responses/native_retail.json')
    mock_billing_data = mock_order_billing_data(ORDER_ID, billing_response)

    mock_deal_id = mock_eats_billing_processor(DEAL_ID_RESPONSE)

    doc = load_json('complex_retail_revision.json')
    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=REVISION_ID,
        document=json.dumps(doc),
    )

    await stq_runner.eats_order_revision_creation_post_process.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': REVISION_ID},
    )
    assert mock_billing_data.times_called == 1
    assert mock_deal_id.times_called == 4
    assert helpers.fetch_mixins_count(pgsql) == 6


@pytest.mark.config(
    EATS_ORDER_REVISION_FEATURE_FLAGS={'post_processing_stq_enabled': True},
)
@pytest.mark.parametrize(
    'n_mock_cancel',
    [
        pytest.param(
            1,
            marks=(
                pytest.mark.experiments3(filename='exp3_cancel_order.json'),
            ),
        ),
        pytest.param(
            0,
            marks=(
                pytest.mark.experiments3(
                    filename='exp3_no_cancel_order_stq.json',
                ),
            ),
        ),
    ],
)
async def test_cancel_order(
        mock_order_billing_data,
        mock_eats_billing_processor,
        mock_eats_core_cancel_order,
        stq_runner,
        pgsql,
        load_json,
        n_mock_cancel,
):
    billing_response = load_json('billing_data_responses/native_retail.json')
    mock_billing_data = mock_order_billing_data(ORDER_ID, billing_response)

    error_response = {'code': 'NOT_FOUND', 'message': 'Cannot find the item'}
    mock_deal_id = mock_eats_billing_processor(error_response, 400)

    cancel_response = {'is_cancelled': True}
    mock_cancel_order = mock_eats_core_cancel_order(cancel_response)

    doc = load_json('complex_retail_revision.json')
    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=REVISION_ID,
        document=json.dumps(doc),
    )

    await stq_runner.eats_order_revision_creation_post_process.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': REVISION_ID},
    )
    assert mock_billing_data.times_called == 1
    assert mock_deal_id.times_called == 1
    assert mock_cancel_order.times_called == n_mock_cancel

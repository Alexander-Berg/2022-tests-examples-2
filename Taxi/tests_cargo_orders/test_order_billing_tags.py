import pytest


@pytest.fixture(name='exp3_order_billing_tags')
async def _exp3_order_billing_tags(experiments3, taxi_cargo_orders):
    async def call(billing_tags=None):
        value = {}
        if billing_tags is not None:
            value['billing_tags'] = billing_tags
        experiments3.add_config(
            match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
            name='cargo_orders_order_billing_tags',
            consumers=['cargo-orders/v1/order-billing-tags'],
            clauses=[],
            default_value=value,
        )
        await taxi_cargo_orders.invalidate_caches()

    return call


def _default_order_billing_tags_request():
    return {
        'order_id': 'taxi-order',
        'tariff_class': 'mock-tariff',
        'transport_type': 'electric_bicycle',
    }


@pytest.fixture(name='v1_order_billing_tags')
async def _v1_order_billing_tags(taxi_cargo_orders):
    class Context:
        request = _default_order_billing_tags_request()

        async def call(self):
            response = await taxi_cargo_orders.post(
                '/v1/order-billing-tags', json=self.request,
            )
            return response

    return Context()


async def test_order_billing_tags_success(
        exp3_order_billing_tags, v1_order_billing_tags,
):
    await exp3_order_billing_tags(['tag_value1', 'tag_value2'])

    response = await v1_order_billing_tags.call()

    assert response.status_code == 200
    assert response.json() == {'billing_tags': ['tag_value1', 'tag_value2']}


async def test_order_billing_tags_value_from_db(
        exp3_order_billing_tags, v1_order_billing_tags, mock_waybill_info,
):
    await exp3_order_billing_tags(['tag_value'])

    response1 = await v1_order_billing_tags.call()
    assert response1.status_code == 200
    assert mock_waybill_info.times_called == 1

    await exp3_order_billing_tags(['will not used'])

    response2 = await v1_order_billing_tags.call()
    assert response2.status_code == 200
    assert response2.json() == {'billing_tags': ['tag_value']}
    assert mock_waybill_info.times_called == 1


async def test_order_billing_tags_not_from_db_on_new_params(
        exp3_order_billing_tags, v1_order_billing_tags,
):
    await exp3_order_billing_tags(['tag_value1'])
    response1 = await v1_order_billing_tags.call()
    assert response1.status_code == 200

    await exp3_order_billing_tags(['tag_value2'])
    v1_order_billing_tags.request['transport_type'] = 'car'
    response2 = await v1_order_billing_tags.call()
    assert response2.status_code == 200
    assert response2.json() == {'billing_tags': ['tag_value2']}

    await exp3_order_billing_tags(['tag_value3'])
    v1_order_billing_tags.request['tariff_class'] = 'new_class'
    response3 = await v1_order_billing_tags.call()
    assert response3.status_code == 200
    assert response3.json() == {'billing_tags': ['tag_value3']}


async def test_order_billing_tags_resave_into_db_with_new_params(
        exp3_order_billing_tags, v1_order_billing_tags, mock_waybill_info,
):
    await exp3_order_billing_tags(['tag_value1'])
    response1 = await v1_order_billing_tags.call()
    assert response1.status_code == 200
    assert mock_waybill_info.times_called == 1

    await exp3_order_billing_tags(['tag_value2'])
    v1_order_billing_tags.request['transport_type'] = 'car'
    response2 = await v1_order_billing_tags.call()
    assert response2.status_code == 200
    assert response2.json() == {'billing_tags': ['tag_value2']}
    assert mock_waybill_info.times_called == 2

    await exp3_order_billing_tags(['will not used'])
    response4 = await v1_order_billing_tags.call()
    assert response4.status_code == 200
    assert response4.json() == {'billing_tags': ['tag_value2']}
    assert mock_waybill_info.times_called == 2


async def test_order_billing_tags_no_config(v1_order_billing_tags):
    response = await v1_order_billing_tags.call()
    assert response.status_code == 200
    assert response.json() == {'billing_tags': []}


async def test_order_billing_tags_empty_config(
        exp3_order_billing_tags, v1_order_billing_tags,
):
    await exp3_order_billing_tags()
    response = await v1_order_billing_tags.call()
    assert response.status_code == 200
    assert response.json() == {'billing_tags': []}


async def test_order_billing_tags_exp_kwargs(
        exp3_order_billing_tags, v1_order_billing_tags, experiments3,
):
    await exp3_order_billing_tags(['tag_value'])

    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_order_billing_tags',
    )
    response = await v1_order_billing_tags.call()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['client_user_id'] == 'taxi_user_id_1'
    assert kwargs['corp_client_id'] == '5e36732e2bc54e088b1466e08e31c486'
    assert kwargs['payment_method'] == 'corp'
    assert kwargs['tariff_class'] == 'mock-tariff'
    assert kwargs['transport'] == 'electric_bicycle'
    assert kwargs['requirements'] == []
    assert kwargs['homezone'] == 'moscow'


async def test_order_billing_tags_exp_kwargs_requiements(
        exp3_order_billing_tags,
        v1_order_billing_tags,
        experiments3,
        my_waybill_info,
):
    await exp3_order_billing_tags(['tag_value'])
    my_waybill_info['waybill']['taxi_order_requirements'] = {
        'bool_req': True,
        'invisible_bool_req': False,
        'obj_req': {},
    }

    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_order_billing_tags',
    )
    response = await v1_order_billing_tags.call()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    assert sorted(tries[0].kwargs['requirements']) == ['bool_req', 'obj_req']


async def test_calc_price_and_order_billing_tags_race(
        exp3_order_billing_tags,
        v1_order_billing_tags,
        calc_price,
        mock_cargo_pricing_calc,
        mock_waybill_info,
):
    await exp3_order_billing_tags(['tag_value1', 'tag_value2'])

    price_response = await calc_price()
    assert price_response.status_code == 200
    assert mock_waybill_info.times_called == 1

    await exp3_order_billing_tags(['will not used'])

    billing_tags_response = await v1_order_billing_tags.call()
    assert billing_tags_response.status_code == 200
    assert billing_tags_response.json() == {
        'billing_tags': ['tag_value1', 'tag_value2'],
    }
    assert mock_waybill_info.times_called == 1


async def test_calc_price_order_billing_tags_exp_kwargs(
        exp3_order_billing_tags, calc_price, experiments3,
):
    await exp3_order_billing_tags(['tag_value'])

    exp3_recorder = experiments3.record_match_tries(
        'cargo_orders_order_billing_tags',
    )
    response = await calc_price()
    assert response.status_code == 200

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['client_user_id'] == 'taxi_user_id_1'
    assert kwargs['corp_client_id'] == '5e36732e2bc54e088b1466e08e31c486'
    assert kwargs['payment_method'] == 'corp'
    assert kwargs['tariff_class'] == 'mock-tariff'
    assert kwargs['transport'] == 'electric_bicycle'
    assert kwargs['requirements'] == []
    assert kwargs['homezone'] == 'moscow'

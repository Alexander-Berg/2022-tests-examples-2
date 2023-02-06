import pytest

from tests_contractor_orders_multioffer import contractor_for_order as cfo

NOW = 1627020050  # 2021-07-23T09:00:00.000000Z


def autoreordered_params():
    params = cfo.default_params()
    params['autoreorder'] = {'decisions': [{'created': NOW - 50}]}
    return params


def multiclass_params():
    params = cfo.default_params()
    params['allowed_classes'] = ['econom', 'comfort', 'business']
    params['order']['request']['class'] = ['econom', 'comfort', 'business']
    return params


def delayed_params():
    params = cfo.default_params()
    params['order']['request']['is_delayed'] = True
    return params


def fallback_price_params():
    params = cfo.default_params()
    params['order']['pricing_data'] = {'is_fallback': True}
    return params


SKIP_AUTOREORDER_CONFIG = {
    'CONTRACTOR_ORDERS_MULTIOFFER_SKIP_AUTOREORDER': {
        'enabled': True,
        'ttl': 60,
    },
}

SKIP_MULTICLASS_CONFIG = {'CONTRACTOR_ORDERS_MULTIOFFER_SKIP_MULTICLASS': True}

SKIP_DELAYED_CONFIG = {'CONTRACTOR_ORDERS_MULTIOFFER_SKIP_DELAYED': True}

SKIP_FALLBACK_PRICE_CONFIG = {
    'CONTRACTOR_ORDERS_MULTIOFFER_SKIP_FALLBACK_PRICE': True,
}


@pytest.mark.driver_tags_match(
    dbid='7f74df331eb04ad78bc2ff25ff88a8f2',
    uuid='4bb5a0018d9641c681c1a854b21ec9ab',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.driver_tags_match(
    dbid='a3608f8f7ee84e0b9c21862beef7e48d',
    uuid='e26e1734d70b46edabe993f515eda54e',
    tags=['uberdriver', 'some_other_tag'],
)
@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'params,config,result',
    [
        (autoreordered_params(), SKIP_AUTOREORDER_CONFIG, 'autoreordered'),
        (autoreordered_params(), {}, 'ok'),
        (multiclass_params(), SKIP_MULTICLASS_CONFIG, 'multiclass'),
        (multiclass_params(), {}, 'ok'),
        (delayed_params(), SKIP_DELAYED_CONFIG, 'delayed'),
        (delayed_params(), {}, 'ok'),
        (
            fallback_price_params(),
            SKIP_FALLBACK_PRICE_CONFIG,
            'fallback_price',
        ),
        (fallback_price_params(), {}, 'ok'),
    ],
)
async def test_contractor_for_order_irrelevant(
        taxi_contractor_orders_multioffer,
        taxi_contractor_orders_multioffer_monitor,
        taxi_config,
        experiments3,
        params,
        config,
        result,
):
    taxi_config.set_values(cfo.create_version_settings('1.00'))
    taxi_config.set_values(config)
    experiments3.add_config(
        **cfo.experiment3(tag='uberdriver', enable_doaa=True),
    )

    await taxi_contractor_orders_multioffer.tests_control(reset_metrics=True)
    response = await taxi_contractor_orders_multioffer.post(
        '/v1/contractor-for-order', json=params,
    )

    expect_status = 'delayed' if result == 'ok' else 'irrelevant'
    assert response.status_code == 200
    assert response.json()['message'] == expect_status

    metrics = await taxi_contractor_orders_multioffer_monitor.get_metric(
        'multioffer_match',
    )
    assert metrics['total_orders'] == int(result == 'ok')
    assert metrics['autoreordered_orders'] == int(result == 'autoreordered')
    assert metrics['multiclass_orders'] == int(result == 'multiclass')
    assert metrics['delayed_orders'] == int(result == 'delayed')
    assert metrics['fallback_price_orders'] == int(result == 'fallback_price')

    assert metrics['moscow']
    assert metrics['moscow']['total_orders'] == int(result == 'ok')
    assert metrics['moscow']['autoreordered_orders'] == int(
        result == 'autoreordered',
    )
    assert metrics['moscow']['multiclass_orders'] == int(
        result == 'multiclass',
    )
    assert metrics['moscow']['delayed_orders'] == int(result == 'delayed')
    assert metrics['moscow']['fallback_price_orders'] == int(
        result == 'fallback_price',
    )

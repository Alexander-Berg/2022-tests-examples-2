# pylint: disable=redefined-outer-name, unused-variable
import pytest

CONSUMER = 'umlaas-eats-regional-offset'

AUTOMATED_OFFSET_CONFIG = pytest.mark.config(
    UMLAAS_EATS_AUTOMATED_OFFSET_ENABLED=True,
)

AUTOMATED_OFFSET_SETTINGS = pytest.mark.config(
    UMLAAS_EATS_AUTOMATED_OFFSET_SETTINGS={
        'calculating': True,
        'logging': False,
        'time_rounding_precision_minutes': 5,
    },
)


def exp3_decorator(name, value):
    return pytest.mark.experiments3(
        name=name,
        consumers=[CONSUMER],
        match={
            'predicate': {
                'init': {
                    'set': [919191],
                    'arg_name': 'place_id',
                    'set_elem_type': 'int',
                },
                'type': 'in_set',
            },
            'enabled': True,
        },
        clauses=[],
        default_value=value,
    )


LL_EXP_PARAMS = exp3_decorator(
    name='umlaas_eats_regional_offset',
    value={
        'enabled': True,
        'rule': [{'threshold': 50, 'offset': 17, 'window': 6}],
    },
)


@AUTOMATED_OFFSET_SETTINGS
@AUTOMATED_OFFSET_CONFIG
@LL_EXP_PARAMS
async def test_regional_offset_cache(
        taxi_umlaas_eats, regional_offset_calculator, load_json, testpoint,
):
    @testpoint('regional-offset-cache')
    def load_level_tp(data):
        pass

    await taxi_umlaas_eats.enable_testpoints()
    response = await load_level_tp.wait_call()

    data = response['data']
    assert data['num_items_loaded'] == 2
    assert data['load_level1'] == 100
    assert data['status1'] == 'ok'
    assert data['offset1'] == 17
    assert data['window1'] == 6
    assert data['load_level2'] == 75
    assert data['status2'] == 'no_exp_value'


@pytest.mark.experiments3(
    name='umlaas_eats_real_time_statistics_cache_settings',
    consumers=['umlaas-eats-eta'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'enabled': True, 'update_batch_size': 1},
)
async def test_real_time_statistics_cache(
        taxi_umlaas_eats, real_time_statistics_provider, load_json, testpoint,
):
    @testpoint('real-time-statistics-cache')
    def real_time_statis_tp(data):
        pass

    await taxi_umlaas_eats.enable_testpoints()
    response = await real_time_statis_tp.wait_call()

    data = response['data']
    assert data['num_items_loaded'] == 1
    assert round(data['cooking0'] - 5.4278344946427808e-8, 6) == 0
    assert round(data['ready_to_delivery1'] - 0.4497153313088638, 6) == 0

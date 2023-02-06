# pylint: disable=redefined-outer-name, unused-variable


async def test_get_extended_supply(
        taxi_umlaas_eats, eda_surge_calculator, load_json, testpoint,
):
    @testpoint('extended-supply-cache')
    def extended_supply_cache_tp(data):
        pass

    await taxi_umlaas_eats.enable_testpoints()
    response = await extended_supply_cache_tp.wait_call()

    expected = load_json('eda_surge_calculator_extended_supply_response.json')

    data = response['data']
    assert data['items_loaded'] == 3
    assert data['cache_size'] == 3
    assert not data['places']['55555']['candidates']
    assert len(data['places']['321075']['candidates']) == 2
    assert (
        data['places']['90213']['candidates']
        == expected['places'][0]['candidates']
    )

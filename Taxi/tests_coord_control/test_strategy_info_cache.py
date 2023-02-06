import json


CHANNEL_NAME = 'strategy-info-channel'
RECEIVED_STRATEGIES_NAME = 'received-strategies'
STRATEGY_INFOS = {
    'performer1': {'etag': 'etag1', 'agent_info': 'taximeter_agent_info1'},
    'performer2': {'etag': 'etag2', 'agent_info': 'taximeter_agent_info2'},
    'performer3': {'etag': 'etag3', 'agent_info': 'taximeter_agent_info3'},
    'performer4': {'etag': 'etag4', 'agent_info': 'taximeter_agent_info4'},
}


async def test_backward_compatibility(
        taxi_coord_control, redis_store, load_binary, load_json, testpoint,
):
    @testpoint('received-strategies')
    def received_strategies(data):
        return data

    await taxi_coord_control.invalidate_caches()

    strategy_info_chunk = load_binary('packed_strategies.bin')
    redis_store.publish(CHANNEL_NAME, strategy_info_chunk)

    strategy_infos = (await received_strategies.wait_call())['data']
    assert len(strategy_infos) == len(STRATEGY_INFOS)
    for key in strategy_infos.keys():
        assert key in STRATEGY_INFOS
        assert strategy_infos[key]['etag'] == STRATEGY_INFOS[key]['etag']
        assert (
            strategy_infos[key]['agent_info']
            == STRATEGY_INFOS[key]['agent_info']
        )
    expected_response = load_json('location_settings_response.json')
    assert (
        json.loads(strategy_infos['performer4']['response'])
        == expected_response
    )

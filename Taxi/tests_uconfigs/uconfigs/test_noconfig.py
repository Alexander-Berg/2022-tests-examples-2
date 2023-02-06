import json


async def test_configs_value(taxi_uconfigs, mockserver):
    @mockserver.json_handler('/configs-service/configs/values')
    def config(request):
        return mockserver.make_response(
            json.dumps(
                {'configs': {}, 'updated_at': '2018-08-24T18:36:00.15Z'},
            ),
            200,
        )

    await taxi_uconfigs.invalidate_caches()
    assert config.times_called == 0

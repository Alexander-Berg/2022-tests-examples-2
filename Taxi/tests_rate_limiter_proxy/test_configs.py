# pylint: disable=import-error
from rate_limiter.fbs.Configs import Configs


def _parse_configs(data):
    result = {}
    configs = Configs.GetRootAsConfigs(data, 0)
    for i in range(configs.ConfigsLength()):
        config = configs.Configs(i)
        result[config.Key().decode('utf-8')] = config.Value().decode('utf-8')
    return result


async def test_configs(taxi_rate_limiter_proxy):
    response = await taxi_rate_limiter_proxy.get('configs')
    assert response.status_code == 200
    configs = _parse_configs(response.content)
    assert {'TVM_ID': '2345'}.items() <= configs.items()

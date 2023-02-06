from aiohttp import ClientSession
from freeswitch_testsuite.environment_config import WEB_BIND_ADDRESS, MOD_IVRD_PORT
from freeswitch_testsuite.logs import log_error
from termcolor import colored
from typing import Dict

__all__ = [
    'assert_metrics',
    'collect_metrics'
]


async def assert_metrics(ts_metrics: Dict):
    metrics: Dict = await collect_metrics()
    for m, v in ts_metrics.items():
        try:
            assert m in metrics
        except AssertionError:
            log_error(f'{colored(f"No {m} in {metrics}", "red")}')
            raise
        try:
            assert metrics[m] == v
        except AssertionError:
            log_error(
                f'{colored(f"{m}: {v} != {metrics[m]}", "red")}')
            raise


async def collect_metrics() -> Dict:
    async with ClientSession() as session:
        async with session.get(f'http://{WEB_BIND_ADDRESS}:{MOD_IVRD_PORT}'
                               f'/statistics') as resp:
            assert resp.status == 200
            assert resp.content_type == 'application/json'
            metrics: Dict = await resp.json()
            to_ret: Dict = {}
            assert 'metrics' in metrics
            for metric in metrics['metrics']:
                assert 'labels' in metric
                assert 'name' in metric['labels']
                assert 'value' in metric
                name: str = metric['labels']['name']
                value: int = metric['value']
                to_ret[name] = value

            return to_ret

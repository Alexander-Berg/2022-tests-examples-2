# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from heatmap_surge_api_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(
    autouse=True,
    scope='function',
    params=[
        pytest.param(
            'deduction_config',
            marks=[
                pytest.mark.experiments3(
                    filename='cfg3_heatmap_surge_api_deduction.json',
                ),
            ],
        ),
    ],
)
def deduction_config():
    pass


@pytest.fixture(autouse=True)
def heatmap_renderer(mockserver):
    @mockserver.json_handler('/heatmap-renderer/v2/meta')
    def _meta_handler(request):
        return mockserver.make_response(
            json={
                'version_id': '148',
                'legend_min': 1.1,
                'legend_max': 1.7,
                'legend': '1.1 - 1.7',
                'legend_measurement_units': 'RUR',
                'updated_epoch': 1580724683,
            },
            headers={'Access-Control-Allow-Origin': '*'},
        )

    @mockserver.json_handler('/heatmap-renderer/v2/version')
    def _version_handler(request):
        return mockserver.make_response(
            json={'version_id': '148'},
            headers={'Access-Control-Allow-Origin': '*'},
        )


@pytest.fixture(autouse=True)
def heatmap_storage(mockserver):
    @mockserver.json_handler('/heatmap-storage/v1/enumerate_keys')
    def _mock_enumerate_keys(request):
        content_type = request.query['content_type']
        if content_type == 'taxi_surge':
            return mockserver.make_response(
                json={'content_keys': ['taxi_surge/__default__/default']},
            )
        return mockserver.make_response(
            json={
                'content_keys': [
                    'taxi_surge_lightweight/__default__/default',
                    'taxi_surge_lightweight/__default__/default_baseline',
                    'taxi_surge_lightweight/econom/default',
                ],
            },
        )


@pytest.fixture(autouse=True)
def _fill_s3_heatmap_storage(s3_heatmap_storage):
    content_keys = [
        'taxi_surge/__default__/default',
        'taxi_surge_lightweight/__default__/default',
        'taxi_surge_lightweight/__default__/default_baseline',
        'taxi_surge_lightweight/econom/default',
    ]

    for content_key in content_keys:
        s3_heatmap_storage.put_map(content_key, None, None, None, b'')


@pytest.fixture(autouse=True)
def tags(mockserver):
    @mockserver.json_handler('/driver-tags/v1/drivers/match/profile')
    def _default_driver_tags(request):
        return {'tags': []}


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(pytest.mark.geoareas(filename='geoareas.json'))
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))

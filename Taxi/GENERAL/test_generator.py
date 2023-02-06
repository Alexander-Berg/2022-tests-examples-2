# pylint: disable=protected-access
import json
import os.path

import pytest

from taxi_dashboards import constructor
from taxi_dashboards import generator
from taxi_dashboards import utils


@pytest.mark.parametrize(
    'path,expected',
    [('foo.yaml', 'foo'), ('/home/taxi/taxi_api.yaml', 'taxi_api')],
)
def test_title_from_path(path, expected):
    title = generator._title_from_path(path)
    assert title == expected


def test_generate_dashboard(patch, monkeypatch):
    hosts = {
        'taxi_api': (
            'taxi-api01e.taxi.yandex.net',
            'taxi-api05e.taxi.yandex.net',
            'taxi-api03f.taxi.yandex.net',
        ),
        'taxi_prestable_api': ('taxi-api01e.taxi.yandex.net',),
    }
    groups = {
        'taxi_api': ['taxi_all', 'taxi_prod_all', 'taxi_api'],
        'taxi_prestable_api': [
            'taxi_all',
            'taxi_prod_all',
            'taxi_prestable_all',
            'taxi_api',
            'taxi_prestable_api',
        ],
    }
    test_folder = os.path.splitext(__file__)[0]
    path = os.path.join(test_folder, 'test_config.yaml')
    config = utils.load_yaml(path)

    @patch('taxi_dashboards.clients.conductor.get_hostlist')
    def _conductor_get_hostlist(conductor_group):
        return hosts[conductor_group]

    @patch('taxi_dashboards.clients.conductor.get_groups_for_host')
    def _conductor_get_groups_for_host(host):
        for group, group_hosts in hosts.items():
            if host in group_hosts:
                return groups[group]
        return None

    old_get_template_file = constructor.get_template_file

    @patch('taxi_dashboards.constructor.get_template_file')
    def _get_template_file(element, panel_group=None):
        if element in ('base_panel', 'dashboard', 'row') and not panel_group:
            return os.path.join(test_folder, 'templates', '%s.json' % element)
        return old_get_template_file(element, panel_group)

    dashboard, _ = generator.generate_dashboard(path, config)
    with open(
            os.path.join(
                os.path.splitext(__file__)[0], 'expected_dashboard.json',
            ),
    ) as expected_dashboard_file:
        expected_dashboard = json.load(expected_dashboard_file)

    assert expected_dashboard == dashboard

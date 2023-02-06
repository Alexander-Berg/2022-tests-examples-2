# pylint: disable=protected-access
import json
import os.path

from taxi_dashboards import generator
from taxi_dashboards import utils


def test_generate_dashboard():
    test_folder = os.path.splitext(__file__)[0]
    print(test_folder)
    path = os.path.join(test_folder, 'test_config_metrix.yaml')
    config = utils.load_yaml(path)

    dashboard, _ = generator.generate_dashboard(path, config)
    with open(
            os.path.join(
                os.path.splitext(__file__)[0],
                'expected_dashboard_metrix.json',
            ),
    ) as expected_dashboard_file:
        expected_dashboard = json.load(expected_dashboard_file)

    assert expected_dashboard == dashboard

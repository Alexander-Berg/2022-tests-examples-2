import pathlib

import pytest

from replication.local_replication import local_yaml

_STATIC = pathlib.Path(__file__).parent.joinpath('static', 'test_local_yaml')


@pytest.mark.parametrize(
    'local_yaml_path,expected',
    [
        (
            'local.1.yaml',
            local_yaml.LocalYaml(
                local_yaml_path=str(_STATIC.joinpath('local.1.yaml')),
                yt={'force_prefix': '//home/prefix/'},
                secdist={'path': '/home/secdist.json'},
                environ={'FOO': 'abc', 'BAR': 'cxz'},
                mongo={'database_label': 'xxx'},
            ),
        ),
        (
            'local.2.yaml',
            local_yaml.LocalYaml(
                local_yaml_path=str(_STATIC.joinpath('local.2.yaml')),
                yt={'force_prefix': '//home/prefix/'},
                secdist={'path': '/home/secdist.json'},
            ),
        ),
    ],
)
def test_load(local_yaml_path, expected):
    replication_local_yaml = local_yaml.load(
        str(_STATIC.joinpath(local_yaml_path)),
    )
    assert replication_local_yaml.local_yaml_path == expected.local_yaml_path
    assert replication_local_yaml.yt == expected.yt
    assert replication_local_yaml.secdist == expected.secdist
    assert replication_local_yaml.mongo == expected.mongo
    assert replication_local_yaml.environ == expected.environ

    assert replication_local_yaml == expected

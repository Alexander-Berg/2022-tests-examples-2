from __future__ import print_function, unicode_literals

import pytest

from sandbox.projects.release_machine.components import configs as rm_config
from sandbox.projects.release_machine.core import const as rm_const


@pytest.mark.parametrize(
    "deploy_list, expected",
    [
        (
            [rm_config.DeployServicesInfo(["s1"])],
            [rm_config.DeployServicesInfo(["s1"])],
        ),
        (
            [("stable", "s1")],
            [rm_config.DeployServicesInfo(["s1"])],
        ),
        (
            [
                ("stable", "s1"),
                ("stable", "s2"),
                ("testing", "s3"),
            ],
            [
                rm_config.DeployServicesInfo(["s1", "s2"]),
                rm_config.DeployServicesInfo(["s3"], level=rm_const.ReleaseStatus.testing)
            ],
        ),
        (
            [
                rm_config.DeployServicesInfo(["s1"]),
                ("stable", "s1"),
                ("stable", "s2"),
                ("testing", "s3"),
            ],
            [
                rm_config.DeployServicesInfo(["s1", "s2"]),
                rm_config.DeployServicesInfo(["s3"], level=rm_const.ReleaseStatus.testing)
            ],
        )
    ]
)
def test__to_deploy_info(deploy_list, expected):
    assert sorted(rm_config.ReferenceConfig.Releases.to_deploy_infos(deploy_list)) == sorted(expected)

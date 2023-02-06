# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.release_machine import core


class CompatibilityTest(unittest.TestCase):
    rr = core.ReleasedResource(1, 2, 3, 4, 5, 6, 7, owner="owner")
    dr1 = core.DeployedResource(1, 2, 3, 4, 5, 6, 7, owner="owner", info="deploy_info")
    dr2 = core.DeployedResource(1, 2, 3, 4, 5, 6, 7, owner="owner")
    dr3 = core.DeployedResource(1, 2, 3, 5, 5, 6, 7, owner="owner")
    dr4 = core.DeployedResource(1, 2, 3, 4, 6, 6, 7, owner="owner")

    def test_comparison(self):
        self.assertFalse(self.dr1 < self.dr2)
        self.assertFalse(self.dr2 < self.dr1)
        self.assertTrue(self.dr1 < self.dr3)
        self.assertTrue(self.dr1 < self.dr4)
        self.assertDictEqual(
            self.dr3.to_json(),
            max([self.dr1, self.dr2, self.dr3, self.dr4]).to_json()
        )

    def test_compatibility(self):
        self.assertDictEqual(
            self.rr.to_json(),
            {
                "id": 1,
                "build_task_id": 2,
                "timestamp": 3,
                "major_release": 4,
                "minor_release": 5,
                "component": 6,
                "status": 7,
                "owner": "owner",
                "info": None,
                "resource_name": "",
            }
        )
        self.assertDictEqual(
            self.dr1.to_json(),
            {
                "id": 1,
                "build_task_id": 2,
                "timestamp": 3,
                "major_release": 4,
                "minor_release": 5,
                "component": 6,
                "status": 7,
                "owner": "owner",
                "info": "deploy_info",
                "resource_name": "",
            }
        )
        self.assertDictEqual(core.DeployedResource.from_released(self.rr).to_json(), self.dr2.to_json())

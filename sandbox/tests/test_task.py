import mock
import pytest

from sandbox import sdk2
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShoot2 import YabsServerB2BFuncShoot2
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp import YabsServerB2BFuncShootCmp


def get_resource_attributes_mock_side_effect(resource_id):
    """Side effect for get_resource_attributes mock.

    :param resource_id: Resource id
    :type resource_id: int
    :return: Resource attributes
    :rtype: dict
    """
    return {"service_tag": "hamster_{}".format(resource_id)}


class TestCompareEnabledHamsters:
    """Test method YabsServerB2BFuncShootCmp.compare_enabled_hamsters."""
    @classmethod
    def setup_class(cls):
        """Set up any state specific to the execution of the given class."""
        cls.get_resource_attributes_patcher = mock.patch(
            "sandbox.projects.yabs.qa.hamster.utils.get_resource_attributes",
            side_effect=get_resource_attributes_mock_side_effect)
        cls.get_resource_attributes_patcher.start()

    @classmethod
    def teardown_class(cls):
        """Teardown any state that was previously setup with a call to setup_class."""
        cls.get_resource_attributes_patcher.stop()

    @pytest.mark.parametrize(
        ["pre_hamster_tags", "pre_resource_ids", "test_hamster_tags", "test_resource_ids", "has_diff"],
        [
            (
                ["hamster_1", "hamster_2"],
                [1, 2],
                ["hamster_1", "hamster_2"],
                [1, 3],
                True,
            ),
            (
                ["hamster_1", "hamster_2"],
                [1, 2],
                ["hamster_1", "hamster_2"],
                [1, 2],
                False,
            ),
        ]
    )
    def test_compare_enabled_hamsters(
        self, pre_hamster_tags, pre_resource_ids,
        test_hamster_tags, test_resource_ids, has_diff,
    ):
        """Test method YabsServerB2BFuncShootCmp.compare_enabled_hamsters."""
        pre_shoot_task = mock.create_autospec(YabsServerB2BFuncShoot2)
        pre_shoot_task.Parameters.hamster_ext_service_tags = pre_hamster_tags
        pre_shoot_task.Parameters.ext_service_endpoint_resources = [
            mock.create_autospec(sdk2.Resource, id=resource_id)
            for resource_id in pre_resource_ids
        ]

        test_shoot_task = mock.create_autospec(YabsServerB2BFuncShoot2)
        test_shoot_task.Parameters.hamster_ext_service_tags = test_hamster_tags
        test_shoot_task.Parameters.ext_service_endpoint_resources = [
            mock.create_autospec(sdk2.Resource, id=resource_id)
            for resource_id in test_resource_ids
        ]

        cmp_task = mock.create_autospec(YabsServerB2BFuncShootCmp)
        cmp_task.pre_task = pre_shoot_task
        cmp_task.test_task = test_shoot_task

        diff = YabsServerB2BFuncShootCmp.compare_enabled_hamsters(cmp_task)
        assert has_diff == bool(diff)

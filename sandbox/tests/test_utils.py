import mock
import pytest

from sandbox.projects.yabs.qa.hamster.utils import AmbiguousEndpointResources, calculate_enabled_hamsters


def get_resource_attributes_mock_side_effect(resource_id):
    """Side effect for get_resource_attributes mock.

    :param resource_id: Resource id
    :type resource_id: int
    :return: Resource attributes
    :rtype: dict
    """
    if resource_id == 10:
        return {}
    if resource_id in [11, 12]:
        return {"service_tag": "hamster11"}
    return {"service_tag": "hamster{}".format(resource_id)}


class TestCalculateEnabledHamsters:
    """Tests for sandbox.projects.yabs.qa.hamster.utils.calculate_enabled_hamsters."""

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

    @pytest.mark.parametrize(["hamster_tags", "resource_ids", "expected"], [
        (
            ["hamster1", "hamster3", "hamster4", "hamster10"], [1, 2, 3, 10],
            {"hamster1": 1, "hamster3": 3}
        ),
    ])
    def test_calculate_enabled_hamsters(self, hamster_tags, resource_ids, expected):
        """Test if the enabled hamsters are returned correctly."""
        enabled_hamsters = calculate_enabled_hamsters(hamster_tags, resource_ids)
        assert enabled_hamsters == expected

    def test_invalid_resource_id_type(self):
        """Test if TypeError is raised when resource_id is not an integer."""
        with pytest.raises(TypeError):
            calculate_enabled_hamsters(["hamster1", "hamster3", "hamster10"], [1, 2, "10"])

    def test_ambiguous_endpoint_resources(self):
        """Test if AmbiguousEndpointResources is raised when there are more than one resource with the same tag."""
        with pytest.raises(AmbiguousEndpointResources):
            calculate_enabled_hamsters(["hamster1", "hamster11", "hamster12"], [1, 11, 12])

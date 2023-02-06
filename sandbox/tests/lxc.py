import pytest

from sandbox.common import config
from sandbox.client.platforms import lxc
from sandbox.common import system as common_system


class TestContainer(object):
    def test__container_name(self):
        port = config.Registry().client.port

        with pytest.raises(ValueError):
            lxc.Container(name="123")

        container = lxc.Container(name="123.5")
        assert container.template == "123"
        assert container.instance == "5"

        container = lxc.Container(name="{}.123.5".format(port))
        assert container.template == "{}.123".format(port)
        assert container.instance == "5"

        with pytest.raises(ValueError):
            container = lxc.Container(name="{}.123.5".format(port + 1))

        container = lxc.Container(name="privileged")
        assert container.template == "privileged"
        assert container.instance == "0"

        container = lxc.Container(name="{}.{}".format(port, "privileged"))
        assert container.template == "{}.privileged".format(port)
        assert container.instance == "0"

        with pytest.raises(ValueError):
            lxc.Container(name="{}.{}".format(port + 1, "privileged"))

    def test__lxc_route_list(self):
        """
        This binary-only test check, that pyroute2 library save IPRoute functionaluity during updates
        """
        if common_system.inside_the_binary():
            dev_name = "lo"
            lxc_net = lxc.LXCNetwork()
            assert len(list(lxc_net.lxc_route_table(dev_name))) == 1
            assert len(list(lxc_net.lxc_route_table(dev_name, global_only=False))) > 1

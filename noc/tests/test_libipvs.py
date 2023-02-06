"""pytest methods, that check libipvs.py modules:
- create/delete services/reals
- check Functions
"""

import pytest
import build.libipvs as libipvs


class TestClient(object):
    """Class cantains test methods for Client class libipvs.
    All test methods equal class methods without test_ keyword.
    """

    test_tree = {"2_10.0.0.1_65535_TCP_wrr_0": []}

    @pytest.yield_fixture
    def client(self):
        client = libipvs.Client()
        yield client

    def test_init_clean(self, client):
        client.tree = {}
        assert client.tree == {}, "Service().tree is not empty"

    def test_create_tree(self, client):
        client.tree = self.test_tree
        assert (
            client.tree == self.test_tree
        ), "Service.tree setter works uncorrect"

    def test_delete_tree(self, client):
        client.tree = self.test_tree
        assert client.tree == self.test_tree, "Cannot create IPVS tree"

        del client.tree
        assert client.tree == {}, "Client.tree wasn't deleted"


class TestService(object):
    """Class cantains test methods for Service class libipvs.
    All test methods equal class methods without test_ keyword.
    """

    test_service = "2_10.0.0.1_65535_TCP_wrr_0"
    test_reals = [
        "2_5.5.5.5_80_100_0_0_TUNNEL",
        "2_6.7.8.9_65535_55_0_0_TUNNEL",
    ]

    @pytest.yield_fixture
    def service(self):
        del libipvs.Client().tree
        yield libipvs.Service(self.test_service)
        del libipvs.Client().tree

    @pytest.yield_fixture
    def reals(self):
        yield [libipvs.Real(i) for i in self.test_reals]

    def test_init_clean(self, service):
        assert service.delete(), "Service.delete has returned False"
        assert service.tree == {}, "Service.tree is not empty after delete"

    def test_create_service(self, service):
        service.create()
        assert self.test_service in service.tree, (
            "Service %s doesn't exist after create" % self.test_service
        )

    def test_delete_service(self, service):
        service.create()
        assert self.test_service in service.tree, (
            "Service %s doesn't exist after create" % self.test_service
        )
        assert service.delete(), "Service.delete has returned False"
        assert service.tree == {}, "Service.tree is not empty after delete"


class TestReals(TestService):
    """Class cantains test methods for Functions class libipvs.
    All test methods equal class methods without test_ keyword.
    """

    def test_init_reals(self, reals):
        assert [
            x for x in reals if not isinstance(x, libipvs.Real)
        ] == [], "Not all object are Real class"

    def test_add_reals(self, service, reals):
        service.delete()
        service.create()
        assert service.tree == {self.test_service: []}, (
            "Service %s doesn't exist after create" % self.test_service
        )
        assert service.add_reals(
            reals
        ), "Received False while reals have added"
        assert (
            service.tree.get(self.test_service) == self.test_reals
        ), "Reals doesn't exist in IPVS tree after add_reals action"

    def test_add_to_service(self, service, reals):
        service.delete()
        service.create()
        for real in reals:
            assert real.add_to_service(
                service
            ), "Cannot link service with real"
        assert (
            service.tree.get(self.test_service) == self.test_reals
        ), "Reals doesn't exist in IPVS tree after add_to_service action"

    def test_del_reals(self, service, reals):
        self.test_add_reals(service, reals)
        assert service.del_reals(
            reals
        ), "Received False while reals have deleted"
        assert service.tree == {self.test_service: []}

    def test_delete_from_service(self, service, reals):
        self.test_add_to_service(service, reals)
        for real in reals:
            assert real.delete_from_service(
                service
            ), "Cannot unlink service with real"
        assert service.tree == {self.test_service: []}


class TestFunctions(object):
    """Class cantains test methods for Functions class libipvs.
    All test methods equal class methods without test_ keyword.
    """

    init_tree = {
        "2_10.0.0.1_65535_TCP_wrr_0": [
            "2_5.5.5.5_80_100_0_0_TUNNEL",
            "2_6.7.8.9_65535_55_0_0_TUNNEL",
        ],
        "2_172.16.0.1_80_TCP_wrr_0": ["2_11.12.13.14_80_1_0_0_TUNNEL"],
        "2_192.168.0.1_53_UDP_wlc_0": [],
    }

    new_tree = {
        "2_10.0.0.1_65535_TCP_wrr_0": ["2_6.7.8.9_65535_55_0_0_TUNNEL"],
        "2_172.16.0.1_80_TCP_wrr_0": [
            "2_172.16.0.14_80_1_0_0_TUNNEL",
            "2_11.12.13.14_80_1_0_0_TUNNEL",
        ],
        "2_192.168.168.168_5353_UDP_wlc_0": [],
    }

    test_diff = {
        "add_vs": {"2_192.168.168.168_5353_UDP_wlc_0": []},
        "del_vs": {"2_192.168.0.1_53_UDP_wlc_0": True},
        "add_rs": {
            "2_172.16.0.1_80_TCP_wrr_0": ["2_172.16.0.14_80_1_0_0_TUNNEL"]
        },
        "del_rs": {
            "2_10.0.0.1_65535_TCP_wrr_0": ["2_5.5.5.5_80_100_0_0_TUNNEL"]
        },
    }

    @pytest.yield_fixture
    def client(self):
        client = libipvs.Client()
        yield client
        del libipvs.Client().tree

    def test_get_trees_diff(self, client):
        client.tree = self.init_tree
        assert client.tree == self.init_tree, "Received wrong tree in setter"
        diff = libipvs.Functions.get_trees_diff(client.tree, self.new_tree)
        assert (
            diff == self.test_diff
        ), "Diff are different, get_services_tree work uncorrectly"
        del client.tree

    def test_check_trees_diff(self, client):
        client.tree = self.init_tree
        modified_diff = dict(self.test_diff)
        modified_diff["del_vs"] = {
            "2_0.0.0.1_1024_UDP_wlc_0": True,
            "2_192.168.0.1_53_UDP_wlc_0": True,
        }
        assert (
            modified_diff != self.test_diff
        ), "Modified diff and test_diff are equals"
        modified_diff = libipvs.Functions.check_trees_diff(modified_diff)
        assert (
            modified_diff == self.test_diff
        ), "Modified diff and test_diff are different after check_trees_diff"

    def test_apply_trees_diff(self, client):
        client.tree = self.init_tree
        assert libipvs.Functions.apply_trees_diff(
            self.test_diff
        ), "apply_trees_diff return False value"
        assert client.tree == self.new_tree
        assert (
            client.tree == self.new_tree
        ), "Different trees after apply changes"

    def test_get_services_tree(self, client):
        client.tree = self.init_tree
        service = libipvs.Functions.get_services_tree(client.tree, "10.0.0.1")
        assert len(service) == 1, "Wrong received filtering service length"
        assert service.get("2_10.0.0.1_65535_TCP_wrr_0") == client.tree.get(
            "2_10.0.0.1_65535_TCP_wrr_0"
        ), "Filtering service received wrong object"


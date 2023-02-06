import sys
from collections import defaultdict
from unittest.mock import MagicMock, patch

import yaml
from scripts import export_objects_to_conductor as eotc

sys.path.append("scripts")  # do not transform scripts into a package


def test_select_runner_my_turn():
    patch1 = patch("scripts.export_objects_to_conductor.socket.getfqdn",
                   return_value="host1.test")
    patch2 = patch(
        "scripts.export_objects_to_conductor.get_group_hosts_by_host",
        return_value=["host1.test", "host2.test", "host3.test"])
    patch3 = patch("scripts.export_objects_to_conductor.time.strftime",
                   return_value="3")
    patch1.start()
    patch2.start()
    patch3.start()
    assert eotc.identify_runner() is True
    patch1.stop()
    patch2.stop()
    patch3.stop()


def test_select_runner_not_my_turn():
    patch1 = patch("scripts.export_objects_to_conductor.socket.getfqdn",
                   return_value="host1.test")
    patch2 = patch(
        "scripts.export_objects_to_conductor.get_group_hosts_by_host",
        return_value=["host1.test", "host2.test", "host3.test"])
    patch3 = patch("scripts.export_objects_to_conductor.time.strftime",
                   return_value="2")
    patch1.start()
    patch2.start()
    patch3.start()
    assert eotc.identify_runner() is False
    patch1.stop()
    patch2.stop()
    patch3.stop()


def test_select_runner_no_neighbors():
    patch1 = patch("scripts.export_objects_to_conductor.socket.getfqdn",
                   return_value="host1.test")
    patch2 = patch(
        "scripts.export_objects_to_conductor.get_group_hosts_by_host",
        return_value=[])
    patch3 = patch("scripts.export_objects_to_conductor.time.strftime",
                   return_value="3")
    patch1.start()
    patch2.start()
    patch3.start()
    assert eotc.identify_runner() is False
    patch1.stop()
    patch2.stop()
    patch3.stop()


def test_create_subgroups():
    yamlstr = """
l3-balancers:
  types:
    common: mnt_traf
    project: mnt_traf
    nat: mnt_traf
    checker: mnt_traf
    cdn: mnt_traf
    cloud: cloud_tt_slb
    blocking: mnt_traf
    awapsftp: mnt_traf
  stages:
    - unstable
    - testing
    - prestable
    - stable
  prefix: balancer
tt-hypervisors:
  types:
    management: mnt_traf
    balancers: mnt_traf
  stages:
    - unstable
    - testing
    - prestable
    - stable
  prefix: ttkvm"""
    names = []
    yamldata = yaml.safe_load(yamlstr)
    patch1 = patch("scripts.export_objects_to_conductor.c_create_group",
                   return_value=True)
    patch1.start()
    for name, rt_predicate in eotc.create_subgroups("l3-balancers",
                                                    yamldata["l3-balancers"]):
        names.append(name)
        name_split = name.split("-")
        assert name_split[2] in rt_predicate
        assert name_split[3] in rt_predicate
    assert "l3-balancers-nat-testing" in names
    assert "l3-balancers-blocking-stable" in names
    assert len(names) == 32
    patch1.stop()


def test_create_subgroups_some_faults():
    yamlstr = """
l3-balancers:
  types:
    common: mnt_traf
    project: mnt_traf
    nat: mnt_traf
    checker: mnt_traf
    cdn: mnt_traf
    cloud: cloud_tt_slb
    blocking: mnt_traf
    awapsftp: mnt_traf
  stages:
    - unstable
    - testing
    - prestable
    - stable
  prefix: balancer
tt-hypervisors:
  types:
    management: mnt_traf
    balancers: mnt_traf
  stages:
    - unstable
    - testing
    - prestable
    - stable
  prefix: ttkvm"""
    names = []
    yamldata = yaml.safe_load(yamlstr)
    boolmix = 8 * [True]
    boolmix.extend(16 * [True, False])
    patch1 = patch("scripts.export_objects_to_conductor.c_create_group",
                   side_effect=boolmix)
    patch1.start()
    for name, _ in eotc.create_subgroups("l3-balancers",
                                         yamldata["l3-balancers"]):
        if name:
            names.append(name)
    assert "l3-balancers-nat-unstable" in names
    assert len(names) == 16
    patch1.stop()


def test_prepare_host_ok():
    all_hosts = defaultdict(lambda: {})
    assert eotc.prepare_host(all_hosts, "some.test", "TST",
                             "balancers-stable") is True
    assert len(all_hosts) == 1
    assert "some.test" in all_hosts
    assert all_hosts["some.test"]["dc"] == "TST"
    assert all_hosts["some.test"]["group"] == "balancers-stable"


def test_prepare_host_no_dc():
    all_hosts = defaultdict(lambda: {})
    assert eotc.prepare_host(all_hosts, "some.test", None,
                             "balancers-stable") is False
    assert len(all_hosts) == 0


def test_create_groups_update_hosts():
    removal_mock = MagicMock()
    create_mock = MagicMock()
    subgroups = [[("l3-balancers-common-unstable", "{some}")]]
    rt_hosts = [{"host1.test": [], "host2.test": [], "host3.test": []}]
    c_hosts = [["host2.test", "host3.test", "host4.test"]]
    create_call_arg = defaultdict(lambda: {})
    create_call_arg["host1.test"] = {
        "dc": "sas",
        "group": "l3-balancers-common-unstable"
    }
    create_call_arg["host2.test"] = {
        "dc": "sas",
        "group": "l3-balancers-common-unstable"
    }
    create_call_arg["host3.test"] = {
        "dc": "sas",
        "group": "l3-balancers-common-unstable"
    }
    patch1 = patch("scripts.export_objects_to_conductor.create_subgroups",
                   side_effect=subgroups)
    patch2 = patch("scripts.export_objects_to_conductor.get_hosts_from_rt",
                   side_effect=rt_hosts)
    patch3 = patch("scripts.export_objects_to_conductor.get_dc_by_etags",
                   return_value="sas")
    patch4 = patch("scripts.export_objects_to_conductor.remove_old_hosts",
                   new=removal_mock)
    patch5 = patch(
        "scripts.export_objects_to_conductor.create_or_update_hosts",
        new=create_mock)
    patch6 = patch(
        "scripts.export_objects_to_conductor.get_hosts_from_conductor",
        side_effect=c_hosts)
    patch1.start()
    patch2.start()
    patch3.start()
    patch4.start()
    patch5.start()
    patch6.start()
    eotc.create_groups_update_hosts("l3-balancers", {}, {})
    removal_mock.assert_called_with(set(["host4.test"]),
                                    "l3-balancers-common-unstable")
    create_mock.assert_called_with(create_call_arg)
    patch1.stop()
    patch2.stop()
    patch3.stop()
    patch4.stop()
    patch5.stop()
    patch6.stop()


def test_get_dc_by_etags_match():
    locations_map = {"Сасово": "sas", "Владимир": "vla", "Мытищи": "myt"}
    etags = {"15": {"tag": "i82599EB"}, "32": {"tag": "Сасово"}}
    result = eotc.get_dc_by_etags(etags, locations_map)
    assert result == "sas"


def test_get_dc_by_etags_no_match():
    locations_map = {"Сасово": "sas", "Владимир": "vla", "Мытищи": "myt"}
    etags = {"15": {"tag": "i82599EB"}, "32": {"tag": "Ивантеевка"}}
    assert not eotc.get_dc_by_etags(etags, locations_map)

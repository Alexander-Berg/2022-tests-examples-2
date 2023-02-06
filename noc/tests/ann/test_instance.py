import os
import typing
import datetime

import pytest
import rtapi

from checkist.ann.diff import DiffBase, DiffStats
from checkist.ann.instance import (
    ALL_GENS,
    AnnInstance,
    ConfigGenerationError,
    ConfigGenerationResult,
    GeneratorDiff,
    ProfileTiming,
    RuleBook,
    TimingType,
    UnifiedDiff,
    UnifiedResult,
    AnnCacher,
)
from settings import Settings

if typing.TYPE_CHECKING:
    from checkist.core import CheckistCore


UNIFIED_OUTPUT = {
    "fail": {
        "publab-u4.yndx.net": "Some\nTraceback\n",
    },
    "success": {
        "iva2-s57.yndx.net": {
            "is_pc": False,
            "all": {
                "diff": "  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n-   rule 56 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:CE2A:3D39/128\n+   rule 56 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n",  # noqa: E501
                "gen": "undo telnet server disable\nundo dhcp enable\nundo ntp server disable\nntp server disable\nntp ipv6 server disable\nntp unicast-server ipv6 2A02:6B8:B012:100F::1 vpn-instance MEth0/0/0\n",  # noqa: E501
                 "order": "port split mode\nport split dimension\nport split refresh\ndfs-group\nassign forward\nip vpn-instance */[Mm][Ee][Tt]h.*/\nip */(ip|ipv6)/-prefix\nip as-path-filter\nip community-filter\nip extcommunity-filter\ntunnel-policy\nroute-policy */VRF_.*/",  # noqa: E501
                "patch": "undo ftp ipv6 server enable\nundo ftp server enable\nundo dns resolve\nundo dns timeout 2\nundo dns server ipv6 2A02:6B8::1:1\n",
                "perf": {
                    "diff_and_patch": 1,
                    "diff_and_patch_safe": 2,
                    "total": 3,
                },
                "safe": {
                    "diff": "  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n-   rule 56 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:CE2A:3D39/128\n",  # noqa: E501
                    "patch": "acl ipv6 number 2710\n  undo rule 55\n  undo rule 56\n",
                },
                "after": [
                    "commit",
                    "q",
                    "save"
                ],
                "before": [
                    "system-view"
                ],
            },
            "per-generator": {
                "Peerings": {
                    "diff": "",
                    "gen": "undo telnet server disable\nundo dhcp enable\n",
                    "patch": "",
                    "perf": {
                        "diff_and_patch": 4,
                        "diff_and_patch_safe": 5,
                        "rt": {
                            "get_object_info": [
                                {
                                    "op": "memory",
                                    "time": 6,
                                }
                            ],
                            "get_object_laggs": [
                                {
                                    "op": "disk_read",
                                    "time": 7,
                                }
                            ]
                        },
                        "total": 8,
                    },
                    "safe": {
                        "diff": "",
                        "patch": "",
                    },
                    "tags": [
                        "peerings",
                    ]
                },
                "SnmpAcl": {
                    "diff": "  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n",  # noqa: E501
                    "gen": "undo telnet server disable\nundo dhcp enable\nundo ntp server disable\n",
                    "patch": "acl ipv6 number 2710\n  undo rule 55\n  undo rule 56\n  undo rule 57\n",
                    "perf": {
                        "diff_and_patch": 9,
                        "diff_and_patch_safe": 10,
                        "rt": {
                            "get_named_pl": [
                                {
                                    "op": "disk_write",
                                    "time": 11,
                                }
                            ]
                        },
                        "total": 12,
                    },
                    "safe": {
                        "diff": "  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n",  # noqa: E501
                        "patch": "acl ipv6 number 2710\n  undo rule 55",
                    },
                    "tags": [
                        "snmp",
                        "snmp_acl",
                        "mgmt",
                    ]
                },
            },
        },
        "sas2-131s76.yndx.net": {
            "is_pc": True,
            "all": {
                "diff": "",
                "gen": "",
                "order": "",
                "patch": "",
                "perf": {
                    "diff_and_patch": 13,
                    "diff_and_patch_safe": 14,
                    "total": 15,
                },
                "before": [
                    "etckeeper check"
                ],
                "after": [
                    "etckeeper commitreload"
                ],
            },
            "per-generator": {
                "CumulusCopp": {
                    "diff": "",
                    "is_safe": True,
                    "output": "[ip6tables]\n-A INPUT --in-interface eth0 -j ACCEPT\n-A INPUT --in-interface lo -j ACCEPT\n-A INPUT --in-interface mgmt -j ACCEPT\n-A INPUT -p tcp --dport 20 -j DROP",
                    "path": "/etc/cumulus/acl/policy.d/mgmt.rules",
                    "perf": {
                        "diff_and_patch": 16,
                        "rt": {},
                        "total": 17,
                    },
                    "reload": "",
                    "tags": [
                        "cumulus",
                        "qos",
                        "copp",
                    ],
                },
            },
        },
        "kiv-decap1.yndx.net": {
            "all": {
                "after": [],
                "before": [],
                "diff": "",
                "gen": "",
                "order": "",
                "patch": "",
                "perf": {}
            },
            "is_pc": True,
            "per-generator": {
                "Telegraf": {
                    "diff": "--- \n+++ \n@@ -0,0 +1,29 @@\n+# generated by annushka\n+\n+[agent]\n",
                    "is_safe": False,
                    "output": "# generated by annushka\n\n[agent]\n",
                    "path": "/etc/telegraf/telegraf.d/annushka.conf",
                    "perf": {
                        "diff_and_patch": 2.6917000000459268e-05
                    },
                    "reload": "sudo service telegraf restart",
                    "tags": [
                        "telegraf",
                        "telegraf.conf"
                    ]
                },
                "YaBird": {
                    "diff": "--- \n+++ \n@@ -0,0 +1,390 @@\n+router id 141.8.136.166;\n",
                    "is_safe": False,
                    "output": "router id 141.8.136.166;\n",
                    "path": "/etc/bird/bird.conf",
                    "perf": {
                        "diff_and_patch": 0.00018170800000039122
                    },
                    "reload": "",
                    "tags": [
                        "yabird"
                    ]
                }
            }
        }
    },
}
EXPECTED_UNIFIED_RESULT = UnifiedResult(
    diffs=[
        UnifiedDiff(
            device_name="iva2-s57",
            after=[
                "commit",
                "q",
                "save"
            ],
            before=["system-view"],
            gen_diffs=[
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text="  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n-   rule 56 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:CE2A:3D39/128\n+   rule 56 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n",  # noqa: E501
                        patch_text="undo ftp ipv6 server enable\nundo ftp server enable\nundo dns resolve\nundo dns timeout 2\nundo dns server ipv6 2A02:6B8::1:1\n",
                        global_stats=DiffStats(added=2, removed=2),
                        effective_stats=DiffStats(added=2, removed=2),
                        vendor="",
                        reload="",
                    ),
                    generator=ALL_GENS,
                    tags=[],
                    acl_safe=False,
                ),
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text="  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n-   rule 56 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:CE2A:3D39/128\n",  # noqa: E501
                        patch_text="acl ipv6 number 2710\n  undo rule 55\n  undo rule 56\n",
                        global_stats=DiffStats(added=1, removed=2),
                        effective_stats=DiffStats(added=1, removed=2),
                        vendor="",
                        reload="",
                    ),
                    generator=ALL_GENS,
                    tags=[],
                    acl_safe=True,
                ),
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text="  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n",  # noqa: E501
                        patch_text="acl ipv6 number 2710\n  undo rule 55\n  undo rule 56\n  undo rule 57\n",
                        global_stats=DiffStats(added=1, removed=1),
                        effective_stats=DiffStats(added=1, removed=1),
                        vendor="",
                        reload="",
                    ),
                    generator="SnmpAcl",
                    tags=["snmp", "snmp_acl", "mgmt"],
                    acl_safe=False,
                ),
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text="  acl ipv6 number 2710\n-   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:F86:0:675:5EC9:7486/128\n+   rule 55 permit vpn-instance MEth0/0/0 source 2A02:6B8:C02:756:0:675:FCED:4A8B/128\n",  # noqa: E501
                        patch_text="acl ipv6 number 2710\n  undo rule 55",
                        global_stats=DiffStats(added=1, removed=1),
                        effective_stats=DiffStats(added=1, removed=1),
                        vendor="",
                        reload="",
                    ),
                    generator="SnmpAcl",
                    tags=["snmp", "snmp_acl", "mgmt"],
                    acl_safe=True,
                ),
            ],
            conf_hash=""
        ),
        UnifiedDiff(
            device_name="sas2-131s76",
            after=["etckeeper commitreload"],
            before=["etckeeper check"],
            gen_diffs=[
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text={"/etc/cumulus/acl/policy.d/mgmt.rules": ""},
                        patch_text={"/etc/cumulus/acl/policy.d/mgmt.rules": "[ip6tables]\n-A INPUT --in-interface eth0 -j ACCEPT\n-A INPUT --in-interface lo -j ACCEPT\n-A INPUT --in-interface mgmt -j ACCEPT\n-A INPUT -p tcp --dport 20 -j DROP"},  # noqa: E501
                        global_stats=DiffStats(added=0, removed=0),
                        effective_stats=DiffStats(added=0, removed=0),
                        vendor="",
                        reload="",
                    ),
                    generator="CumulusCopp",
                    tags=["cumulus", "qos", "copp"],
                    acl_safe=True,
                ),
            ],
            conf_hash=""
        ),
        UnifiedDiff(
            device_name="kiv-decap1",
            after=[],
            before=[],
            gen_diffs=[
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text={"/etc/telegraf/telegraf.d/annushka.conf": "--- \n+++ \n@@ -0,0 +1,29 @@\n+# generated by annushka\n+\n+[agent]\n"},
                        patch_text={"/etc/telegraf/telegraf.d/annushka.conf": "# generated by annushka\n\n[agent]\n"},
                        global_stats=DiffStats(added=3, removed=0),
                        effective_stats=DiffStats(added=3, removed=0),
                        vendor="",
                        reload="sudo service telegraf restart",
                    ),
                    generator="Telegraf",
                    tags=["telegraf", "telegraf.conf"],
                    acl_safe=False,
                ),
                GeneratorDiff(
                    diff=DiffBase(
                        diff_text={"/etc/bird/bird.conf": "--- \n+++ \n@@ -0,0 +1,390 @@\n+router id 141.8.136.166;\n"},
                        patch_text={"/etc/bird/bird.conf": "router id 141.8.136.166;\n"},
                        global_stats=DiffStats(added=1, removed=0),
                        effective_stats=DiffStats(added=1, removed=0),
                        vendor="",
                        reload="",
                    ),
                    generator="YaBird",
                    tags=["yabird"],
                    acl_safe=False,
                ),
            ],
            conf_hash=""
        ),
    ],
    configs=[ConfigGenerationResult(
        device_name="iva2-s57",
        config="undo telnet server disable\nundo dhcp enable\nundo ntp server disable\nntp server disable\nntp ipv6 server disable\nntp unicast-server ipv6 2A02:6B8:B012:100F::1 vpn-instance MEth0/0/0\n",  # noqa: E501
    )],
    rulebooks=[RuleBook(
        device_name="iva2-s57",
        order="port split mode\nport split dimension\nport split refresh\ndfs-group\nassign forward\nip vpn-instance */[Mm][Ee][Tt]h.*/\nip */(ip|ipv6)/-prefix\nip as-path-filter\nip community-filter\nip extcommunity-filter\ntunnel-policy\nroute-policy */VRF_.*/"  # noqa: E501
    )],
    errors=[ConfigGenerationError(device_name="publab-u4", error="Some\nTraceback\n")],
    profile=[
        ProfileTiming(
            value=3,
            device_name="iva2-s57",
            generator=ALL_GENS,
            git_commit_id="master",
            timing_type=TimingType.total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=1,
            device_name="iva2-s57",
            generator=ALL_GENS,
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=8,
            device_name="iva2-s57",
            generator="Peerings",
            git_commit_id="master",
            timing_type=TimingType.total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=4,
            device_name="iva2-s57",
            generator="Peerings",
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=6,
            device_name="iva2-s57",
            generator="Peerings",
            git_commit_id="master",
            timing_type=TimingType.rt_func,
            rt_func="get_object_info",
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=7,
            device_name="iva2-s57",
            generator="Peerings",
            git_commit_id="master",
            timing_type=TimingType.rt_func,
            rt_func="get_object_laggs",
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=13.0,
            device_name="iva2-s57",
            generator="Peerings",
            git_commit_id="master",
            timing_type=TimingType.rt_total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=12,
            device_name="iva2-s57",
            generator="SnmpAcl",
            git_commit_id="master",
            timing_type=TimingType.total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=9,
            device_name="iva2-s57",
            generator="SnmpAcl",
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=11,
            device_name="iva2-s57",
            generator="SnmpAcl",
            git_commit_id="master",
            timing_type=TimingType.rt_func,
            rt_func="get_named_pl",
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=11.0,
            device_name="iva2-s57",
            generator="SnmpAcl",
            git_commit_id="master",
            timing_type=TimingType.rt_total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=15,
            device_name="sas2-131s76",
            generator=ALL_GENS,
            git_commit_id="master",
            timing_type=TimingType.total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=13,
            device_name="sas2-131s76",
            generator=ALL_GENS,
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=17,
            device_name="sas2-131s76",
            generator="CumulusCopp",
            git_commit_id="master",
            timing_type=TimingType.total,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=16,
            device_name="sas2-131s76",
            generator="CumulusCopp",
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host=rtapi.default_server,
            ci_mode="0",
        ),
        ProfileTiming(
            value=2.6917000000459268e-05,
            device_name="kiv-decap1",
            generator="Telegraf",
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host="ro.racktables.yandex.net",
            ci_mode="0",
        ),
        ProfileTiming(
            value=0.00018170800000039122,
            device_name="kiv-decap1",
            generator="YaBird",
            git_commit_id="master",
            timing_type=TimingType.diff_and_patch,
            rt_func=None,
            rt_host="ro.racktables.yandex.net",
            ci_mode="0"
        ),
    ],
)


@pytest.mark.asyncio
async def test_parse_checkist_unified_output():
    instance = AnnInstance(git_commit_id="master", settings=Settings())
    assert await instance._parse_checkist_unified_output(
        data=UNIFIED_OUTPUT,
        config_source="/tmp/config_dir",
        calculate_conf_hash=False,
        ci_mode=False,
        rtapi_env=None,
        per_generator_perf=True,
    ) == EXPECTED_UNIFIED_RESULT


@pytest.mark.asyncio
async def test_ann_cacher_add_ann(core: "CheckistCore"):
    created_files = [
        "ann.py",
        "annushka/generators/__init__.py",
    ]
    ann_cacher = AnnCacher(core)
    instance = AnnInstance(git_commit_id="master", settings=core.settings)
    instance._commit_hash = "5e57926d8be0688e64588448421d7c0db93a4a4a"
    instance._dirname = os.path.join(core.settings.tmpdir, "annushka")
    os.makedirs(instance.dirname, exist_ok=True)
    open(os.path.join(instance.dirname, AnnInstance.commit_hash_filename), "w").write("")
    for f in created_files:
        path = os.path.join(instance.dirname, f)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w").write("")

    await ann_cacher.add_ann(instance)

    cache_dir = os.path.join(core.settings.annushka.cache_path, instance._commit_hash)
    assert os.path.exists(cache_dir)
    for f in created_files:
        assert os.path.exists(os.path.join(cache_dir, f))


@pytest.mark.asyncio
async def test_ann_cacher_find_ann(core: "CheckistCore"):
    ann_cacher = AnnCacher(core)
    commit_hash = "5e57926d8be0688e64588448421d7c0db93a4a4a"
    instance_dir = os.path.join(core.settings.annushka.cache_path, commit_hash)
    ann_instance = ann_cacher.find_ann(commit_hash)
    assert not ann_instance

    os.makedirs(os.path.join(instance_dir), exist_ok=True)
    open(os.path.join(instance_dir, AnnInstance.commit_hash_filename), "w").write(commit_hash)
    ann_instance = ann_cacher.find_ann(commit_hash)
    assert ann_instance
    assert ann_instance.get_commit_hash() == commit_hash
    assert ann_instance.dirname == instance_dir


@pytest.mark.asyncio
async def test_ann_cacher_rotate_ann(core: "CheckistCore"):
    cache_ttl = datetime.timedelta(days=1)
    core.settings.annushka.cache_ttl = cache_ttl
    ann_cacher = AnnCacher(core)
    commit_hash = "5e57926d8be0688e64588448421d7c0db93a4a4a"
    instance_dir = os.path.join(core.settings.annushka.cache_path, commit_hash)

    os.makedirs(os.path.join(instance_dir), exist_ok=True)
    os.makedirs(os.path.join(instance_dir, "annushka"), exist_ok=True)
    open(os.path.join(instance_dir, AnnInstance.commit_hash_filename), "w").write(commit_hash)
    open(os.path.join(instance_dir, "annushka", "ann.py"), "w").write(commit_hash)

    await ann_cacher.rotate_ann()
    assert ann_cacher.find_ann(commit_hash)
    assert os.path.exists(instance_dir)

    # Старим директорию с кешом ровно на ttl
    now = datetime.datetime.now()
    expired_at = now - cache_ttl
    os.utime(instance_dir, times=(now.timestamp(), expired_at.timestamp()))

    await ann_cacher.rotate_ann()
    assert not ann_cacher.find_ann(commit_hash)
    assert not os.path.exists(instance_dir)

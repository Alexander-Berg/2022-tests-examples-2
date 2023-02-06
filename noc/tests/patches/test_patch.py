import pytest

from checkist.patches.patch import Patch, PatchFile, PatchMeta


@pytest.mark.parametrize("dct, res", (
    ({"hostname": "noc-sas", "config_md5": "bac123"}, PatchMeta("noc-sas", "bac123")),
))
def test_patch_meta_from_dict(dct, res):
    assert PatchMeta.from_dict(dct) == res


@pytest.mark.parametrize("dct, res", (
    (
        {
            "hostname": "noc-myt",
            "patch": {"": "my patch"},
            "run_config_hash": "a7446e8c318d900d4fe0c349aaaa4754",
            "run_before": 123456,
            "run_after": 654321,
            "before": ["conf t"],
            "after": ["exit", "write"],
            "reloads": {}
        },
        Patch("noc-myt", "conf t\nmy patch\nexit\nwrite", [], "a7446e8c318d900d4fe0c349aaaa4754", 123456, 654321, None),
    ),
    (
        {
            "hostname": "noc-sas",
            "patch": {
                "/tmp/a": "bb",
            },
            "run_config_hash": "a7446e8c318d900d4fe0c349aaaa4754",
            "before": [],
            "after": [],
            "reloads": {
                "/tmp/a": "system restart a",
            },
        },
        Patch("noc-sas", "", [PatchFile("/tmp/a", "bb", [], ["system restart a"])], "a7446e8c318d900d4fe0c349aaaa4754", None, None, None),
    ),
    (
        {
            "hostname": "noc-sas",
            "patch_text": {
                "/tmp/a": "bb",
            },
            "run_config_hash": "a7446e8c318d900d4fe0c349aaaa4754",
            "before": ["etckeeper check"],
            "after": ["etckeeper commitreload"],
            "reloads": {
                "/tmp/a": "system restart a",
            },
        },
        Patch("noc-sas", "", [PatchFile("/tmp/a", "bb", ["etckeeper check"], ["system restart a", "etckeeper commitreload"])], "a7446e8c318d900d4fe0c349aaaa4754", None, None, None),
    ),
    (
        {
            "hostname": "noc-myt",
            "patch_text": {"": "my patch"},
            "run_config_hash": "a7446e8c318d900d4fe0c349aaaa4754",
            "run_before": 123456,
            "run_after": 654321,
            "object_id": 123,
            "before": ["conf t"],
            "after": ["exit", "write"],
            "reloads": {}
        },
        Patch("noc-myt", "conf t\nmy patch\nexit\nwrite", [], "a7446e8c318d900d4fe0c349aaaa4754", 123456, 654321, 123),
    ),
))
def test_patch_from_dict(dct, res):
    assert Patch.from_dict(dct) == res

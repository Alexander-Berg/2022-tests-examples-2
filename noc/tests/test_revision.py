import os
import tempfile
from unittest import mock


import pytest

import checkist.ann.revision
from checkist.ann.instance import (
    ConfigGenerationError,
    ConfigGenerationResult,
    DiffBase,
    DiffStats,
    RuleBook,
    GeneratorDiff,
    UnifiedDiff,
    UnifiedResult,
    ALL_GENS
)
from checkist.models.device import Device


@pytest.fixture
async def revision_with_files(core):
    rev = checkist.ann.revision.Revision(core, id="xxxxxxxxxxxxxxxxx")
    core.devices.get_devices = mock.AsyncMock(return_value=[
        Device(1, 100, "device1", "device1.yndx.net", None, None, None, "huawei", None, False, True),
        Device(2, 200, "device2", "device2.yndx.net", None, None, None, "cisco", None, False, True),
        Device(3, 300, "device3", "device3.yndx.net", None, None, None, "pc", None, False, True),
    ])
    await uresult_upload(rev, uresult("device1", "device1 config", [], []))
    await uresult_upload(rev, uresult("device2", "", [], ["device2 error"]))
    await uresult_upload(rev, uresult("device3", "", [{"/etc/network/interfaces": "device3 whitebox interfaces config"}], []))
    await uresult_upload(rev, uresult("device3", "", [{"/etc/snmp/snmpd.conf": "device3 whitebox snmpd config"}], []))
    return rev


@pytest.mark.asyncio
async def test_revision_create_new_rev(core, ann_instance):
    rev = await checkist.ann.revision.Revision.create_new_rev(
        core=core,
        ann_instance=ann_instance,
        base_rtcache_id="xxxxxxxxxxxxxxxxxx",
        allow_amend=False,
        ttl=3600,
        auto_approve=False,
    )
    saved_rev = await rev.find_by_id(core, rev.id)
    assert rev.id == saved_rev.id


@pytest.mark.asyncio
async def test_revision_upload_configs(core):
    rev = checkist.ann.revision.Revision(core, id="xxxxxxxxxxxxxxxxx")
    with tempfile.TemporaryDirectory() as temp_dir:
        errors_dir = os.path.join(temp_dir, "errors")
        os.mkdir(errors_dir)
        # сгенерированный конфиг
        open(os.path.join(temp_dir, "device1.cfg"), "w").write("device1 config")
        # ошибка генерации
        open(os.path.join(errors_dir, "device2.cfg"), "w").write("device2 error")
        # конфиг вайтбокса
        os.mkdir(os.path.join(temp_dir, "device3.cfg"))
        os.makedirs(os.path.join(temp_dir, "device3.cfg", "etc", "network"))
        open(os.path.join(temp_dir, "device3.cfg", "etc", "network", "interfaces"), "w").write("device3 whitebox interfaces config")
        os.makedirs(os.path.join(temp_dir, "device3.cfg", "etc", "snmp"))
        open(os.path.join(temp_dir, "device3.cfg", "etc", "snmp", "snmpd.conf"), "w").write("device3 whitebox snmpd config")
        await rev.upload_configs(temp_dir)
    await rev.update_files()
    assert rev.files == ["device1.cfg", "device3.cfg/etc/network/interfaces", "device3.cfg/etc/snmp/snmpd.conf"]
    await rev.update_errors()
    assert rev.errors == [checkist.ann.revision.ConfigGenerationError(device_name="device2.cfg", error="device2 error")]


@pytest.mark.asyncio
async def test_revision_upload_config_double_call(core):
    rev = checkist.ann.revision.Revision(core, id="xxxxxxxxxxxxxxxxx")
    with tempfile.TemporaryDirectory() as temp_dir:
        open(os.path.join(temp_dir, "device1.cfg"), "w").write("device1 config")
        await rev.upload_configs(temp_dir)
    await rev.update_files()
    assert rev.files == ["device1.cfg"]
    await rev.update_files()
    assert rev.files == ["device1.cfg"]


@pytest.mark.asyncio
async def test_revision_upload_removed(core):
    rev = checkist.ann.revision.Revision(core, id="xxxxxxxxxxxxxxxxx", files=["device1.cfg"])
    assert rev.files == ["device1.cfg"]
    await rev.update_files()
    assert rev.files == []


@pytest.mark.asyncio
async def test_revision_remove_for_hostnames(revision_with_files):
    async def up(rev):
        await rev.update_files()
        await rev.update_diffs()
        await rev.update_generators_list()
        await rev.update_errors()

    rev: checkist.ann.revision.Revision = revision_with_files
    # ничего не удалили
    await rev.remove_for_hostnames([])
    await up(rev)
    assert rev.files == [
        "device1.cfg",
        "device3.cfg/etc/network/interfaces",
        "device3.cfg/etc/snmp/snmpd.conf",
    ]
    assert rev.diffs == ["device1.cfg", "device3.cfg/etc/network/interfaces", "device3.cfg/etc/snmp/snmpd.conf"]
    assert rev.errors == [ConfigGenerationError(device_name="device2.cfg", error="device2 error")]

    await rev.remove_for_hostnames(["device1"])
    await up(rev)
    assert rev.files == [
        "device3.cfg/etc/network/interfaces",
        "device3.cfg/etc/snmp/snmpd.conf",
    ]
    assert rev.diffs == ["device3.cfg/etc/network/interfaces", "device3.cfg/etc/snmp/snmpd.conf"]
    assert rev.errors == [ConfigGenerationError(device_name="device2.cfg", error="device2 error")]

    await rev.remove_for_hostnames(["device3"])
    await up(rev)
    assert rev.files == []
    assert rev.diffs == []
    assert rev.errors == [ConfigGenerationError(device_name="device2.cfg", error="device2 error")]

    await rev.remove_for_hostnames(["device2"])
    await up(rev)
    assert rev.files == []
    assert rev.diffs == []
    assert rev.errors == []

    # catch-all, мы зачистили все устройства, больше файлов быть не должно
    left_files = [f async for f in rev._file_storage().find({})]
    assert left_files == []


def test_cfg_from_hostname():
    assert checkist.ann.revision.cfg_from_hostname("device1") == "device1.cfg"


def test_hostname_from_cfg():
    assert checkist.ann.revision.hostname_from_cfg("device1.cfg") == "device1"
    assert checkist.ann.revision.hostname_from_cfg("device3.cfg/etc/network/interfaces") == "device3"
    with pytest.raises(ValueError):
        checkist.ann.revision.hostname_from_cfg("device1")


@pytest.mark.asyncio
async def test_revision_files_for_hosts(revision_with_files):
    rev = revision_with_files
    files = await rev.files_for_hosts([])
    assert files == []
    files = await rev.files_for_hosts(["device1"])
    assert files == ["device1.cfg", "device1.cfg/Gen1.anngen", "device1.order"]
    files = await rev.files_for_hosts(["device1", "device3"])
    assert files == ["device1.cfg", "device1.cfg/Gen1.anngen", "device1.order", "device3.cfg/etc/network/interfaces", "device3.cfg/etc/snmp/snmpd.conf"]
    files = await rev.files_for_hosts(["device2"])
    assert files == ["errors/device2.cfg"]


@pytest.mark.asyncio
async def test_revision_hosts_for_files(revision_with_files: checkist.ann.revision.Revision):
    hosts = await revision_with_files.hosts_for_files([])
    assert hosts == []
    hosts = await revision_with_files.hosts_for_files(["device1.cfg"])
    assert hosts == ["device1"]
    hosts = await revision_with_files.hosts_for_files([
        "device1.cfg",
        "device3.cfg/etc/network/interfaces",
        "device3.cfg/etc/snmp/snmpd.conf"
    ])
    assert hosts == ["device1", "device3"]


@pytest.mark.asyncio
async def test_merge_revisions(core, revision_with_files: checkist.ann.revision.Revision):
    merge_into = revision_with_files
    merge_from = checkist.ann.revision.Revision(core, id="yyyyyyyyyyyyyyy")
    await uresult_upload(merge_from, uresult("device1", "", [], ["device1 error"]))
    await uresult_upload(merge_from, uresult("device2", "device2 config", [], []))
    await uresult_upload(merge_from, uresult("device3", "", [{"/etc/snmp/snmpd.conf": "updated snmpd config"}], []))

    await checkist.ann.revision.merge_revision(core, merge_into, merge_from)

    merged = await checkist.ann.revision.Revision.find_by_id(core, merge_into.id)
    assert merged
    assert merged.files == [
        "device2.cfg",
        "device3.cfg/etc/snmp/snmpd.conf",
    ]
    assert merged.errors == [
        checkist.ann.revision.ConfigGenerationError("device1.cfg", "device1 error"),
    ]
    assert merged.diffs == [
        "device2.cfg",
        "device3.cfg/etc/snmp/snmpd.conf",
    ]


async def uresult_upload(rev: checkist.ann.revision.Revision, ures: UnifiedResult):
    def update_hostnames(rev, hostnames):
        result = set(rev.hostnames).union(hostnames)
        rev.hostnames = list(result)
        rev.hostnames.sort()
    update_hostnames(rev, [x.device_name for x in ures.configs])
    update_hostnames(rev, [x.device_name for x in ures.diffs])
    update_hostnames(rev, [x.device_name for x in ures.rulebooks])
    update_hostnames(rev, [x.device_name for x in ures.errors])
    await rev.upload_unified_result(ures)
    await rev.update_files()
    await rev.update_diffs()
    await rev.update_generators_list()
    await rev.update_errors()
    await rev.save()


def uresult(hostname, config, files, errors):
    stats = DiffStats(1, 2)
    configs = []
    gen_diffs = []
    rulebooks = []
    errors = [
        ConfigGenerationError(hostname, error)
        for error in errors
    ]
    if config:
        configs = [ConfigGenerationResult(hostname, config)]
        rulebooks = [RuleBook(hostname, f"{hostname} order")]
        gen_diffs = [
            GeneratorDiff(
                diff=DiffBase(config, config, stats, stats, "huawei", ""),
                generator="Gen1",
                tags=["gen1"],
                acl_safe=False,
            ),
            GeneratorDiff(
                diff=DiffBase(config, config, stats, stats, "huawei", ""),
                generator=ALL_GENS,
                tags=[],
                acl_safe=False,
            )
        ]
    elif files:
        gen_diffs = [
            GeneratorDiff(
                diff=DiffBase(file, file, stats, stats, "pc", f"service gen{i} restart"),
                generator=f"Gen{i}",
                tags=["gen", f"gen{i}"],
                acl_safe=False,
            )
            for i, file in enumerate(files)
        ]
    return UnifiedResult(
        diffs=[
            UnifiedDiff(
                device_name=hostname,
                gen_diffs=gen_diffs,
                conf_hash=f"{hostname}-conf-hash-xxxx",
                before=[],
                after=[],
            )
        ],
        configs=configs,
        rulebooks=rulebooks,
        errors=errors,
        profile=[],
    )

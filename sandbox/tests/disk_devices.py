import pytest

from sandbox.deploy import disk_devices as disk_devices
import sandbox.deploy.utils as utils
import __builtin__


class BinaryIoMock(object):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MdStatMock(BinaryIoMock):
    @staticmethod
    def readlines():
        proc_mdstat = [
            "Personalities : [raid0] [linear] [multipath] [raid1] [raid6] [raid5] [raid4] [raid10]",
            "md2 : active raid0 sdc3[2] sdd3[3] sdg3[6] sdf3[5] sde3[4] sdh3[7] sda3[0] sdb3[1]",
            "7072538624 blocks super 1.2 256k chunks",
            "md1 : active raid0 sdg2[6] sdh2[7] sde2[4] sdf2[5] sdc2[2] sdd2[3] sdb2[1] sda2[0]",
            "419168256 blocks super 1.2 256k chunks"
        ]
        return proc_mdstat

    def read(self):
        pass


class MdStatMockNvmeRaid(BinaryIoMock):
    @staticmethod
    def readlines():
        proc_mdstat = [
            "Personalities : [raid0] [raid10] [linear] [multipath] [raid1] [raid6] [raid5] [raid4]",
            "md1 : active raid10 sdb2[1] sda2[0]",
            "15624683520 blocks super 1.2 2 near-copies [2/2] [UU]",
            "bitmap: 6/117 pages [24KB], 65536KB chunk",
            "md2 : active raid0 nvme1n1p2[1] nvme0n1p2[0]",
            "6248841216 blocks super 1.2 256k chunks"
        ]
        return proc_mdstat

    def read(self):
        pass


class RotationalMockSsd(BinaryIoMock):
    @staticmethod
    def read():
        return "0"


class RotationalMockHdd(BinaryIoMock):
    @staticmethod
    def read():
        return "1"


def mock_df_output(monkeypatch, device_name):
    foo = [
        "Filesystem      1K-blocks       Used  Available Use% Mounted on",
        "{}       7016814680 4899552100 1763619268  74% /place".format(device_name)
    ]
    monkeypatch.setattr(utils, "check_output", lambda _: iter(foo))


def mock_builtin_open_ssd(filename):
    if filename == "/proc/mdstat":
        return MdStatMock()
    elif filename.startswith("/sys/block/"):
        return RotationalMockSsd()
    return BinaryIoMock()


def mock_builtin_open_nvme(filename):
    if filename == "/proc/mdstat":
        return MdStatMockNvmeRaid()
    elif filename.startswith("/sys/block/"):
        return RotationalMockSsd()
    return BinaryIoMock()


def mock_builtin_open_hdd(filename):
    if filename == "/proc/mdstat":
        return MdStatMock()
    elif filename.startswith("/sys/block/"):
        return RotationalMockHdd()
    return BinaryIoMock()


class TestDiskDevices(object):
    @pytest.mark.parametrize("device_name", ["/dev/md2", "/dev/foo1"])
    def test__parse_linux_ssd(self, monkeypatch, device_name):
        mock_df_output(monkeypatch, device_name)
        monkeypatch.setattr(__builtin__, "open", mock_builtin_open_ssd)
        tags = set(disk_devices.Parser.parse_linux("/place/sandbox-data/tasks"))
        assert tags == {"SSD"}

    @pytest.mark.parametrize("device_name", ["/dev/md2", "/dev/foo2"])
    def test__parse_linux_hdd(self, monkeypatch, device_name):
        mock_df_output(monkeypatch, device_name)
        monkeypatch.setattr(__builtin__, "open", mock_builtin_open_hdd)
        tags = set(disk_devices.Parser.parse_linux("/place/sandbox-data/tasks"))
        assert tags == {"HDD"}

    def test__parse_linux_nvme_raid(self, monkeypatch):
        mock_df_output(monkeypatch, "/dev/md2")
        monkeypatch.setattr(__builtin__, "open", mock_builtin_open_nvme)
        tags = set(disk_devices.Parser.parse_linux("/place/sandbox-data/tasks"))
        assert tags == {"SSD"}

    def test__parse_linux_nvme(self, monkeypatch):
        mock_df_output(monkeypatch, "/dev/nvme0n1p2")
        monkeypatch.setattr(__builtin__, "open", mock_builtin_open_ssd)
        tags = set(disk_devices.Parser.parse_linux("/place/sandbox-data/tasks"))
        assert tags == {"SSD"}

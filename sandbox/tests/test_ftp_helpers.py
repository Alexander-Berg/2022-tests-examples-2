from sandbox.projects.masstransit.MapsMasstransitImportVehicleTasks.ftp_helpers import (
    parse_microsoft_dir_entry,
    parse_unix_dir_entry
)
from datetime import datetime


def test_parse_microsoft_dir_entry():
    result = parse_microsoft_dir_entry("02-21-20  11:19AM       <DIR>          FTP-ISRPD")
    assert result.name == "FTP-ISRPD"
    assert result.is_dir is True
    assert result.modification_time == datetime(2020, 02, 21, 11, 19)


def test_parse_unix_dir_entry_with_year():
    result = parse_unix_dir_entry("-rwxrwxrwx   1 owner    group   1708252896 Apr  2  2019 filename")
    assert result.name == "filename"
    assert result.is_dir is False
    assert result.modification_time == datetime(2019, 04, 02)


def test_parse_unix_dir_entry_with_time():
    result = parse_unix_dir_entry("drwxrwxrwx   1 owner    group            0 Apr 21 15:53 dirname with spaces", 2020)
    assert result.name == "dirname with spaces"
    assert result.is_dir is True
    assert result.modification_time == datetime(2020, 04, 21, 15, 53)


def test_parse_unix_dir_entry_leap_year():
    result = parse_unix_dir_entry("drwxrwxrwx   1 owner    group            0 Feb 29 23:30 dirname", 2020)
    assert result.name == "dirname"
    assert result.is_dir is True
    assert result.modification_time == datetime(2020, 02, 29, 23, 30)

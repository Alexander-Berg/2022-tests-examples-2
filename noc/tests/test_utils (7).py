import shelve
from pathlib import Path, PurePath
from time import time
from unittest.mock import Mock, patch

import pytest
from tt_main.utils import (
    get_check_name,
    is_check_disabled,
    is_contains_rt_tag,
    read_from_cache,
    retry_func_with_status,
    strip_mask,
    write_to_cache,
)

CACHE_FILE = "/tmp/test_tt_main_utils_cache"
CACHE_KEY = "test"


@pytest.fixture
def clear_cache():
    p = Path("/") / PurePath(CACHE_FILE).parent
    filename = PurePath(CACHE_FILE).name
    some_files_deleted = False
    for _file in p.glob(f"{filename}*"):
        try:
            _file.unlink()
            some_files_deleted = True
        except (FileNotFoundError, OSError):
            continue
    return some_files_deleted


def test_strip_mask_no_mask():
    assert strip_mask("192.0.1.15") == "192.0.1.15"


def test_strip_mask_with_mask():
    assert strip_mask("2001:db8:516::4/128") == "2001:db8:516::4"


def test_strip_mask_no_input():
    assert strip_mask("") == ""


def test_read_from_cache_fresh_cache_used(clear_cache):
    with shelve.open(CACHE_FILE) as cache:
        cache[CACHE_KEY] = [0, "test data"]
    cached_data = read_from_cache(CACHE_FILE, CACHE_KEY, 1)
    assert len(cached_data) == 2
    assert "test data" in cached_data


def test_read_from_cache_stale_cache_ignored(clear_cache):
    with shelve.open(CACHE_FILE) as cache:
        cache[CACHE_KEY] = [0, "test data"]

    with patch("tt_main.utils.time.time", return_value=time() + 100000):
        cached_data = read_from_cache(CACHE_FILE, CACHE_KEY, 1)

    assert not cached_data


def test_read_from_cache_wrong_key(clear_cache):
    with shelve.open(CACHE_FILE) as cache:
        cache[CACHE_KEY] = [0, "test data"]
    cached_data = read_from_cache(CACHE_FILE, "wrong key", 1)
    assert not cached_data


def test_read_from_cache_file_not_found(clear_cache):
    print(list(Path("/tmp").glob("test_*")))
    cached_data = read_from_cache(CACHE_FILE, CACHE_KEY, 1)
    assert not cached_data


def test_write_to_cache_ok(clear_cache):
    status = write_to_cache(CACHE_FILE, CACHE_KEY, [0, "test data"])
    assert status is True
    with shelve.open(CACHE_FILE, flag="r") as cache:
        cached_data = cache[CACHE_KEY]
    assert len(cached_data) == 2
    assert "test data" in cached_data


def test_write_to_cache_error(clear_cache):
    status = write_to_cache("/test/test_data", CACHE_KEY, [0, "test data"])
    assert status is False


def test_is_check_disabled_yes(tmp_path):
    content = "NO_BIRD_PROTO_CHECK\nNO_CPU_STAT_CHECK\nl3mgr_svn='true'"
    p = tmp_path / "environment"
    p.write_text(content)
    assert is_check_disabled("bird_proto", p)


def test_is_check_disabled_no(tmp_path):
    content = "NO_CPU_STAT_CHECK\nl3mgr_svn='true'"
    p = tmp_path / "environment"
    p.write_text(content)
    assert not is_check_disabled("bird_proto", p)


def test_is_check_disabled_no_file():
    assert not is_check_disabled("bird_proto", "/tmp/non_existent_file")


def test_false_is_contains_rt_tag(tmp_path):
    content = "ConnectX-5\nl3mgr"
    p = tmp_path / "racktables-tags"
    p.write_text(content)
    assert not is_contains_rt_tag("YANET", p)


def test_true_is_contains_rt_tag(tmp_path):
    content = "YANET\nConnectX-5\nl3mgr"
    p = tmp_path / "racktables-tags"
    p.write_text(content)
    assert is_contains_rt_tag("YANET", p)


def test_is_contains_rt_tag_no_file():
    assert not is_contains_rt_tag("YANET", "/tmp/non_existent_file")


def test_get_check_name():
    assert get_check_name(__file__) == "test_utils"


def test_retry_func_with_status_fail_than_ok():
    testfunc = Mock(side_effect=[(False, "ERR"), (True, "OK")])
    start_time = time()
    status, msg = retry_func_with_status(testfunc, "")
    assert status
    assert msg == "OK"
    assert time() - start_time > 1
    testfunc.assert_called_with("")
    assert testfunc.call_count == 2


def test_retry_func_with_status_ok():
    testfunc = Mock(return_value=(True, "OK"))
    start_time = time()
    status, msg = retry_func_with_status(testfunc, "")
    assert status
    assert msg == "OK"
    assert time() - start_time < 1
    testfunc.assert_called_once_with("")


def test_retry_func_with_status_fail_than_fail():
    testfunc = Mock(side_effect=[(False, "ERR"), (False, "ERR")])
    start_time = time()
    status, msg = retry_func_with_status(testfunc, "")
    assert not status
    assert msg == "ERR"
    assert time() - start_time > 1
    testfunc.assert_called_with("")
    assert testfunc.call_count == 2


def test_retry_required_data():
    testfunc = Mock(side_effect=[(True, []), (True, [1, 2])])
    start_time = time()
    status, data = retry_func_with_status(testfunc, "", need_data=True)
    assert status
    assert data == [1, 2]
    assert time() - start_time > 1
    testfunc.assert_called_with("")
    assert testfunc.call_count == 2

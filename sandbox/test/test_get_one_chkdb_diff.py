import textwrap
import logging

from sandbox.projects.yabs.qa.compare import get_one_chkdb_diff


def _get_one_chkdb_diff(a, b):
    diff = get_one_chkdb_diff(a, b)
    logging.info("Diff:\n%s", diff)
    return diff


def test_no_diff():
    data = {
        "bases.dyn_size": [{
            "AllocatedSize": None,
            "ItemCount": None,
            "ItemSize": None,
            "Key": None,
            "Size": None,
            "Value": 8160
        }],
        "bases.id": [{
            "AllocatedSize": None,
            "ItemCount": None,
            "ItemSize": None,
            "Key": None,
            "Size": None,
            "Value": 2054
        }]
    }
    diff = _get_one_chkdb_diff(data, data)
    assert diff == ''


def test_two_subkeys_diff():
    diff = _get_one_chkdb_diff(
        {"some.key": [{"SomeSubkey": "DEADBEEF", "Value": 8160}]},
        {"some.key": [{"SomeSubkey": "FOOBAR", "Value": 8162}]}
    )
    assert diff == textwrap.dedent(
        """\
        some.key:
            - {"SomeSubkey": "DEADBEEF", "Value": 8160}
            + {"SomeSubkey": "FOOBAR", "Value": 8162}"""
    )


def test_submaps_diff():
    diff = _get_one_chkdb_diff(
        {"some.key": [{"Key": "A", "Value": 1}, {"Key": "B", "Value": "ZZZ"}, {"Key": "D", "Value": "V"}]},
        {"some.key": [{"Key": "A", "Value": 1}, {"Key": "C", "Value": "ZZZ"}, {"Key": "D", "Value": "B"}]},
    )
    assert diff == textwrap.dedent(
        """\
        some.key:
            - {"Key": "B", "Value": "ZZZ"}
            + {"Key": "C", "Value": "ZZZ"}
            - {"Key": "D", "Value": "V"}
            + {"Key": "D", "Value": "B"}"""
    )


def test_unequal_submaps_diff():
    diff = _get_one_chkdb_diff(
        {"some.key": [{"Key": "A", "Value": 1}, {"Key": "D", "Value": "V"}]},
        {"some.key": [{"Key": "A", "Value": 1}, {"Key": "C", "Value": "ZZZ"}, {"Key": "D", "Value": "B"}]},
    )
    assert diff == textwrap.dedent(
        """\
        some.key:
            + {"Key": "C", "Value": "ZZZ"}
            - {"Key": "D", "Value": "V"}
            + {"Key": "D", "Value": "B"}"""
    )


def test_non_submaps_keys():
    diff = _get_one_chkdb_diff(
        {"some.key": [{"SomeSubkey": "DEADBEEF", "Value": 8160}]},
        {"another_key": [{"SomeSubkey": "FOOBAR", "Value": 8162}]}
    )
    assert diff == textwrap.dedent(
        """\
        another_key:
            + {"SomeSubkey": "FOOBAR", "Value": 8162}
        some.key:
            - {"SomeSubkey": "DEADBEEF", "Value": 8160}"""
    )

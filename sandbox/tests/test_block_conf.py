from __future__ import unicode_literals
from sandbox.projects.release_machine.components.config_core import release_block as rb
from release_machine.common_proto import test_results_pb2

import pytest
import re


@pytest.mark.parametrize("block_conf_instance, job_test_results_dict, expected_value", [
    (  # no block if all OK
        rb.REQUIRE_ALL_OK,
        {"T1": rb.OK, "T2": rb.OK},
        False,
    ),
    (  # block if OK required and some tests are in CRIT
        rb.REQUIRE_ALL_OK,
        {"T1": rb.OK, "T2": rb.CRIT},
        True,
    ),
    (  # block if OK required and some tests are in WARN
        rb.REQUIRE_ALL_OK,
        {"T1": rb.OK, "T2": rb.WARN},
        True,
    ),
    (  # ignore tests that do not match name filter
        rb.block_conf(name_filter='TEST_*', accept_result_threshold=rb.OK),
        {"TEST_SOMETHING": rb.OK, "BUILD_SOMETHING": rb.CRIT},
        False,
    ),
    (  # do not ignore tests that DO match name filter; CRIT blocks if OK required
        rb.block_conf(name_filter='TEST_*', accept_result_threshold=rb.OK),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE": rb.CRIT},
        True,
    ),
    (  # UB blocks if OK required
        rb.block_conf(name_filter='TEST_*', accept_result_threshold=rb.OK),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE": rb.UB},
        True,
    ),
    (  # UB blocks if at least CRIT required (UB is worse than CRIT)
        rb.block_conf(name_filter='TEST_*', accept_result_threshold=rb.CRIT),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE": rb.UB},
        True,
    ),
    (  # regular expressions also work
        rb.block_conf(name_filter=re.compile(r'TEST_[A-Z_]+_IMPORTANT'), accept_result_threshold=rb.OK),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE": rb.CRIT},
        False,
    ),
    (  # regular expressions also work (2)
        rb.block_conf(name_filter=re.compile(r'TEST_[A-Z_]+_IMPORTANT'), accept_result_threshold=rb.OK),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE_IMPORTANT": rb.CRIT},
        True,
    ),
    (  # `None` test results are ignored by default
        rb.block_conf(name_filter=re.compile(r'TEST_[A-Z_]+_IMPORTANT'), accept_result_threshold=rb.OK),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE_IMPORTANT": None},
        False,
    ),
    (  # `None` test results will not be ignored if `ignore_empty` is `False`
        rb.block_conf(
            name_filter=re.compile(r'TEST_[A-Z_]+_IMPORTANT'),
            accept_result_threshold=rb.OK,
            ignore_empty=False,
        ),
        {"TEST_SOMETHING": rb.OK, "TEST_SOMETHING_ELSE_IMPORTANT": None},
        True,
    ),
])
def test__should_block(block_conf_instance, job_test_results_dict, expected_value):
    assert block_conf_instance.should_block(job_test_results_dict) == expected_value


def test__test_result_status_ordering():
    assert rb.ONGOING < rb.UB < rb.CRIT < rb.WARN < rb.OK


@pytest.mark.parametrize("rb_status", [
    rb.ONGOING,
    rb.UB,
    rb.CRIT,
    rb.WARN,
    rb.OK,
])
def test__all_statuses_in_release_block_are_present_in_original_protobuf_enum(rb_status):
    assert rb_status.name in set(test_results_pb2.TestResult.TestStatus.keys())


@pytest.fixture
def block_conf_proto():
    from release_machine.common_proto import block_release_pb2, test_results_pb2

    return [
        block_release_pb2.BlockRelease(
            accept_result_threshold=test_results_pb2.TestResult.TestStatus.OK,
            ignore_empty=True,
            name_filter_str="_TEST__*",
        ),
    ]


@pytest.fixture
def block_conf_expected():
    return [
        rb.block_conf(
            name_filter="_TEST__*",
            accept_result_threshold=rb.OK,
            ignore_empty=True,
        ),
    ]


def test__parse_block_conf_proto(block_conf_proto, block_conf_expected):

    block_conf_built = rb.parse_block_conf_proto(block_conf_proto)

    assert type(block_conf_built) is list
    assert len(block_conf_built) == len(block_conf_expected)

    for item_built, item_expected in zip(block_conf_built, block_conf_expected):

        assert item_built.name_filter_str == item_expected.name_filter_str
        assert item_built.ignore_empty == item_expected.ignore_empty
        assert isinstance(item_built.accept_result_threshold, type(item_expected.accept_result_threshold))
        assert item_built.accept_result_threshold == item_expected.accept_result_threshold


def test__all_test_statuses_present_and_correct_in_known_statuses():

    for status_value in test_results_pb2.TestResult.TestStatus.values():
        status_name = test_results_pb2.TestResult.TestStatus.Name(status_value)

        assert status_name in rb.KNOWN_STATUSES, "{name} not present in KNOWN_STATUSES".format(
            name=status_name,
        )
        assert rb.KNOWN_STATUSES[status_name].name == status_name, "KNOWN_STATUSES[{name}] value is incorrect".format(
            name=status_name,
        )
        assert rb.KNOWN_STATUSES[status_name].order is not None, "Got order = None in KNOWN_STATUSES[{name}]".format(
            name=status_name,
        )

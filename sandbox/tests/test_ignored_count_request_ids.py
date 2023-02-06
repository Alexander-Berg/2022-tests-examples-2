from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.ignored_count_requests import get_ignored_count_request_ids


def test_ignored_count_request_ids():
    pre_dump = {
        'Some words for check',
        '-123456789',
        '123456789',
        '12345678901234567890',
        '',
    }

    test_dump = {
        '',
        '98765432109876543210',
        'Some words for check again',
        '1234567890123456789',
        '12345.6789',
    }

    bad_request_ids = {
        10000000,
        1234567,
        50005000,
        123456,
        4900,
    }

    expected_result = {
        12345678901234567890,
        1234567890123456789,
    }

    result = get_ignored_count_request_ids(pre_dump, test_dump, bad_request_ids)
    assert result == expected_result

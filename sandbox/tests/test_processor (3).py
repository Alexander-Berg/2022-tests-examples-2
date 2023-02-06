import datetime

import mock
import pytest
import pytz

from sandbox.projects.browser.plus_point_scrapper import processor

MSK_TIMEZONE = pytz.timezone('Europe/Moscow')
DATE_1_MSK = pytz.UTC.localize(datetime.datetime(2021, 1, 1)).astimezone(MSK_TIMEZONE)
DATE_2_MSK = pytz.UTC.localize(datetime.datetime(2021, 2, 1)).astimezone(MSK_TIMEZONE)

TEST_PUID_TIME_LIST = [
    (1, 111),
    (2, 222),
    (3, 333),
    (4, 444),
    (5, 555),
    (6, 666),
    (7, 777),
]


class TestProcessor(processor.PassportUserIDProcessor):
    _MAX_PUID_LIST_SIZE_FOR_SAVE = 4

    def __init__(self, dry_run, puid_time_list):
        super(TestProcessor, self).__init__(
            None, dry_run, 'YQL-TOKEN', 'TVM-SERVICE-TICKET')
        self.mock_handle = mock.MagicMock()
        self._yql_insert_to_history = self.mock_yql_insert = mock.MagicMock()
        self._yql_select_puids = mock.MagicMock(
            return_value=mock.MagicMock(table=mock.MagicMock(rows=puid_time_list)))

    def _handle(self, passport_user_id, utc_start_time, plus_transaction_id):
        self.mock_handle(passport_user_id, utc_start_time, plus_transaction_id)


def test_processor_save():
    test_processor = TestProcessor(False, TEST_PUID_TIME_LIST)
    test_processor.process(DATE_1_MSK, DATE_2_MSK)
    assert test_processor.mock_handle.mock_calls == [
        mock.call(p, t, mock.ANY) for p, t in TEST_PUID_TIME_LIST]
    assert test_processor.mock_yql_insert.mock_calls == [
        mock.call(mock.ANY, [
            (p, t, mock.ANY) for p, t in TEST_PUID_TIME_LIST[0:4]]),
        mock.call(mock.ANY, [
            (p, t, mock.ANY) for p, t in TEST_PUID_TIME_LIST[4:]]),
    ]


def test_processor_save_and_exception():
    def broken_handle(passport_user_id, utc_start_time, plus_transaction_id):
        if passport_user_id == 3:
            raise ValueError('Broken passport user ID')

    test_processor = TestProcessor(False, TEST_PUID_TIME_LIST)
    test_processor._handle = broken_handle
    with pytest.raises(ValueError):
        test_processor.process(DATE_1_MSK, DATE_2_MSK)
    assert test_processor.mock_yql_insert.mock_calls == [
        mock.call(mock.ANY, [
            (p, t, mock.ANY) for p, t in TEST_PUID_TIME_LIST[0:2]]),
    ]

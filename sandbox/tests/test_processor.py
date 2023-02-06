# coding=utf-8

import calendar
import datetime
import logging
import unittest

import mock
import pytz

from sandbox.projects.browser.booking import common
from sandbox.projects.browser.booking.config import (
    BookingConfig,
)
from sandbox.projects.browser.booking.processor import (
    BookingClient,
    BookingInfo,
    BookingParams,
    Processor,
)


def mock_release(release_id, version, responsible):
    """
    :rtype: shuttle_client.Release
    """
    release = mock.MagicMock()
    release.id = release_id
    release.version = version
    release.responsible = responsible
    return release


def mock_event(event_id, event_type, date, title, params):
    """
    :rtype: shuttle_client.Event
    """
    event = mock.MagicMock()
    event.id = event_id
    event.type = event_type
    event.date = date
    event.title = title
    event.parameters = params
    return event


def mock_booking_info(booking_id, start_date, start_from_date):
    """
    :rtype: BookingInfo
    """
    return BookingInfo({
        'bookingId': booking_id,
        'status': BookingInfo.STATUS_ACTIVE,
        'estimate': {
            'startTs': calendar.timegm(start_date.utctimetuple()) * 1000,
            'deadlineTs': calendar.timegm((start_date + datetime.timedelta(1)).utctimetuple()) * 1000,
        },
        'params': {
            'startTsFrom': calendar.timegm(start_from_date.utctimetuple()) * 1000,
        },
    })


TEST_PROJECT_KEY = 'android'
TEST_RELEASE = mock_release(101, '12.3.4', 'username')
TEST_EVENT_ID = 103
TEST_EVENT_TYPE = 'milestone:regression'
TEST_EVENT_TITLE = 'Регрессия'
TEST_BOOKING_KIND = 'build:rc'
TEST_BOOKING_ID = 107
TEST_BOOKING_ID_AND_URL = '#{} ({})'.format(
    TEST_BOOKING_ID, BookingClient.get_booking_url(TEST_BOOKING_ID))
TEST_BOOKING_ID_NEW = 109
TEST_BOOKING_ID_AND_URL_NEW = '#{} ({})'.format(
    TEST_BOOKING_ID_NEW, BookingClient.get_booking_url(TEST_BOOKING_ID_NEW))


def mock_event_without_booking(event_date):
    """
    :type event_date: datetime.datetime
    :rtype: (shuttle_client.Event, BookingInfo)
    """
    event_date = pytz.UTC.localize(event_date)
    params = {BookingParams.PARAM_BOOKING: {
        BookingParams.PARAM_BOOKING_KIND: TEST_BOOKING_KIND,
    }}
    event = mock_event(TEST_EVENT_ID, TEST_EVENT_TYPE, event_date, TEST_EVENT_TITLE, params)
    return event, None


def mock_event_with_booking(event_date, booking_id, booking_start_from_date, booking_start_date):
    """
    :type event_date: datetime.datetime
    :type booking_id: int
    :type booking_start_from_date: datetime.datetime
    :type booking_start_date: datetime.datetime
    :rtype: (shuttle_client.Event, BookingInfo)
    """
    event_date = pytz.UTC.localize(event_date)
    params = {BookingParams.PARAM_BOOKING: {
        BookingParams.PARAM_BOOKING_KIND: TEST_BOOKING_KIND,
        BookingParams.PARAM_BOOKING_ID: TEST_BOOKING_ID,
    }}
    event = mock_event(TEST_EVENT_ID, TEST_EVENT_TYPE, event_date, TEST_EVENT_TITLE, params)
    booking_info = mock_booking_info(booking_id, booking_start_date, booking_start_from_date)
    return event, booking_info


TEST_BOOKING_CONFIG_PARAMS = {
    'quotaSource': 'qs_testpalm_combined_brocase_ru',
    'speedMode': 'NORMAL',
    'volumeDescription': {
        "volumeSources": [],
        'customVolume': {
            'amount': '100',
            'environmentDistribution': {
                'android': 0.5,
                'iphone': 0.5,
            }
        }
    }
}
TEST_BOOKING_CONFIG_JSON = {
    'create-days': 14,
    'veto-days': 7,
    'notification-hours-threshold': 1,
    'time-msk': '12:00',
    'params': TEST_BOOKING_CONFIG_PARAMS,
}
TEST_BOOKING_CONFIG = BookingConfig(TEST_PROJECT_KEY, TEST_BOOKING_KIND, TEST_BOOKING_CONFIG_JSON)


class MockProcessor(Processor):
    def __init__(self, now_datetime_msk_str):
        now_datetime_msk = common.MSK_TIMEZONE.localize(
            datetime.datetime.strptime(
                now_datetime_msk_str, common.DATETIME_FORMAT))

        super(MockProcessor, self).__init__(
            mock.MagicMock(), mock.MagicMock(), now_datetime_msk, False)
        self.info = []
        self.chat = []
        self.cancel_booking = mock.MagicMock()
        self.create_booking = mock.MagicMock()

    @property
    def logger(self):
        return logging.getLogger('booking')

    def set_info(self, message):
        self.info.append(message)

    def notify_responsible(self, project_key, release, message):
        self.chat.append((project_key, release, message))


class TestProcessor(unittest.TestCase):
    def test_process_booking_not_a_time(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_without_booking(datetime.datetime(2020, 1, 16, 12, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == []
        assert notifications == []

    def test_process_booking_check_correct(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 12, 9, 0, 0), datetime.datetime(2020, 1, 12, 15, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == notifications == [
            'Проект {}: Бронирование {} для вехи "{}" релиза "{}" назначено на {} (а не на {}).\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_EVENT_TITLE, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE),
                booking_info.start_from.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                booking_info.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]

    def test_process_booking_create_new(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_without_booking(datetime.datetime(2020, 1, 12, 12, 0, 0))
        _, new_booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0), TEST_BOOKING_ID_NEW,
            datetime.datetime(2020, 1, 12, 9, 0, 0), datetime.datetime(2020, 1, 12, 15, 0, 0))
        processor.create_booking.return_value = new_booking_info

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, TEST_RELEASE, event, new_booking_info.start_from,
                      TEST_BOOKING_CONFIG_PARAMS, None),
        ]
        assert processor.info == notifications == [
            'Проект {}: Создано бронирование {} для вехи "{}" релиза "{}" на {}\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL_NEW, TEST_EVENT_TITLE, TEST_RELEASE.version,
                new_booking_info.start.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                new_booking_info.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]

    def test_process_booking_create_new_veto(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_without_booking(datetime.datetime(2020, 1, 5, 12, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 5, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == [
            'Проект {}: Бронирование для вехи "{}" релиза "{}" должно быть назначено на {}, '
            'но на операцию уже действует вето ({} дней).'.format(
                TEST_PROJECT_KEY, TEST_EVENT_TITLE, TEST_RELEASE.version,
                booking_datetime.astimezone(common.MSK_TIMEZONE),
                TEST_BOOKING_CONFIG_JSON['veto-days']),
        ]
        assert notifications == []

    def test_process_booking_move_backward(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 9, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 10, 9, 0, 0), datetime.datetime(2020, 1, 10, 15, 0, 0))
        _, new_booking_info_1 = mock_event_without_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0))
        processor.cancel_booking.return_value = new_booking_info_1
        _, new_booking_info_2 = mock_event_with_booking(
            datetime.datetime(2020, 1, 9, 12, 0, 0), TEST_BOOKING_ID_NEW,
            datetime.datetime(2020, 1, 9, 9, 0, 0), datetime.datetime(2020, 1, 9, 18, 0, 0))
        processor.create_booking.return_value = new_booking_info_2

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 9, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, event, booking_info),
        ]
        assert processor.create_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, TEST_RELEASE, event, booking_datetime,
                      TEST_BOOKING_CONFIG_PARAMS, None),
        ]
        assert processor.info == [
            'Проект {}: Отменено бронирование {} для вехи "Регрессия" релиза "{}", назначенное на {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE)),
            'Проект {}: Создано бронирование {} для вехи "Регрессия" релиза "{}" на {}\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL_NEW, TEST_RELEASE.version,
                new_booking_info_2.start.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                new_booking_info_2.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]
        assert notifications == [
            'Проект {}: Создано бронирование {} для вехи "Регрессия" релиза "{}" на {}\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL_NEW, TEST_RELEASE.version,
                new_booking_info_2.start.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                new_booking_info_2.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]

    def test_process_booking_move_backward_veto(self):
        processor = MockProcessor('2020-01-02 17:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 9, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 10, 9, 0, 0), datetime.datetime(2020, 1, 10, 15, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 9, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == [
            'Проект {}: Бронирование {} для вехи "{}" релиза "{}", назначенное на {}, '
            'должно быть перенесено на {}, но на операцию уже действует вето ({} дней).'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_EVENT_TITLE, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE),
                booking_datetime.astimezone(common.MSK_TIMEZONE),
                TEST_BOOKING_CONFIG_JSON['veto-days'])
        ]
        assert notifications == []

    def test_process_booking_move_forward(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 10, 9, 0, 0), datetime.datetime(2020, 1, 10, 15, 0, 0))
        _, new_booking_info_1 = mock_event_without_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0))
        processor.cancel_booking.return_value = new_booking_info_1
        _, new_booking_info_2 = mock_event_with_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0), TEST_BOOKING_ID_NEW,
            datetime.datetime(2020, 1, 12, 9, 0, 0), datetime.datetime(2020, 1, 12, 18, 0, 0))
        processor.create_booking.return_value = new_booking_info_2

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 12, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, event, booking_info),
        ]
        assert processor.create_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, TEST_RELEASE, event, booking_datetime,
                      TEST_BOOKING_CONFIG_PARAMS, None),
        ]
        assert processor.info == [
            'Проект {}: Отменено бронирование {} для вехи "Регрессия" релиза "{}", назначенное на {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE)),
            'Проект {}: Создано бронирование {} для вехи "Регрессия" релиза "{}" на {}\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL_NEW, TEST_RELEASE.version,
                new_booking_info_2.start.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                new_booking_info_2.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]
        assert notifications == [
            'Проект {}: Создано бронирование {} для вехи "Регрессия" релиза "{}" на {}\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL_NEW, TEST_RELEASE.version,
                new_booking_info_2.start.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                new_booking_info_2.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]

    def test_process_booking_move_forward_veto(self):
        processor = MockProcessor('2020-01-03 20:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 10, 9, 0, 0), datetime.datetime(2020, 1, 10, 15, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 12, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == [
            'Проект {}: Бронирование {} для вехи "{}" релиза "{}", назначенное на {}, '
            'должно быть перенесено на {}, но на операцию уже действует вето ({} дней).'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_EVENT_TITLE, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE),
                booking_datetime.astimezone(common.MSK_TIMEZONE),
                TEST_BOOKING_CONFIG_JSON['veto-days'])
        ]
        assert notifications == []

    def test_process_booking_cancel_old(self):
        processor = MockProcessor('2020-01-01 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 18, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 10, 9, 0, 0), datetime.datetime(2020, 1, 10, 15, 0, 0))
        _, new_booking_info = mock_event_without_booking(
            datetime.datetime(2020, 1, 18, 12, 0, 0))
        processor.cancel_booking.return_value = new_booking_info

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        assert processor.cancel_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, event, booking_info),
        ]
        assert processor.create_booking.mock_calls == []
        assert processor.info == [
            'Проект {}: Отменено бронирование {} для вехи "Регрессия" релиза "{}", назначенное на {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE)),
        ]
        assert notifications == []

    def test_process_booking_cancel_old_veto(self):
        processor = MockProcessor('2020-01-09 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 18, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 10, 9, 0, 0), datetime.datetime(2020, 1, 10, 15, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 18, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == [
            'Проект {}: Бронирование {} для вехи "{}" релиза "{}", назначенное на {}, должно быть '
            'перенесено на {}, но на операцию уже действует вето ({} дней).'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL, TEST_EVENT_TITLE, TEST_RELEASE.version,
                booking_info.start.astimezone(common.MSK_TIMEZONE),
                booking_datetime.astimezone(common.MSK_TIMEZONE, ),
                TEST_BOOKING_CONFIG_JSON['veto-days']),
        ]
        assert notifications == []

    def test_process_booking_check_old_without_booking(self):
        processor = MockProcessor('2020-01-15 00:00:00')
        event, booking_info = mock_event_without_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == []
        assert notifications == []

    def test_process_booking_check_old_with_booking(self):
        processor = MockProcessor('2020-01-15 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 12, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 12, 9, 0, 0), datetime.datetime(2020, 1, 12, 15, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == []
        assert notifications == []

    def test_process_booking_move_old(self):
        processor = MockProcessor('2020-01-15 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 24, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 12, 9, 0, 0), datetime.datetime(2020, 1, 12, 15, 0, 0))
        _, new_booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 24, 12, 0, 0), TEST_BOOKING_ID_NEW,
            datetime.datetime(2020, 1, 24, 9, 0, 0), datetime.datetime(2020, 1, 24, 10, 0, 0))
        processor.create_booking.return_value = new_booking_info

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 24, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == [
            mock.call(TEST_PROJECT_KEY, TEST_RELEASE, event, booking_datetime,
                      TEST_BOOKING_CONFIG_PARAMS, None),
        ]
        assert processor.info == [
            'Проект {}: Создано бронирование {} для вехи "{}" релиза "{}" на {}\n'
            'Дата выкатки: {}\n'
            'Окончание дедлайна: {}'.format(
                TEST_PROJECT_KEY, TEST_BOOKING_ID_AND_URL_NEW, TEST_EVENT_TITLE, TEST_RELEASE.version,
                new_booking_info.start.astimezone(common.MSK_TIMEZONE),
                event.date.astimezone(common.MSK_TIMEZONE),
                new_booking_info.deadline.astimezone(common.MSK_TIMEZONE),
            ),
        ]
        assert notifications == []

    def test_process_booking_move_old_veto(self):
        processor = MockProcessor('2020-01-20 00:00:00')
        event, booking_info = mock_event_with_booking(
            datetime.datetime(2020, 1, 24, 12, 0, 0), TEST_BOOKING_ID,
            datetime.datetime(2020, 1, 12, 9, 0, 0), datetime.datetime(2020, 1, 12, 15, 0, 0))

        notifications = []
        processor.process_event(
            TEST_PROJECT_KEY, TEST_RELEASE, event,
            TEST_BOOKING_CONFIG, booking_info,
            notifications)

        booking_datetime = datetime.datetime(2020, 1, 24, 9, 0, 0, tzinfo=pytz.UTC)
        assert processor.cancel_booking.mock_calls == []
        assert processor.create_booking.mock_calls == []
        assert processor.info == [
            'Проект {}: Бронирование для вехи "{}" релиза "{}" должно быть назначено на {}, '
            'но на операцию уже действует вето ({} дней).'.format(
                TEST_PROJECT_KEY, TEST_EVENT_TITLE, TEST_RELEASE.version,
                booking_datetime.astimezone(common.MSK_TIMEZONE),
                TEST_BOOKING_CONFIG_JSON['veto-days']),
        ]
        assert notifications == []

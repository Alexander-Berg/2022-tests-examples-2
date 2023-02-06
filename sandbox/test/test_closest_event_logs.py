import pytest
import pytz
from datetime import datetime, timedelta
from yt.wrapper import ypath_join
from sandbox.projects.yabs.qa.bases.sample_tables.closest_event_logs import choose_closest_event_logs, LOGFELLER_TIMEZONE
import logging

logger = logging.getLogger(__name__)


def create_event_log(yt_client, event_log_dir, log_time, time_format):
    path = ypath_join(event_log_dir, log_time.strftime(time_format))
    yt_client.create(
        'table',
        path,
        recursive=True,
        ignore_existing=True,
    )
    logger.debug('Created table %s for %s', path, log_time)
    return path


@pytest.fixture()
def time_node(input_prefix, yt_client):
    path = ypath_join(input_prefix, 'yt_tables/test_table')
    yt_client.create(
        'table',
        path,
        recursive=True
    )
    return path


@pytest.fixture()
def creation_time(yt_client, time_node):
    attr = yt_client.get_attribute(time_node, 'creation_time')
    logger.debug('creation_time: %s', attr)
    return datetime.strptime(
        attr,
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=pytz.utc).astimezone(LOGFELLER_TIMEZONE)


@pytest.fixture()
def create_far_logs(yt_client, input_prefix, creation_time):
    create_event_log(
        yt_client,
        ypath_join(input_prefix, '1d'),
        creation_time + timedelta(days=-2),
        '%Y-%m-%d'
    )
    create_event_log(
        yt_client,
        ypath_join(input_prefix, '1d'),
        creation_time + timedelta(days=2),
        '%Y-%m-%d'
    )
    create_event_log(
        yt_client,
        ypath_join(input_prefix, 'stream/5min'),
        creation_time + timedelta(days=-2),
        '%Y-%m-%dT%H:%M:00'
    )
    create_event_log(
        yt_client,
        ypath_join(input_prefix, 'stream/5min'),
        creation_time + timedelta(days=2),
        '%Y-%m-%dT%H:%M:00'
    )


class TestClosestEventLogs(object):
    @pytest.mark.parametrize("expected_logs", [
        [
        ],
        [
            {'type': '1d',   'delta': timedelta(days=-1)},
        ],
        [
            {'type': '1d',   'delta': timedelta(days=0)},
        ],
        [
            {'type': '1d',   'delta': timedelta(days=-1)},
            {'type': '1d',   'delta': timedelta(days=0)},
        ],
        [
            {'type': '5min', 'delta': timedelta(days=-1, minutes=1)},
            {'type': '5min', 'delta': timedelta(days=-1, minutes=6)},
            {'type': '5min', 'delta': timedelta(days=-1, minutes=11)},
            {'type': '5min', 'delta': timedelta(days=-1, minutes=21)},
        ],
        [
            {'type': '5min', 'delta': timedelta(days=0, minutes=-20)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-10)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-5)},
            {'type': '5min', 'delta': timedelta(days=0)},
        ],
        [
            {'type': '5min', 'delta': timedelta(days=-1, minutes=1)},
            {'type': '5min', 'delta': timedelta(days=-1, minutes=6)},
            {'type': '5min', 'delta': timedelta(days=-1, minutes=11)},
            {'type': '5min', 'delta': timedelta(days=-1, minutes=21)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-20)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-10)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-5)},
            {'type': '5min', 'delta': timedelta(days=0)},
        ],
        [
            {'type': '1d',   'delta': timedelta(days=-1)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-20)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-10)},
            {'type': '5min', 'delta': timedelta(days=0, minutes=-5)},
            {'type': '5min', 'delta': timedelta(days=0)},
        ],
    ])
    def test_closest_event_logs(self, input_prefix, yt_client, creation_time, create_far_logs, expected_logs):
        logger.debug('Now: %s', creation_time)
        created_logs = []
        already_added_1d_log = False
        for log in expected_logs:
            if log['type'] == '1d':
                path = create_event_log(
                    yt_client,
                    ypath_join(input_prefix, '1d'),
                    creation_time + log['delta'],
                    '%Y-%m-%d'
                )
                if not already_added_1d_log:
                    created_logs.append(path)
                    already_added_1d_log = True
                # Always create unexpected 5min log to check for 1d log precedence
                create_event_log(
                    yt_client,
                    ypath_join(input_prefix, 'stream/5min'),
                    creation_time + log['delta'],
                    '%Y-%m-%dT%H:%M:00'
                )
            if log['type'] == '5min':
                path = create_event_log(
                    yt_client,
                    ypath_join(input_prefix, 'stream/5min'),
                    creation_time + log['delta'],
                    '%Y-%m-%dT%H:%M:00'
                )
                if not already_added_1d_log:
                    created_logs.append(path)
        actual_logs = choose_closest_event_logs(
            yt_client,
            input_prefix,
            input_prefix,
            timedelta(days=1)
        )
        assert actual_logs == created_logs

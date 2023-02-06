import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.internal import event_monitor
from taxi.internal import startrack_error_notifiers as startrack


CHECK_TYPE = 'big-check'
CHECK_DESCRIPTION = 'Big check description'


def get_dummy_notifier(patch, monkeypatch):
    monkeypatch.setattr(settings, 'STARTRACK_API_TOKEN', 'supersecret')
    created_tickets = []
    comments = []

    @patch('taxi.external.staff.search_staff_by_department_id')
    @async.inline_callbacks
    def search_staff_by_department_id(department_id, fields=None,
                                      log_extra=None):
        assert department_id == 111111
        yield async.return_value([{'login': 'test_user'}])

    @patch('taxi.external.startrack.create_ticket_or_comment')
    @async.inline_callbacks
    def create_ticket_or_comment(queue, title, message, ticket=None, **kwargs):
        if not ticket:
            created_tickets.append((title, message))
        else:
            comments.append(message)
        yield async.return_value(ticket)

    @patch('taxi.external.startrack.create_comment')
    @async.inline_callbacks
    def create_comment(ticket, body):
        comments.append(body)
        yield async.return_value()

    class DummyNotifier(startrack._BaseYtReplicationCheckNotifier):
        def __init__(self):
            self.created_tickets = created_tickets
            self.comments = comments

        check_type = CHECK_TYPE
        check_description = CHECK_DESCRIPTION

    return DummyNotifier()


def patch_event(monkeypatch, ticket_event):
    class DummyEvent(object):
        @pytest.inline_callbacks
        def get_recent(self, *args, **kwargs):
            yield async.return_value(ticket_event)

        @pytest.inline_callbacks
        def __call__(self, *args, **kwargs):
            assert 'ticket' in kwargs
            yield

    monkeypatch.setattr(event_monitor, 'yt_data_issue_event', DummyEvent())


BaseNotifier = startrack._BaseYtReplicationCheckNotifier

FAILED_CHECK = {
    'check_name': 'check_failed',
    'check_result': {
        'key1': 3,
        'key2': 1,
        'details': {'key1': [1, 2, 3], 'key2': [11]},
    },
    'result_keys': ['key1', 'key2'],
    'status': False,
}
OK_CHECK = {
    'check_name': 'check_ok',
    'check_result': {},
    'result_keys': [],
    'status': True,
}

FAILED_CHECK_NEW_STATUS = FAILED_CHECK.copy()
FAILED_CHECK_NEW_STATUS['status'] = BaseNotifier.STATUS_FAILED
OK_CHECK_NEW_STATUS = {
    'check_name': 'check_ok',
    'status': BaseNotifier.STATUS_OK,
}

INFO_UPDATED_CHECK = FAILED_CHECK.copy()
INFO_UPDATED_CHECK['status'] = BaseNotifier.STATUS_INFO_UPDATED

FAILED_CHECK_DESCRIPTION = (
    '<{key1: 3\n* 1\n* 2\n* 3\n}>\n<{key2: 1\n* 11\n}>\n'
)


@pytest.mark.config(MONITORINGS_SETTINGS={
    'startrack_queue': {
        'yt_replication': 'queue',
    },
    'startrack_kwargs': {
        'yt_replication': {
            'component': 100500,
            'department_id': 111111,
        },
    }
})
@pytest.mark.parametrize(
    'ticket_event,multiple_data,expected_created_tickets,expected_comments',
    [
        (
            {'ticket': 'previous_ticket'},
            [
                FAILED_CHECK,
                OK_CHECK,
            ],
            [],
            ['!!(red)**Big check description** check failed for check_failed!!'
             '\n{0}\n'
             '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION)],
        ),
        (
            {'ticket': 'previous_ticket'},
            [
                OK_CHECK,
                OK_CHECK,
            ],
            [],
            ['!!(green)**Big check description** now OK for check_ok!!\n\n'
             '!!(green)**Big check description** now OK for check_ok!!'],
        ),
        (
            None,
            [
                OK_CHECK,
            ],
            [],
            [],
        ),
        (
            None,
            [
                FAILED_CHECK,
                FAILED_CHECK,
            ],
            [('[big-check] Big check description check failed: check_failed',
              '!!(red)**Big check description** check failed for check_failed!!'
              '\n{0}\n'
              '!!(red)**Big check description** check failed for check_failed!!'
              '\n{0}'.format(FAILED_CHECK_DESCRIPTION))],
            [],
        ),
        (
            None,
            [
                OK_CHECK,
                OK_CHECK_NEW_STATUS,
            ],
            [],
            [],
        ),
        (
            None,
            [
                OK_CHECK_NEW_STATUS,
            ],
            [],
            [],
        ),
        (
            {'ticket': 'previous_ticket'},
            [
                FAILED_CHECK_NEW_STATUS,
                OK_CHECK_NEW_STATUS,
            ],
            [],
            ['!!(red)**Big check description** check failed for check_failed!!'
             '\n{0}\n'
             '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION)],
        ),
        (
            {'ticket': 'previous_ticket'},
            [
                OK_CHECK_NEW_STATUS,
                FAILED_CHECK_NEW_STATUS,
            ],
            [],
            ['!!(red)**Big check description** check failed for check_failed!!'
             '\n{0}\n'
             '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION)],
        ),
        (
            {'ticket': 'previous_ticket'},
            [
                OK_CHECK,
                FAILED_CHECK_NEW_STATUS,
            ],
            [],
            ['!!(red)**Big check description** check failed for check_failed!!'
             '\n{0}\n'
             '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION)],
        ),
        (
            {'ticket': 'previous_ticket'},
            [
                OK_CHECK_NEW_STATUS,
                INFO_UPDATED_CHECK,
            ],
            [],
            ['!!(blue)last **Big check description** '
             'check updated for check_failed!!\n'
             '{0}\n'
             '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION)],
        ),
        (
            {'ticket': 'previous_ticket'},
            [
                OK_CHECK_NEW_STATUS,
                FAILED_CHECK_NEW_STATUS,
                INFO_UPDATED_CHECK,
            ],
            [],
            ['!!(red)**Big check description** check failed for check_failed!!'
             '\n{0}\n'
             '!!(blue)last **Big check description** '
             'check updated for check_failed!!\n'
             '{0}\n'
             '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION)],
        ),
        (
            None,
            [
                OK_CHECK_NEW_STATUS,
                INFO_UPDATED_CHECK,
            ],
            [('[big-check] Big check description check failed: check_failed',
              '!!(blue)last **Big check description** '
              'check updated for check_failed!!\n'
              '{0}\n'
              '!!(green)**Big check description** now OK for check_ok!!'.format(
                FAILED_CHECK_DESCRIPTION))],
            [],
        ),
    ]
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_yt_multiple_notifier(patch, monkeypatch, ticket_event, multiple_data,
                              expected_created_tickets, expected_comments):
    patch_event(monkeypatch, ticket_event)
    notifier = get_dummy_notifier(patch, monkeypatch)
    yield notifier.setup(multiple_data)
    yield notifier.notify()

    assert notifier.created_tickets == expected_created_tickets
    assert notifier.comments == expected_comments

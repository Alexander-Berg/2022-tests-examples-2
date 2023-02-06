import logging
import unittest
from mock import MagicMock
from sandbox.projects.yabs.release.tasks.YabsServerGetB2BDiffs import YabsServerGetB2BDiffs, DiffKey, DiffValue
from sandbox.projects.yabs.release.binary_search import intervals


ST_TICKET = 'BSRELEASE-254987'
TESTS = [
    "YABS_SERVER_40_FT_BS_A_B",
    "YABS_SERVER_40_FT_BSRANK_A_B",
    "YABS_SERVER_40_FT_YABS_A_B",
    "YABS_SERVER_40_PERFORMANCE_BEST_BS",
    "YABS_SERVER_40_PERFORMANCE_BEST_BSRANK",
    "YABS_SERVER_40_PERFORMANCE_BEST_YABS",
    "YABS_SERVER_45_PERFORMANCE_META_BS_A_B_SAMPLED",
    "YABS_SERVER_45_PERFORMANCE_META_BSRANK_A_B_SAMPLED",
    "YABS_SERVER_45_PERFORMANCE_META_YABS_A_B_SAMPLED"
]


class TestNotification(unittest.TestCase):
    def setUp(self):
        self.task = YabsServerGetB2BDiffs(None)
        self.task.delete()

        self.task.on_create()
        self.task.set_info = MagicMock()

    def test_notify_about_unresolved_diffs(self):
        self.task._YabsServerGetB2BDiffs__get_release_ticket = MagicMock(status=MagicMock(name='Need Acceptance', key='needAcceptance'), key=ST_TICKET, assignee='assignee')
        self.task._YabsServerGetB2BDiffs__notify = MagicMock()
        self.task._YabsServerGetB2BDiffs__notify_about_success = MagicMock()
        self.task._YabsServerGetB2BDiffs__wait = MagicMock()
        self.task._YabsServerGetB2BDiffs__get_ticket_assignee = MagicMock(return_value='ticket_assignee')

        logging.info(self.task.Context.next_notify_time)

        interval_sequence = [intervals.Interval(1, 2, intervals.DIFF_DATA, 123, 'yabs-2.0', 'user_name'),
                             intervals.Interval(2, 3, intervals.DIFF_DATA, 123, 'yabs-2.0', 'user_name_2'),
                             intervals.Interval(3, 4, intervals.DIFF_DATA, 123, 'yabs-2.0-rerun-9537713-9539588', 'user_name'),
                             intervals.Interval(4, 5, intervals.DIFF_DATA, 123, 'yabs-2.0-rerun-9537713-9539588', 'user_name'),
                             intervals.Interval(5, 6, intervals.NO_CMP_TASK, 123, 'yabs-2.0-rerun-9537713-9539588', 'user_name_3'),
                             intervals.Interval(6, 7, intervals.FIXED, 123, 'yabs-2.0', 'user_name_2')]

        problems_by_interval = {2: {"status": 'unresolved'}, 3: {"status": 'unresolved'},  5: {"status": 'resolved'}, 7: {"status": 'resolved'}}

        test_results = dict()
        for test in TESTS[:-1]:
            test_results[test] = (interval_sequence, problems_by_interval)

        interval_sequence = [intervals.Interval(7, 8, intervals.NO_CMP_TASK, 123, 'yabs-2.0-rerun-9537713-9539588', 'user_name_4'),
                             intervals.Interval(8, 9, intervals.FIXED, 123, 'yabs-2.0', 'user_name_5'),
                             intervals.Interval(9, 10, intervals.DIFF_DATA, 123, 'yabs-2.0', 'user_name_6')]

        problems_by_interval = {9: {"status": 'resolved'}, 10: {"status": 'resolved'}}
        test_results[TESTS[-1]] = (interval_sequence, problems_by_interval)

        release_ticket = MagicMock(status=MagicMock(name='Need Acceptance', key='needAcceptance'), key=ST_TICKET, assignee='assignee')

        self.task.notify_about_results(test_results, release_ticket)

        call_arg = self.task._YabsServerGetB2BDiffs__notify.call_args_list[0][0]

        assert call_arg[1] == 5  # diff_count

        diffs = call_arg[2]
        logging.info(diffs)
        assert len(diffs) == 2
        assert DiffKey(staff='user_name', telegram='user_name') in diffs
        assert DiffKey(staff='user_name_2', telegram='user_name_2') in diffs
        assert DiffKey(staff='user_name_3', telegram='user_name_3') not in diffs

        assert len(diffs[DiffKey(staff='user_name', telegram='user_name')]) == 1
        assert len(diffs[DiffKey(staff='user_name_2', telegram='user_name_2')]) == 1

        diffs_without_problems = call_arg[3]
        logging.info(diffs_without_problems)
        assert len(diffs_without_problems) == 3
        assert diffs_without_problems[0].interval_end == 8
        assert diffs_without_problems[1].interval_end == 4
        assert diffs_without_problems[2].interval_end == 6

        logging.info(self.task.Context.tests_with_diffs)
        assert sorted(self.task.Context.tests_with_diffs) == sorted(TESTS)

        assert self.task._YabsServerGetB2BDiffs__wait.call_count == 1
        assert self.task._YabsServerGetB2BDiffs__notify.call_count == 1
        assert self.task._YabsServerGetB2BDiffs__notify_about_success.call_count == 0

        self.task.Context.next_notify_time = '2022-01-01T00:00:00'
        self.task.notify_about_results(test_results, release_ticket)

        assert self.task._YabsServerGetB2BDiffs__wait.call_count == 2
        assert self.task._YabsServerGetB2BDiffs__notify.call_count == 2
        assert self.task._YabsServerGetB2BDiffs__notify_about_success.call_count == 0

    def test_notify_about_success(self):
        self.task._YabsServerGetB2BDiffs__get_release_ticket = MagicMock(status=MagicMock(name='Need Acceptance', key='needAcceptance'), key=ST_TICKET, assignee='assignee')
        self.task._YabsServerGetB2BDiffs__notify_about_unresolved_diffs = MagicMock()
        self.task._YabsServerGetB2BDiffs__notify_about_success = MagicMock()
        self.task._YabsServerGetB2BDiffs__wait = MagicMock()
        self.task._YabsServerGetB2BDiffs__get_ticket_assignee = MagicMock(return_value='ticket_assignee')

        interval_sequence = [intervals.Interval(1, 2, intervals.DIFF_DATA, 123, 'dsd', 'user_name')]
        problems_by_interval = {2: {"status": 'resolved'}}

        test_results = dict()
        for test in TESTS:
            test_results[test] = (interval_sequence, problems_by_interval)

        release_ticket = MagicMock(status=MagicMock(name='Need Acceptance', key='needAcceptance'), key=ST_TICKET, assignee='assignee')

        self.task.notify_about_results(test_results, release_ticket)
        logging.info('ok')

        assert self.task._YabsServerGetB2BDiffs__wait.call_count == 0
        assert self.task._YabsServerGetB2BDiffs__notify_about_unresolved_diffs.call_count == 0
        assert self.task._YabsServerGetB2BDiffs__notify_about_success.call_count == 1

    def test_notification_template(self):
        notification_template = self.task._YabsServerGetB2BDiffs__get_notification_template()

        diffs = {}
        diffs[DiffKey('user_name1', 'telegram_user2')] = {DiffValue(1, 'yabs-2.0-rerun-9537713-9539588'), DiffValue(2, 'yabs-2.0')}
        diffs[DiffKey('user_name2', 'telegram_user2')] = {DiffValue(3, 'yabs-2.0-rerun-9')}

        diffs_without_problems = [DiffValue(4, 'yabs-2.0-rerun-9537713-9539588'), DiffValue(5, 'yabs-2.0')]

        st_issue = MagicMock(key=ST_TICKET, assignee='assignee')
        msg_tlg = self.task._YabsServerGetB2BDiffs__get_notification_message(notification_template, 'telegram', st_issue, 5, diffs, diffs_without_problems, ['on_duty'])
        msg_ych = self.task._YabsServerGetB2BDiffs__get_notification_message(notification_template, 'yachats', st_issue, 3, diffs, [], ['on_duty'])
        msg_emp = self.task._YabsServerGetB2BDiffs__get_notification_message(notification_template, 'telegram', st_issue, 0, diffs, diffs_without_problems, ['on_duty'])

        logging.info(msg_tlg)
        logging.info(msg_ych)
        logging.info(msg_emp)

        return msg_tlg, msg_ych, msg_emp

    def test_get_test_comments(self):
        ticket_comments = [MagicMock(text='==== YABS_SERVER_45_PERFORMANCE_META_BS_A_B_SAMPLED ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(red)Unresolved diff!! | 3 |'),
                           MagicMock(text='==== YABS_SERVER_40_PERFORMANCE_BEST_BSRANK ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(green)No diff!! | 22 |'),
                           MagicMock(text='==== YABS_SERVER_45_PERFORMANCE_META_BSRANK_A_B_SAMPLED ==== #| || **Status** | **Number of intervals** | **Revisions** ||'),
                           # '==== YABS_SERVER_40_FT_BS_A_B ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(red)Unresolved diff!! | 5 |',
                           MagicMock(text='==== YABS_SERVER_45_PERFORMANCE_META_YABS_A_B_SAMPLED ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(green)No diff!! | 22 |'),
                           MagicMock(text='==== YABS_SERVER_40_PERFORMANCE_BEST_YABS ==== #| || **Status** | **Number of intervals** | **Revisions** ||'),
                           MagicMock(text='==== YABS_SERVER_40_PERFORMANCE_BEST_BS ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(green)No diff!! | 22 |'),
                           # '==== YABS_SERVER_40_FT_YABS_A_B ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(red)Unresolved diff!! | 2 |',
                           MagicMock(text='==== YABS_SERVER_40_FT_BSRANK_A_B ==== #| || **Status** | **Number of intervals** | **Revisions** || || !!(green)No diff!! | 26 |'),
                           MagicMock(text='С тестами YABS_SERVER_40_FT_BS_A_B и YABS_SERVER_40_FT_YABS_A_B возникли проблемы')]

        comments = self.task._YabsServerGetB2BDiffs__get_test_comments(MagicMock(comments=MagicMock(get_all=MagicMock(return_value=ticket_comments))), TESTS)

        assert len(comments) == 7
        assert 'YABS_SERVER_40_FT_BS_A_B' not in comments
        assert 'YABS_SERVER_40_FT_YABS_A_B' not in comments
        assert 'YABS_SERVER_45_PERFORMANCE_META_BS_A_B_SAMPLED' in comments
        assert 'YABS_SERVER_40_PERFORMANCE_BEST_BSRANK' in comments

    def test_ready_to_deploy(self):
        assert not self.task.check_release_ticket(MagicMock(status=MagicMock(name='Ready To Deploy', key='readyToDeploy'), key=ST_TICKET, assignee='assignee'))
        assert self.task.check_release_ticket(MagicMock(status=MagicMock(name='Need Acceptance', key='needAcceptance'), key=ST_TICKET, assignee='assignee'))

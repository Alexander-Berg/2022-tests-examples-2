import calendar
import datetime as dt

import mock
import pytest
import responses

from library.sky import hostresolver

import sandbox.common.types.misc as ctm
from sandbox.services.modules.juggler.components import tasks_autodeploy


@pytest.fixture
def mocked_responses():
    # When set to True, this option shadows tracebacks, giving little to no information as to what has failed and why
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


@pytest.fixture
def servers_patcher(mocked_responses, serviceapi_port):
    def f(checker, server_revision, server_datetime, empty=False):
        servers = ["sandbox-fake-server{:02d}.search.yandex.net".format(i) for i in xrange(5)]
        for i, server in enumerate(servers):
            url = tasks_autodeploy.revision_url_for(server, serviceapi_port)
            headers = {ctm.HTTPHeader.TASKS_REVISION: str(server_revision)} if (i > 0 and not empty) else {}
            mocked_responses.add(responses.GET, url, headers=headers)

        resolver = mock.MagicMock()
        resolver.resolveHosts = mock.Mock(return_value=servers)
        hostresolver.Resolver = mock.MagicMock(return_value=resolver)

        checker.arcanum.commit_datetime = mock.Mock(return_value=server_datetime)
        return servers

    return f


def generate_commits(dt_start, timedelta, revision_start, amount):
    return [
        dict(
            revision=revision_start - i,
            date=calendar.timegm((dt_start - i * timedelta).timetuple()) * 1000  # real Arcanum returns milliseconds
        )
        for i in xrange(amount)
    ]


class TestRevisionChecker(object):
    MAX_DELAY = 30
    SERVERS_REVISION = 1

    def __perform_check(self, checker, expected):
        assert checker.check() == expected
        assert checker.send_to_juggler.called
        assert checker.arcanum.commit_datetime.called_with(rev=self.SERVERS_REVISION)

    def test__sanity_check(self):
        utcnow = dt.datetime.utcnow()
        commits = generate_commits(
            utcnow, timedelta=dt.timedelta(minutes=3), revision_start=100, amount=100
        )
        for i in xrange(len(commits) - 1):
            assert commits[i]["date"] > commits[i + 1]["date"]
            assert commits[i]["revision"] > commits[i + 1]["revision"]

    def test__long_silence_before_new_commit__okay(self, serviceapi_port, servers_patcher):
        # * two revisions in trunk are many hours apart;
        # * the first one is relatively fresh (less than `max_delay` minutes ago) and not deployed yet;
        # * the second one is on the server already for a long time:
        #   [ * - - - - | - - - - - - - - - - - - - - - - - - - - * ]
        #     ^HEAD     ^MAX_DELAY minutes ago                    ^SERVERS

        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        delta = dt.timedelta(hours=10)

        revisions = generate_commits(
            utcnow - dt.timedelta(minutes=self.MAX_DELAY - 20), timedelta=delta,
            revision_start=self.SERVERS_REVISION + 1, amount=2
        )

        server_commit_time = tasks_autodeploy.from_ms_timestamp(revisions[-1]["date"])
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.OK)

    def test__large_gap_between_old_commits__crit(self, serviceapi_port, servers_patcher):
        # * two revisions in trunk are many hours apart;
        # * the first one is not fresh and not deployed also;
        # * the second one is on the server already:
        #   [ - | - - - - - - - - - - - - - - - * - - - - * ]
        #       ^MAX_DELAY minutes ago          ^HEAD     ^SERVERS

        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()

        revisions = generate_commits(
            utcnow - dt.timedelta(minutes=self.MAX_DELAY * 2), timedelta=dt.timedelta(minutes=self.MAX_DELAY * 10),
            revision_start=self.SERVERS_REVISION + 1, amount=2
        )

        server_commit_time = tasks_autodeploy.from_ms_timestamp(revisions[-1]["date"])
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.CRITICAL)

    def test__regular_workflow__okay(self, serviceapi_port, servers_patcher):
        # * there are many revisions in VCS, and servers catch up on them so far without exceeding MAX_DELAY:
        #   [ * * * * * * * * * * * * * | * * ]
        #     ^HEAD   ^SERVERS          ^MAX_DELAY minutes ago

        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        delta_mins = 1
        amount = self.MAX_DELAY / delta_mins

        revisions = generate_commits(
            utcnow, timedelta=dt.timedelta(minutes=delta_mins),
            revision_start=self.SERVERS_REVISION + amount, amount=amount * 3
        )

        server_commit_time = tasks_autodeploy.from_ms_timestamp(revisions[amount - 2]["date"])
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.OK)

    def test__broken_autodeploy__crit(self, serviceapi_port, servers_patcher):
        # * there are many revisions in VCS, and servers have stopped updating:
        #   [ * * * * | * * * * * * * * * * * * * * * * * ]
        #     ^HEAD   ^MAX_DELAY minutes ago        ^SERVERS

        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        delta_mins = 1
        amount = self.MAX_DELAY / delta_mins

        revisions = generate_commits(
            utcnow, timedelta=dt.timedelta(minutes=delta_mins),
            revision_start=self.SERVERS_REVISION + amount * 2, amount=amount * 2 + 1
        )

        server_commit_time = tasks_autodeploy.from_ms_timestamp(revisions[-1]["date"])
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.CRITICAL)

    def test__regular_workflow_but_too_many_commits__okay(self, serviceapi_port, servers_patcher):
        # * there are many revisions in VCS, so many that Arcanum doesn't give us them all,
        #   so we have to check servers' minimal revision's datetime
        #   [ * * * * * * * * *  * * * * * * * * * * * * * * | * * * ]
        #     ^HEAD     ^Arcanum's API limit   ^SERVERS      ^MAX_DELAY minutes ago

        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        delta_mins = 1
        amount = self.MAX_DELAY / delta_mins

        revisions = generate_commits(
            utcnow, timedelta=dt.timedelta(minutes=delta_mins),
            revision_start=self.SERVERS_REVISION + amount, amount=max(1, amount - 10)
        )

        server_commit_time = utcnow - dt.timedelta(minutes=self.MAX_DELAY - 3)
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.OK)

    def test__too_many_commits_and_deploy_is_broken__crit(self, serviceapi_port, servers_patcher):
        # * there are many revisions in VCS, so many that Arcanum doesn't give us them all,
        #   and servers have stopped deploying
        #   [ * * * * * * * * *  * * * * * * * | * * * * * * * * * * * * * * ]
        #     ^HEAD     ^Arcanum's API limit   ^MAX_DELAY minutes ago    ^SERVERS

        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        delta_mins = 1
        amount = self.MAX_DELAY / delta_mins

        revisions = generate_commits(
            utcnow, timedelta=dt.timedelta(minutes=delta_mins),
            revision_start=self.SERVERS_REVISION + amount, amount=max(1, amount - 10)
        )

        server_commit_time = utcnow - dt.timedelta(minutes=self.MAX_DELAY * 5)
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.CRITICAL)

    def test__empty_arcanum_reply__warning(self, serviceapi_port, servers_patcher):
        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        server_commit_time = utcnow - dt.timedelta(minutes=self.MAX_DELAY * 5)
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=[])):
            self.__perform_check(checker, ctm.JugglerCheckStatus.WARNING)

    def test__empty_servers_reply__warning(self, serviceapi_port, servers_patcher):
        checker = tasks_autodeploy.TasksAutodeploy("fake-token", serviceapi_port, self.MAX_DELAY)
        checker.send_to_juggler = mock.Mock()

        utcnow = dt.datetime.utcnow()
        delta_mins = 1
        amount = self.MAX_DELAY / delta_mins

        revisions = generate_commits(
            utcnow, timedelta=dt.timedelta(minutes=delta_mins),
            revision_start=self.SERVERS_REVISION + amount, amount=max(1, amount - 10)
        )

        server_commit_time = utcnow - dt.timedelta(minutes=self.MAX_DELAY - 3)
        servers_patcher(checker, self.SERVERS_REVISION, server_commit_time, empty=True)

        with mock.patch.object(checker.arcanum, "history", mock.Mock(return_value=revisions)):
            self.__perform_check(checker, ctm.JugglerCheckStatus.WARNING)

import operator
import datetime as dt
import itertools as it

import pytest
import requests

import sandbox.common.types.misc as ctm
import sandbox.common.types.notification as ctn
import sandbox.serviceq.types as qtypes

import sandbox.yasandbox.manager.tests as manager_tests


def test__statistics_not_used_task_types(rest_session, task_manager):
    def build_task(type_, lst_run_days_ago):
        task = manager_tests._create_task(task_manager, type=type_)
        task.mapping().execution.time.started = today - dt.timedelta(days=lst_run_days_ago)
        return task.save()

    today = dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    rest_handle = rest_session.service.statistics.task.types.not_used

    ret = rest_handle.read(days_ago=180)

    assert ret == [], ret

    outdated_tasks = [
        build_task("TEST_TASK", 190),
        build_task("SERVICE_SANDBOX_OUTDATED_TASKS", 270),
    ]

    build_task("SERVICE_SANDBOX_CLIENTS_2", 181)
    build_task("SERVICE_SANDBOX_CLIENTS_2", 179)

    ret = rest_handle.read(days_ago=180)

    assert set(r["type"] for r in ret) == set(t.type for t in outdated_tasks), (ret, outdated_tasks)


def test__shortify(client_manager, rest_session):
    hosts = list(it.chain(
        ["sandbox0{:02d}.search.yandex.net".format(_) for _ in xrange(1, 11)],
        ["sandbox-storage{}.search.yandex.net".format(_) for _ in xrange(1, 11)],
    ))
    clients = []
    for h in hosts:
        c = client_manager.load(h.split(".", 2)[0], create=True)
        c.update({"system": {"fileserver": "http://{}:12345".format(h), "fqdn": h}})
        clients.append(c.hostname)

    assert (
        (rest_session >> rest_session.PLAINTEXT).service.shortify.client(clients) ==
        "+sandbox-storage{1..10} +sandbox{001..010}"
    )


class TestServiceRESTAPI:
    API_URL = "service/ui/notification"

    TEST_STATUS_STATISTICS = {
        u'absolute': {
            u'assigned': 4,
            u'deleted': 0,
            u'draft': 0,
            u'enqueued': 3273,
            u'enqueuing': 0,
            u'exception': 172,
            u'executing': 30,
            u'expired': 0,
            u'failure': 0,
            u'finishing': 0,
            u'no_res': 0,
            u'not_released': 6,
            u'preparing': 1,
            u'released': 0,
            u'releasing': 0,
            u'resuming': 0,
            u'stopped': 46,
            u'stopping': 0,
            u'success': 0,
            u'suspended': 0,
            u'suspending': 0,
            u'temporary': 0,
            u'timeout': 989,
            u'wait_mutex': 0,
            u'wait_out': 0,
            u'wait_res': 2,
            u'wait_task': 1,
            u'wait_time': 149
        },
        u'delta': {
            u'assigned': 0,
            u'deleted': 0,
            u'draft': 0,
            u'enqueued': 15,
            u'enqueuing': 0,
            u'exception': 13,
            u'executing': 26,
            u'expired': 0,
            u'failure': 63,
            u'finishing': 0,
            u'no_res': 0,
            u'not_released': 0,
            u'preparing': 1,
            u'released': 1,
            u'releasing': 0,
            u'resuming': 0,
            u'stopped': 0,
            u'stopping': 0,
            u'success': 424,
            u'suspended': 0,
            u'suspending': 0,
            u'temporary': 0,
            u'timeout': 0,
            u'wait_mutex': 0,
            u'wait_out': 0,
            u'wait_res': 0,
            u'wait_task': 1,
            u'wait_time': 0
        },
        u'resources': {
            u'broken': 14,
            u'deleted': 0,
            u'not_ready': 44,
            u'ready': 818
        },
        u'tasks': {
            u'assigned': 4,
            u'deleted': 0,
            u'draft': 0,
            u'enqueued': 3273,
            u'enqueuing': 0,
            u'exception': 172,
            u'executing': 30,
            u'expired': 0,
            u'failure': 63,
            u'finishing': 0,
            u'no_res': 0,
            u'not_released': 6,
            u'preparing': 1,
            u'released': 1,
            u'releasing': 0,
            u'resuming': 0,
            u'stopped': 46,
            u'stopping': 0,
            u'success': 424,
            u'suspended': 0,
            u'suspending': 0,
            u'temporary': 0,
            u'timeout': 989,
            u'wait_mutex': 0,
            u'wait_out': 0,
            u'wait_res': 2,
            u'wait_task': 1,
            u'wait_time': 149
        }
    }

    def prepare_status_statistics(self, statistics_controller):
        doc = statistics_controller.Model()
        doc.key = statistics_controller.Keys.STATUS
        doc.data = self.TEST_STATUS_STATISTICS
        doc.save()

    def test__ui_notifications_create(self, rest_session, rest_su_session, uinotification_controller):
        noti_data = {"severity": ctn.Severity.WARNING, "content": "TEST"}
        with pytest.raises(rest_session.HTTPError) as exc_info:
            getattr(rest_session, self.API_URL)(noti_data)
        assert exc_info.value.status == requests.codes.FORBIDDEN

        def validate(data, target):
            for field in ("content", "severity"):
                assert data[field] == target[field]
            assert "id" in data

        resp = getattr(rest_su_session, self.API_URL)(noti_data)
        validate(resp, noti_data)
        nid = resp["id"]

        new_noti_data = {"severity": ctn.Severity.CRITICAL, "content": "A-a-a-a-a-a-a-a!"}
        getattr(rest_su_session, self.API_URL)[nid] = new_noti_data
        items = getattr(rest_su_session, self.API_URL).read()
        validate([_ for _ in items if _["id"] == nid][0], new_noti_data)

    def test__ui_notifications(self, rest_su_session, rest_session, uinotification_controller):
        notifications_data = [
            getattr(rest_su_session, self.API_URL)(
                {"severity": severity, "content": "Content with severity {}".format(severity)}
            )
            for severity in ctn.Severity
        ]

        rest_path = getattr(rest_session, self.API_URL)
        notifications = rest_path.read()
        assert sorted(notifications, key=operator.itemgetter("id")) == sorted(
            notifications_data, key=operator.itemgetter("id"))

    def test__ui_notifications_delete(self, rest_su_session, rest_session, uinotification_controller):
        notifications_data = [
            getattr(rest_su_session, self.API_URL)(
                {"severity": severity, "content": "Content with severity {}".format(severity)}
            )
            for severity in ctn.Severity
        ]

        with pytest.raises(rest_session.HTTPError) as exc_info:
            del getattr(rest_session, self.API_URL)[notifications_data[0]["id"]]
        assert exc_info.value.status == requests.codes.FORBIDDEN

        del getattr(rest_su_session, self.API_URL)[notifications_data[0]["id"]]

        notifications = getattr(rest_su_session, self.API_URL).read()
        assert sorted(notifications, key=operator.itemgetter("id")) == sorted(
            notifications_data[1:], key=operator.itemgetter("id"))

    def test__server_status(self, rest_session):
        ret = rest_session.service.status.server
        assert ret["host"]
        assert ret["uptime"]
        assert ret["processes"]["workers"]

    def test__echo(self, rest_session):
        hdrs_jar = rest_session.HEADERS()
        rest_session = rest_session << rest_session.HEADERS({"X-Header": "X-Value"}) << rest_session.PLAINTEXT
        data = (rest_session >> rest_session.JSON >> hdrs_jar).service.echo("Hallo There!")
        assert data["headers"]["X-Header"] == "X-Value"
        assert hdrs_jar["X-Service-Mode"] == "normal"
        assert ctm.HTTPHeader.BACKEND_NODE in hdrs_jar
        assert ctm.HTTPHeader.TASKS_REVISION in hdrs_jar
        assert data["data"] == "Hallo There!"
        assert data["method"] == ctm.RequestMethod.POST

    def test__service_statistics_task_status(self, rest_session, statistics_controller):
        self.prepare_status_statistics(statistics_controller)

        for stat_type in ("absolute", "delta"):
            res = rest_session.service.statistics.task.status[stat_type].read()
            for status_type, statuses in res.iteritems():
                for status, count in statuses.iteritems():
                    assert count == self.TEST_STATUS_STATISTICS[stat_type][status]

    @pytest.mark.usefixtures("serviceapi", "serviceq")
    def test__service_status_q_instances(self, rest_session):
        rest_handle = rest_session.service.status.q.instances
        ret = rest_handle.read()
        assert len(ret) == 1
        assert ret[0]["status"] == qtypes.Status.PRIMARY
        assert ret[0]["port"]
        assert ret[0]["address"]

import pytest
import datetime as dt

from six.moves import http_client

from sandbox.common import rest as common_rest
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
import sandbox.common.types.scheduler as cts
import sandbox.common.types.notification as ctn

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.controller import user as user_controller
from sandbox.yasandbox.controller import scheduler as scheduler_controller

import sandbox.web.helpers as web_helpers

from sandbox.tests.common.models import user as user_test_models


def canonized_tags(obj, pop=True):
    task = obj.get("task", obj)
    reqs = task.get("requirements", task)
    tags = (reqs.pop if pop else reqs.get)("client_tags", "")
    return sorted(tag.strip() for tag in tags.split("|"))  # assume that tag expression is simple union


class TestRESTAPIScheduler(object):

    TASK_TYPES = ["UNIT_TEST", "TEST_TASK_2"]

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_create(self, task_type, rest_session, rest_session_login):
        scheduler_data = {}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler(scheduler_data)
        assert ex.value.status == http_client.BAD_REQUEST

        owner = user_controller.Group.create(mapping.Group(
            name="SCHEDULER_OWNER", users=[rest_session_login],
            juggler_settings=mapping.Group.JugglerSettings(default_host="dtest.host", default_service="dtest_service")
        )).name
        scheduler_notifications = {
            "recipients": [owner],
            "statuses": [cts.Status.STOPPED],
            "transport": ctn.Transport.EMAIL
        }
        test_tag = "test_tag"
        scheduler_juggler_notifications = {
            "recipients": [owner, "host=test.host&service=test_service"],
            "statuses": [cts.Status.STOPPED],
            "transport": ctn.Transport.JUGGLER,
            "check_status": ctn.JugglerStatus.CRIT,
            "juggler_tags": [test_tag]
        }
        scheduler_data = {
            "task_type": task_type,
            "data": {
                "owner": owner, "scheduler_notifications": [scheduler_notifications, scheduler_juggler_notifications]
            }
        }
        scheduler = rest_session.scheduler(scheduler_data)
        assert scheduler["author"] == rest_session_login
        assert scheduler["owner"] == owner
        assert scheduler["task"]["type"] == task_type
        assert scheduler["scheduler_notifications"][0]["recipients"] == scheduler_notifications["recipients"]
        assert scheduler["scheduler_notifications"][0]["statuses"] == scheduler_notifications["statuses"]
        assert scheduler["scheduler_notifications"][0]["transport"] == scheduler_notifications["transport"]
        assert (
            sorted(scheduler["scheduler_notifications"][1]["recipients"]) ==
            sorted(scheduler_juggler_notifications["recipients"])
        )
        assert scheduler["scheduler_notifications"][1]["statuses"] == scheduler_juggler_notifications["statuses"]
        assert scheduler["scheduler_notifications"][1]["transport"] == scheduler_juggler_notifications["transport"]
        assert (
            scheduler["scheduler_notifications"][1]["check_status"] == scheduler_juggler_notifications["check_status"]
        )
        assert (
            scheduler["scheduler_notifications"][1]["juggler_tags"] == scheduler_juggler_notifications["juggler_tags"]
        )

        scheduler_data.update(source=scheduler["id"])
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler(scheduler_data)
        assert ex.value.status == http_client.BAD_REQUEST

        scheduler_data = {"source": scheduler["id"]}
        scheduler_new = rest_session.scheduler(scheduler_data)
        assert canonized_tags(scheduler_new) == canonized_tags(scheduler)
        assert scheduler_new["task"] == scheduler["task"]
        assert scheduler_new["id"] != scheduler["id"]
        assert scheduler_new["owner"] == scheduler["owner"]

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__owner(self, task_type, rest_session, rest_session_login):
        scheduler_data = {"task_type": task_type}
        scheduler = rest_session.scheduler(scheduler_data)
        sched_id = scheduler["id"]

        scheduler_get = rest_session.scheduler[sched_id].read()
        assert scheduler_get["author"] == rest_session_login
        assert scheduler_get["owner"] == rest_session_login
        assert scheduler_get["task"]["owner"] == rest_session_login

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler[sched_id].update({"owner": "NON_EXISTENT_GROUP"})
        assert ex.value.status == http_client.FORBIDDEN

        user_controller.Group.create(mapping.Group(name="SCHED_OWNER", users=[rest_session_login], email="mail"))
        rest_session.scheduler[sched_id].update({"owner": "SCHED_OWNER"})

        scheduler_get = rest_session.scheduler[sched_id].read()
        assert scheduler_get["author"] == rest_session_login
        assert scheduler_get["owner"] == "SCHED_OWNER"
        assert scheduler_get["task"]["owner"] == "SCHED_OWNER"

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__update_author(self, task_type, rest_session, rest_session_login, rest_su_session):
        robot_in_group_login = user_test_models.register_robot("robot-in-group", [rest_session_login])
        other_robot_login = user_test_models.register_robot("robot-not-in-group", [rest_session_login])
        non_rest_login = user_test_models.register_user("non_rest_login")

        scheduler_data = {"task_type": task_type}
        sched_id = rest_session.scheduler(scheduler_data)["id"]

        for rest_client in (rest_session, rest_su_session):
            with pytest.raises(common_rest.Client.HTTPError) as exc:
                rest_client.scheduler[sched_id].update({"author": non_rest_login})
            assert exc.value.status == http_client.FORBIDDEN

        grp = mapping.Group(name="NEW_SCHED_OWNER", users=[non_rest_login]).save()

        with pytest.raises(common_rest.Client.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"owner": grp.name})
        assert ex.value.status == http_client.FORBIDDEN

        with pytest.raises(common_rest.Client.HTTPError) as ex:
            rest_session.scheduler[sched_id].update({"author": non_rest_login})
        assert ex.value.status == http_client.FORBIDDEN

        rest_su_session.scheduler[sched_id].update({"author": non_rest_login, "owner": grp.name})
        scheduler_get = rest_session.scheduler[sched_id].read()
        assert scheduler_get["author"] == non_rest_login
        assert scheduler_get["owner"] == grp.name

        grp.users.extend([rest_session_login, robot_in_group_login])
        grp.save()

        rest_session.scheduler[sched_id].update({"author": non_rest_login})
        rest_session.scheduler[sched_id].update({"author": rest_session_login})
        resp = rest_session.scheduler[sched_id].read()
        assert resp["author"] == rest_session_login
        assert resp["owner"] == grp.name

        with pytest.raises(common_rest.Client.HTTPError) as ex:
            rest_session.scheduler[sched_id].update({"author": other_robot_login})
        assert ex.value.status == http_client.FORBIDDEN

        rest_session.scheduler[sched_id].update({"author": robot_in_group_login})
        resp = rest_session.scheduler[sched_id].read()
        assert resp["author"] == robot_in_group_login

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__start_time(self, task_type, rest_session):
        scheduler_data = {"task_type": task_type}
        scheduler = rest_session.scheduler(scheduler_data)
        sched_id = scheduler["id"]

        scheduler_get = rest_session.scheduler[sched_id].read()
        assert scheduler_get["schedule"]["start_time"] is None
        sch = scheduler_controller.Scheduler.load(sched_id)
        assert sch.plan.start_mode == cts.StartMode.IMMEDIATELY

        start_time = web_helpers.utcdt2iso(dt.datetime(2017, 1, 1, 10, 11))
        schedule = {
            "start_time": start_time,
            "repetition": {"weekly": [0, 1, 5, 6]}
        }
        rest_session.scheduler[sched_id].update({"schedule": schedule})
        scheduler_get = rest_session.scheduler[sched_id].read()
        assert scheduler_get["schedule"]["start_time"] == start_time
        sch = scheduler_controller.Scheduler.load(sched_id)
        assert sch.plan.start_mode == cts.StartMode.SET

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_get(self, task_type, rest_session, rest_session_login, rest_su_session, rest_su_session_login):
        not_found_id = 2
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler[not_found_id].read()
        assert ex.value.status == http_client.NOT_FOUND
        assert "Scheduler #{} not found.".format(not_found_id) in str(ex.value)

        scheduler_data = {"task_type": task_type}
        scheduler = rest_session.scheduler(scheduler_data)
        scheduler_get = rest_session.scheduler[scheduler["id"]].read()
        assert canonized_tags(scheduler_get) == canonized_tags(scheduler)
        assert scheduler_get["task"] == scheduler["task"]
        assert scheduler_get["task"]["type"] == task_type
        assert scheduler_get["author"] == rest_session_login
        assert scheduler_get["rights"] == "write"

        scheduler = rest_su_session.scheduler(scheduler_data)
        scheduler_get = rest_session.scheduler[scheduler["id"]].read()
        assert scheduler_get["author"] == rest_su_session_login
        assert canonized_tags(scheduler_get) == canonized_tags(scheduler)
        assert scheduler_get["task"] == scheduler["task"]
        assert scheduler_get["rights"] == "read"

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_list(self, task_type, rest_session, rest_su_session, rest_session_login, rest_su_session_login):
        schedulers = rest_session.scheduler[:10]
        assert schedulers["total"] == len(schedulers["items"]) == 0
        assert schedulers["limit"] == 10
        test_task_data = {"task_type": "TEST_TASK"}
        unit_test_data = {"task_type": task_type}
        TEST_NUM, UNIT_NUM, SU_TEST_NUM, SU_UNIT_NUM = 3, 4, 4, 6
        total = sum((TEST_NUM, UNIT_NUM, SU_TEST_NUM, SU_UNIT_NUM))
        [rest_session.scheduler(test_task_data) for _ in range(TEST_NUM)]
        [rest_session.scheduler(unit_test_data) for _ in range(UNIT_NUM)]
        [rest_su_session.scheduler(test_task_data) for _ in range(SU_TEST_NUM)]
        [rest_su_session.scheduler(unit_test_data) for _ in range(SU_UNIT_NUM)]

        all_scheds = rest_session.scheduler[:20]
        assert all_scheds["limit"] == 20
        assert all_scheds["total"] == len(all_scheds["items"]) == total
        assert sum(1 if o["rights"] == "write" else 0 for o in all_scheds["items"]) == TEST_NUM + UNIT_NUM
        unit_scheds = rest_session.scheduler.read({"limit": 20, "task_type": task_type})
        assert unit_scheds["limit"] == 20
        assert unit_scheds["total"] == len(unit_scheds["items"]) == UNIT_NUM + SU_UNIT_NUM

        user_unit_scheds = rest_session.scheduler.read(
            {"limit": 20, "task_type": task_type, "author": rest_session_login})
        assert user_unit_scheds["total"] == len(user_unit_scheds["items"]) == UNIT_NUM
        limit = 2
        su_unit_scheds = rest_session.scheduler.read(
            {"limit": limit, "task_type": task_type, "author": rest_su_session_login})
        assert su_unit_scheds["limit"] == limit
        assert su_unit_scheds["total"] == SU_UNIT_NUM
        assert len(su_unit_scheds["items"]) == limit
        assert all(o["rights"] == "read" for o in su_unit_scheds["items"])

    def test__scheduler_list_empty(self, rest_session):
        resp = rest_session.scheduler.read(limit=0)
        assert not resp["items"]

    def test__scheduler_list_tags(
        self, rest_session, rest_su_session, rest_session_login, rest_su_session_login
    ):
        test_data = {"task_type": "TEST_TASK_2", "data": {"task": {}}}
        assert rest_session.scheduler(test_data)["id"]
        test_data["data"]["task"]["tags"] = ["aaa", "bbb"]
        sc2 = rest_session.scheduler(test_data)["id"]
        test_data["data"]["task"]["tags"] = ["bbb", "ccc"]
        sc3 = rest_session.scheduler(test_data)["id"]

        schedulers = rest_session.scheduler.read({"limit": 20, "tags": ["aaa"]})
        assert schedulers["total"] == 1
        assert schedulers["items"][0]["id"] == sc2

        schedulers = rest_session.scheduler.read({"limit": 20, "tags": ["aaa", "ccc"], "all_tags": True})
        assert schedulers["total"] == 0

        schedulers = rest_session.scheduler.read({"limit": 20, "tags": ["aaa", "ccc"], "all_tags": False})
        assert schedulers["total"] == 2
        assert set(sc["id"] for sc in schedulers["items"]) == {sc2, sc3}

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_delete(self, task_type, rest_session, rest_su_session):
        scheduler_count = 4
        scheduler_data = {"task_type": task_type}
        new_sched = rest_su_session.scheduler(scheduler_data)
        [rest_session.scheduler(scheduler_data) for _ in range(scheduler_count - 1)]
        sched_id = new_sched["id"]
        scheduler = rest_session.scheduler[sched_id].read()
        assert scheduler["rights"] == "read"
        assert scheduler["id"] == sched_id

        schedulers = rest_session.scheduler[:10]
        assert schedulers["total"] == scheduler_count

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_session.scheduler[sched_id]
        assert ex.value.status == http_client.FORBIDDEN

        del rest_su_session.scheduler[sched_id]
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler[sched_id].read()
        assert ex.value.status == http_client.NOT_FOUND

        schedulers = rest_session.scheduler[:10]
        assert schedulers["total"] == scheduler_count - 1

    def test__scheduler_return_deleted_type(self, rest_session):
        scheduler_data = {"task_type": self.TASK_TYPES[0]}
        new_sched = rest_session.scheduler(scheduler_data)
        sched_id = new_sched["id"]

        custom_fields = rest_session.scheduler[sched_id]["custom"]["fields"].read()
        assert custom_fields

        scheduler = mapping.Scheduler.objects.with_id(sched_id)
        scheduler.type = "THIS_TYPE_SHOULD_NOT_EXIST"
        scheduler.save()

        custom_fields = rest_session.scheduler[sched_id].read()["task"]["custom_fields"]
        assert not custom_fields

    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test__scheduler_update(self, task_type, rest_session, rest_su_session):
        new_sched = rest_su_session.scheduler({"task_type": task_type})
        sched_id = new_sched["id"]
        sched_id_not_found = 301
        schedule = new_sched["schedule"]
        schedule["repetition"] = None
        rest_su_session.scheduler[sched_id].update({"scheduler": schedule})
        scheduler = rest_session.scheduler[sched_id].read()
        client_tags = canonized_tags(new_sched)
        assert canonized_tags(scheduler) == client_tags
        assert scheduler["task"] == new_sched["task"]
        assert scheduler["schedule"]["repetition"] is None
        assert scheduler["schedule"]["retry"] == schedule["retry"]

        schedule["repetition"] = {"weekly": [0, 1, 5, 6]}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.FORBIDDEN

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id_not_found].update({"schedule": schedule})
        assert ex.value.status == http_client.NOT_FOUND

        rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        scheduler = rest_session.scheduler[sched_id].read()
        assert canonized_tags(scheduler) == client_tags
        assert scheduler["task"] == new_sched["task"]
        assert scheduler["schedule"]["repetition"] == schedule["repetition"]
        assert scheduler["schedule"]["retry"] == schedule["retry"]

        schedule["retry"] = {"interval": 114}
        task_settings = scheduler["task"]
        task_settings["description"] = "ANOTHER TEST DESCRIPTION"
        requirements = {
            "cores": 42,
            "disk_space": 101 << 20,
            "dns": ctm.DnsType.DNS64,
            "host": "localhost",
            "platform": "linux",
            "ram": 42 << 20,
        }
        from sandbox import sdk2
        if task_type not in sdk2.Task:
            requirements["cpu_model"] = "cpu_model_42"
        task_settings["requirements"].update(requirements)
        rest_su_session.scheduler[sched_id].update({"schedule": schedule, "task": task_settings})

        scheduler = rest_session.scheduler[sched_id].read()
        new_task_settings = scheduler["task"]
        new_task_reqs = new_task_settings.pop("requirements")
        task_reqs = task_settings.pop("requirements")

        assert canonized_tags(new_task_reqs) == client_tags
        assert new_task_reqs == task_reqs
        assert new_task_settings == task_settings
        assert scheduler["schedule"] == schedule

        schedule["repetition"] = {"weekly": [0, 1, 5, 6], "interval": 1800}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.BAD_REQUEST

        schedule["repetition"] = {}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.BAD_REQUEST

        schedule["repetition"] = {"weekly": []}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.BAD_REQUEST

        schedule["repetition"] = {"weekly": [1, 2, 2, 3]}
        rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        scheduler = rest_session.scheduler[sched_id].read()
        assert scheduler["schedule"]["repetition"] == {"weekly": [1, 2, 3]}

        schedule["repetition"] = {"weekly": [1, 7, 8]}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.BAD_REQUEST

        schedule["repetition"] = {"weekly": [1, -4]}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.BAD_REQUEST

        schedule["repetition"] = {"weekly": ["a day"]}
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_su_session.scheduler[sched_id].update({"schedule": schedule})
        assert ex.value.status == http_client.BAD_REQUEST

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__scheduler_custom_fields_update(self, task_type, rest_session):
        scheduler = rest_session.scheduler({"task_type": task_type})
        sched_id = scheduler["id"]

        fields = {"live_time": 42}
        rest_session.scheduler[sched_id].update({
            "task": {"custom_fields": [{"name": name, "value": value} for name, value in fields.items()]}
        })

        new_fields = rest_session.scheduler[sched_id].read()["task"]["custom_fields"]
        new_fields = {f["name"]: f["value"] for f in new_fields}
        for name, value in fields.items():
            assert value == new_fields[name]

        new_fields = rest_session.scheduler[sched_id].custom.fields.read()
        new_fields = {f["name"]: f["value"] for f in new_fields}
        for name, value in fields.items():
            assert value == new_fields[name]

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__scheduler_common_params_update(self, task_type, rest_session, rest_session_login):
        group = mapping.Group(name="GROUP", users=[rest_session_login], email="email@")
        group_name = user_controller.Group.create(group).name

        task_common_params = {
            "kill_timeout": 123,
            "fail_on_any_error": True,
            "hidden": True,
            "notifications": [{
                "statuses": [ctt.Status.SUCCESS],
                "transport": ctn.Transport.TELEGRAM,
                "recipients": [rest_session_login],
                "check_status": None,
                "juggler_tags": []
            }],
            "suspend_on_status": [ctt.Status.EXCEPTION],
            "score": 5
        }
        scheduler = rest_session.scheduler({"task_type": task_type, "data": {"task": task_common_params}})
        sch_id = scheduler["id"]
        task_params = rest_session.scheduler[sch_id].read()["task"]
        for name, value in task_common_params.items():
            assert value == task_params[name], name

        for param in task_common_params:
            value = task_common_params[param]
            if isinstance(value, bool):
                value = not value
            elif isinstance(value, int):
                value += 1
            task_common_params[param] = value

        rest_session.scheduler[sch_id] = {"task": task_common_params, "owner": group_name}
        response = rest_session.scheduler[sch_id].read()
        assert response["owner"] == group_name
        task_params = response["task"]
        for name, value in task_common_params.items():
            assert value == task_params[name], name

        task_common_params["notifications"][0]["statuses"] = ["PAUSED"]
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.scheduler[sch_id] = {"task": task_common_params}
        assert ex.value.status == http_client.BAD_REQUEST

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__scheduler_run_by_group_member(self, task_type, rest_session, rest_session_login, serviceq):
        another_user = user_test_models.register_user("another_user")
        group = mapping.Group(name="GROUP", users=[rest_session_login, another_user], email="email@")
        group_name = user_controller.Group.create(group).name
        init_data = {
            "task_type": task_type,
            "data": {
                "owner": group_name,
                "schedule": {
                    "repetition": {"weekly": range(7)},
                },
            },
        }

        scheduler = rest_session.scheduler(init_data)
        mapping.Scheduler.objects.filter(id=scheduler["id"]).update(set__author=another_user)
        scheduler = rest_session.scheduler[scheduler["id"]].read()
        assert scheduler["owner"] == group_name
        assert scheduler["author"] == another_user
        assert not rest_session.task.read(scheduler_id=scheduler["id"], limit=1)["items"]
        resp = rest_session.batch.schedulers.start.update(scheduler["id"])
        assert resp[0]["status"] == "SUCCESS", resp[0]
        tasks = rest_session.task.read(scheduler_id=scheduler["id"], limit=1)["items"]
        assert tasks

        resp = rest_session.scheduler.read(scheduler_id=scheduler["id"], limit=1)["items"][0]
        assert resp["task"]["last"]["id"] == tasks[0]["id"]
        resp = rest_session.scheduler[scheduler["id"]].read()
        assert resp["task"]["last"]["id"] == tasks[0]["id"]

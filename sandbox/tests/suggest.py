import httplib

import pytest

import sandbox.common.types.client as ctc

from sandbox import sdk2

import sandbox.yasandbox.manager.tests as manager_tests
import sandbox.yasandbox.database.mapping as mp
from sandbox.services.modules import task_tags_checker


class TestSuggest:
    def _tagcmp(self, a, b):
        return ctc.Query.predicates(a) == ctc.Query.predicates(b)

    def test__resource(self, rest_session):
        resp = rest_session.suggest.resource[:]
        assert isinstance(resp, list)

    def test__task(self, rest_session):
        resp = rest_session.suggest.task[:]
        assert isinstance(resp, list)

        for type_ in ["TEST_TASK", "TEST_TASK_2"]:
            resp = rest_session.suggest.task.read(type=type_)
            data = rest_session.task(type=type_)
            assert self._tagcmp(resp[0]["client_tags"], data["requirements"]["client_tags"])

    def test__task_relative_path(self, rest_session):
        import projects.sandbox.test_task as tt
        import projects.sandbox.test_task_2 as tt2

        pairs = zip(
            (tt.TestTask, tt2.TestTask2),
            ("projects/sandbox/test_task/__init__.py", "projects/sandbox/test_task_2/__init__.py")
        )

        for task_class, task_path in pairs:
            ret = next(iter(rest_session.suggest.task.read(type=task_class.type)))
            assert ret["relative_path"] == task_path, "{} is probably moved from {} to somewhere else".format(
                task_class.type, task_path
            )

    def test__group(self, rest_session, gui_su_session, gui_su_session_login, group_controller):
        resp = rest_session.suggest.group[:]
        assert len(resp) == 2  # 2 groups from res_session and gui_su_session
        group_name = 'TestGroup'
        group_controller.create(mp.Group(name=group_name, users=[gui_su_session_login], email='mail'))
        resp = rest_session.suggest.group[:]
        assert group_name.upper() in (_["name"] for _ in resp)

    def test__client(self, rest_session):
        ret = rest_session.suggest.client[:]
        assert isinstance(ret, dict)
        assert isinstance(ret['platforms'], list)
        assert isinstance(ret['hosts'], list)

        for type_ in ["TEST_TASK", "TEST_TASK_2"]:
            ret = rest_session.suggest.client.read(task_type=type_)
            data = rest_session.task(type=type_)
            assert self._tagcmp(ret["client_tags"], data["requirements"]["client_tags"])

    def test__quicksearch(self, rest_session, task_manager):
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.suggest.quicksearch.read()
        assert ex.value.status == httplib.NOT_FOUND
        task = manager_tests._create_task(task_manager, type='TEST_TASK', parameters={'descr': 'moo'})
        ret = rest_session.suggest.quicksearch[task.id][:]
        assert any('task' in o for o in ret)
        task_response = next(o['task'] for o in ret if 'task' in o)
        assert task_response['id'] == task.id

    @pytest.mark.parametrize("task_type", ["TEST_TASK", "TEST_TASK_2"])
    def test__custom_fields(self, rest_session, task_type):
        from sandbox import projects

        task_class = projects.TYPES[task_type].cls
        data = {_["name"]: _ for _ in rest_session.suggest[task_type].custom_fields[:]}
        task_parameters = {
            p.name: p
            for p in (task_class.Parameters if task_class.type in sdk2.Task else task_class.input_parameters)
        }
        missing = set(task_parameters.keys()) - set(data.keys())
        assert not missing, "api reply for {} is missing these parameters: {}".format(task_type, ", ".join(missing))

        for name, parameter in task_parameters.items():
            api_reply = data[name]
            assert parameter.required == api_reply["required"]
            assert parameter.description == api_reply["title"]

    @staticmethod
    def _update_task_tags_cache():
        for tag, hits in mp.TaskTagCache.objects().order_by("accessed").scalar("tag", "hits"):
            task_tags_checker.TaskTagsChecker._worker_proc(tag, hits)

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__task_tags(self, rest_session, task_manager, rest_session_login, test_task_2):
        task1 = manager_tests._create_task(task_manager, "TEST_TASK", owner=rest_session_login)
        task2 = test_task_2(None, description=u"Test task")
        task2.Parameters.tags = ["aaaa", "bbbb"]
        task2.save()
        rest_session.task[task1.id].tags(["aabb"])
        rest_session.task[task1.id].tags(["aaaa"])
        rest_session.task[task1.id].tags(["zz/yy"])
        self._update_task_tags_cache()

        suggest = rest_session.suggest.task.tags["aa"][:]
        assert suggest == [{"tag": "AAAA", "hits": 2}, {"tag": "AABB", "hits": 1}]

        suggest = rest_session.suggest.task.tags.read(query="aa")
        assert suggest == [{"tag": "AAAA", "hits": 2}, {"tag": "AABB", "hits": 1}]

        suggest = rest_session.suggest.task.tags.read(query="zz/")
        assert suggest == [{"tag": "ZZ/YY", "hits": 1}]

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.suggest.task.tags.read()
        assert ex.value.status == httplib.BAD_REQUEST

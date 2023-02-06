import pytest
import httplib

from sandbox.common import itertools as common_itertools
from sandbox.common.types import misc as ctm
from sandbox.common.types import task as ctt
from sandbox.common.types import client as ctc
from sandbox.common.types import template as ctte

from sandbox.yasandbox.database import mapping


def rec_check(d1, d2, skip_fields=frozenset()):
    assert type(d1) == type(d2)
    if isinstance(d1, list):
        assert len(d1) == len(d2)
        for i, v in enumerate(d1):
            rec_check(v, d2[i], skip_fields)
        return
    if isinstance(d1, dict):
        assert frozenset(d1.keys()) == frozenset(d2.keys())
        for k, v in d1.iteritems():
            if k not in skip_fields:
                rec_check(v, d2[k], skip_fields)
        return
    assert d1 == d2


class TestTemplate(object):

    def _check_result_with_empty_template(self, test_data, template, rest_session_login):
        assert template["author"] == rest_session_login
        assert template["alias"] == test_data["alias"]
        assert template["status"] == ctte.Status.READY
        assert rest_session_login in template["shared_with"]
        task = template["task"]
        assert task["type"] == test_data["task_type"]
        parameters = task["parameters"]
        input_parameters = parameters["input"]
        ordered_input_parameters = [None] * len(input_parameters)

        for name, parameter in input_parameters.iteritems():
            ordered_input_parameters[parameter["meta"]["order"]] = parameter

        template_model = mapping.TaskTemplate.objects.with_id(template["alias"])

        for index, parameter in enumerate(ordered_input_parameters):
            assert template_model.task.input_parameters[index].name == parameter["meta"]["name"]

    def test__create_empty_template(self, rest_session, rest_session_login, template_controller, task_controller):
        test_data = {
            "alias": "tmpl_1",
            "task_type": "TEST_TASK_2",
            "description": "Test template",
            "shared_with": ["user1", "user2"]
        }
        template = rest_session.template.create(**test_data)
        self._check_result_with_empty_template(test_data, template, rest_session_login)
        template_get = rest_session.template[template["alias"]].read()
        self._check_result_with_empty_template(test_data, template_get, rest_session_login)

        rest_session.template[template_get["alias"]].favorite.create()
        favorite_templates = rest_session.template.read(favorites=rest_session_login, limit=10)
        assert favorite_templates["total"] == 1
        assert len(favorite_templates["items"]) == 1
        assert favorite_templates["items"][0]["alias"] == template_get["alias"]
        rest_session.template[template_get["alias"]].favorite.delete()
        favorite_templates = rest_session.template.read(favorites=rest_session_login, limit=10)
        assert favorite_templates["total"] == 0
        assert len(favorite_templates["items"]) == 0

        rest_session.template[template["alias"]].delete()
        templates = rest_session.template.read(limit=10)
        assert len(templates["items"]) == 0
        assert templates["total"] == 0
        templates = rest_session.template.read(limit=10, status=ctte.Status.DELETED)
        assert templates["total"] == 1
        assert len(templates["items"]) == 1
        assert templates["items"][0]["alias"] == template["alias"]

    def _compare_task_and_template(self, task, template):
        template_task = template["task"]

        assert template_task["type"] == task["type"]

        for name, parameter in task["input_parameters"].iteritems():
            template_parameter = template_task["parameters"]["input"][name]
            assert parameter == template_parameter["value"]

        for name, requirement in template_task["requirements"].iteritems():
            assert task["requirements"][name] == requirement["value"]

        for name, parameter in template_task["parameters"]["common"].iteritems():
            if name == "notifications":
                continue
            assert task[name] == parameter["value"]

    def test__create_template_from_task(self, rest_session, rest_session_login, template_controller, task_controller):
        task = rest_session.task.create(
            type="TEST_TASK_2", custom_fields=[
                dict(name="live_time", value=42),
                dict(name="break_time", value=112),
                dict(name="go_to_state", value="SUCCESS"),
                dict(name="sleep_in_subprocess", value=True),
                dict(name="multiselect", value="Option One"),
                dict(name="list_of_strings", value=["1", "2", "3"]),
                dict(name="dict_of_strings", value={"k1": "v1", "k2": "v2"})
            ]
        )
        alias = "tmpl_1"
        template = rest_session.template.create(task_id=task["id"], alias=alias)
        assert template["alias"] == alias
        self._compare_task_and_template(task, template)
        template_get = rest_session.template[template["alias"]].read()
        self._compare_task_and_template(task, template_get)

        task = rest_session.task.create(
            type="TEST_TASK_2", requirements={
                "ram": 2 << 30,
                "cores": 32,
                "dns": ctm.DnsType.DNS64,
                "cpu_model": "chip",
                "platform": "linux",
                "ramdrive": {"size": 2 << 20, "type": "tmpfs"},
                "client_tags": str(ctc.Tag.SERVER),
            }
        )
        alias = "tmpl2"
        template = rest_session.template.create(task_id=task["id"], alias=alias)
        assert template["alias"] == alias
        self._compare_task_and_template(task, template)
        template_get = rest_session.template[template["alias"]].read()
        self._compare_task_and_template(task, template_get)

        task = rest_session.task.create(
            type="TEST_TASK_2",
            dump_disk_usage=False,
            tcpdump_args='"host ya.ru and port 443" -v',
            tags=["AAA", "BBB"],
            hints=[1, "abCd", ""],
            max_restarts=42,
            kill_timeout=3600,
            suspend_on_status=[ctt.Status.EXCEPTION],
            score=6,
            notifications=[
                {"statuses": [ctt.Status.SUCCESS], "transport": "email", "recipients": [rest_session_login]}],
            fail_on_any_error=True,
            hidden=True,
            priority={
                "class": ctt.Priority.Class.BACKGROUND,
                "subclass": ctt.Priority.Subclass.LOW,
            },
        )
        alias = "tmpl3"
        template = rest_session.template.create(task_id=task["id"], alias=alias)
        assert template["alias"] == alias
        self._compare_task_and_template(task, template)
        template_get = rest_session.template[template["alias"]].read()
        self._compare_task_and_template(task, template_get)

    def test_update_template(
        self, rest_session, rest_session_login, rest_session2, rest_session_login2, template_controller, task_controller
    ):
        alias = "tmpl_1"
        test_data = {
            "alias": alias,
            "task_type": "TEST_TASK_2",
            "description": "Test template",
            "shared_with": ["user1", "user2"]
        }

        rest_session.template.create(**test_data)
        base_template = rest_session.template[alias].read()
        assert rest_session_login in base_template["shared_with"]

        update_data = {
            u"description": u"Test template 2",
            u"task": {
                u"requirements": {
                    u"ram": {
                        u"value": 2 << 30,
                        u"meta": {
                            u"default_from_code": False
                        }
                    },
                    u"cores": {
                        u"meta": {
                            u"hide": True,
                        }
                    }
                },
                u"parameters": {
                    u"common": {
                        u"kill_timeout": {
                            u"value": 100,
                            u"meta": {
                                u"default_from_code": False
                            }
                        },
                        u"max_restarts": {
                            u"meta": {
                                u"hide": True
                            }
                        }
                    },
                    u"input": {
                        u"live_time": {
                            u"value": 100,
                            u"meta": {
                                u"default_from_code": False
                            }
                        },
                        u"break_time": {
                            u"meta": {
                                u"hide": True
                            }
                        },
                        u"mount_image": {
                            u"meta": {
                                u"filter": {
                                    u"type": u"SANDBOX_TASKS_RESOURCE",
                                    u"owner": u"SANDBOX",
                                    u"limit": 1,
                                    u"offset": 0
                                }
                            }
                        }
                    }
                }
            }
        }

        rest_session.template[alias].update(**update_data)
        updated_template = rest_session.template[alias].read()
        base_template = common_itertools.merge_dicts(base_template, update_data)
        rec_check(base_template, updated_template, skip_fields=frozenset(("time", )))

        template_audit = rest_session.template.audit.read(template_alias=alias, limit=10)
        assert template_audit["total"] == 1
        assert len(template_audit["items"]) == 1
        audit = template_audit["items"][0]
        assert audit["author"] == rest_session_login

        assert update_data["task"]["requirements"].keys() == audit["task"]["requirements"].keys()
        assert update_data["task"]["parameters"]["input"].keys() == audit["task"]["parameters"]["input"].keys()
        assert update_data["task"]["parameters"]["common"].keys() == audit["task"]["parameters"]["common"].keys()

        with pytest.raises(rest_session2.HTTPError) as ex:
            rest_session2.template[alias].update()
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(rest_session2.HTTPError) as ex:
            rest_session.template[alias].update(shared_with=["user1", "user2", rest_session_login2])
        assert ex.value.status == httplib.BAD_REQUEST
        rest_session.template[alias].update(shared_with=["user1", "user2", rest_session_login, rest_session_login2])
        rest_session2.template[alias].update()

    def test_create_task_from_template(
        self, rest_session, rest_session2, rest_session_login,
        rest_session_login2, template_controller, task_controller, group_controller
    ):
        group = mapping.Group(name="TEST_GROUP", users=[rest_session_login], abc="test_abc")
        group.save()
        task = rest_session.task.create(
            type="TEST_TASK_2", custom_fields=[
                dict(name="live_time", value=42),
                dict(name="break_time", value=112),
                dict(name="go_to_state", value="SUCCESS"),
                dict(name="sleep_in_subprocess", value=True),
                dict(name="multiselect", value="Option One"),
                dict(name="list_of_strings", value=["1", "2", "3"]),
                dict(name="dict_of_strings", value={"k1": "v1", "k2": "v2"})
            ],
            requirements={
                "cores": 5
            },
            owner="TEST_GROUP",
            notifications=[
                {
                    "transport": "email",
                    "statuses": [ctt.Status.SUCCESS],
                    "recipients": ["TEST_GROUP", rest_session_login]
                }
            ]
        )
        alias = "tmpl_1"
        template = rest_session.template.create(task_id=task["id"], alias=alias)
        rest_session.template[template["alias"]].update(task={
            "parameters": {
                "common": {
                    "notifications": {
                        "value": [{
                            "transport": "email",
                            "statuses": [ctt.Status.SUCCESS],
                            "recipients": ["<owner>", "<author>"]
                        }],
                        "meta": {
                            "default_from_code": False
                        }
                    }
                }
            }
        })
        task2 = rest_session.task.create(template_alias=template["alias"])
        rec_check(task["input_parameters"], task2["input_parameters"])
        rec_check(task["notifications"], task2["notifications"])
        del task["requirements"]["resources"]["url"]
        del task2["requirements"]["resources"]["url"]
        rec_check(task["requirements"], task2["requirements"])

        tasks = rest_session.task.read(template_alias=template["alias"], limit=10)
        assert tasks["total"] == 1
        assert tasks["items"][0]["id"] == task2["id"]

        template_info = {
            "alias": "tmpl2",
            "task_type": "TEST_TASK_2",
            "description": "Test template",
            "shared_with": ["user1", "user2"]
        }
        template2 = rest_session.template.create(**template_info)
        update_info = {
            "task": {
                "parameters": {
                    "input": {
                        "live_time": {
                            "value": 42,
                            "meta": {
                                "default_from_code": False
                            }
                        },
                        "break_time": {
                            "value": 112,
                            "meta": {
                                "default_from_code": False
                            }
                        },
                        "go_to_state": {
                            "value": "SUCCESS",
                            "meta": {
                                "default_from_code": False
                            }
                        },
                        "sleep_in_subprocess": {
                            "value": True,
                            "meta": {
                                "default_from_code": False
                            }
                        },
                        "multiselect": {
                            "value": "Option One",
                            "meta": {
                                "default_from_code": False
                            }
                        },
                        "list_of_strings": {
                            "value": ["1", "2", "3"],
                            "meta": {
                                "default_from_code": False
                            }
                        },
                        "dict_of_strings": {
                            "value": {"k1": "v1", "k2": "v2"},
                            "meta": {
                                "default_from_code": False
                            }
                        }
                    }
                },
                "requirements": {
                    "cores": {
                        "value": 5,
                        "meta": {
                            "default_from_code": False
                        }
                    }
                }
            }
        }
        rest_session.template[template2["alias"]].update(**update_info)
        task3 = rest_session.task.create(template_alias=template2["alias"])
        rec_check(task["input_parameters"], task3["input_parameters"])
        del task3["requirements"]["resources"]["url"]
        rec_check(task["requirements"], task3["requirements"])
        assert task3["template_alias"] == template2["alias"]

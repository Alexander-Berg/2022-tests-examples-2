import pytest

from sandbox.common import errors

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.proxy import task as task_proxy

from sandbox.yasandbox.manager import tests


class TestTask:
    @staticmethod
    def __session(controller, login):
        controller.validated(login)
        return login

    def test__mapping(self):
        task = task_proxy.Task()
        task.ctx['t'] = task_proxy.Task()
        pytest.raises(errors.TaskContextError, task.mapping)

    def test__check_ctx(self):
        task_proxy.Task.check_ctx({1: None})
        task_proxy.Task.check_ctx({False: None})
        task_proxy.Task.check_ctx({'k': None})
        task_proxy.Task.check_ctx({'k': 1})
        task_proxy.Task.check_ctx({'k': 'v'})
        task_proxy.Task.check_ctx({'k': u'v'})
        task_proxy.Task.check_ctx({'k': 0.1})
        task_proxy.Task.check_ctx({'k': [1, '2']})
        task_proxy.Task.check_ctx({'k': {'kk': [3, 4]}})
        pytest.raises(errors.TaskContextError, task_proxy.Task.check_ctx, {'k': task_proxy.Task()})
        pytest.raises(errors.TaskContextError, task_proxy.Task.check_ctx, {'k': {'k': task_proxy.Task()}})
        pytest.raises(errors.TaskContextError, task_proxy.Task.check_ctx, {'k': [task_proxy.Task()]})
        pytest.raises(errors.TaskContextError, task_proxy.Task.check_ctx, {'k': (task_proxy.Task(), )})
        pytest.raises(errors.TaskContextError, task_proxy.Task.check_ctx, {'k': {task_proxy.Task(), }})

    def test__user_has_permission__user(self, task_manager, user_controller):
        author = self.__session(user_controller, 'permissions-test-author')
        owner = self.__session(user_controller, 'permissions-test-owner')
        task = tests._create_task(task_manager, owner=owner, author=author)
        assert task.user_has_permission(owner)
        assert task.user_has_permission(author)

    def test__user_has_permission__group(self, task_manager, user_controller, group_controller):
        author = self.__session(user_controller, 'permissions-test-author')
        fellow = self.__session(user_controller, 'permissions-test-fellow')
        group_controller.create(mapping.Group(name='TESTGROUP', users=[fellow]))
        task = tests._create_task(task_manager, owner='TESTGROUP', author=author)
        assert task.user_has_permission(author)
        assert task.user_has_permission(fellow)

    def test__release_info(self, task_manager, user_controller):
        author = self.__session(user_controller, "test-author")
        task = tests._create_task(task_manager, owner=author, author=author)
        tests._create_resource(task_manager, task=task)
        assert task._release_info(author, "Comment")

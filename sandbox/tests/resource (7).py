# coding: utf-8

import py
import pytest
import logging
import os.path

logger = logging.getLogger(__name__)

from sandbox import common

from yasandbox.database import mapping
import yasandbox.manager.tests


class TestResources:
    @staticmethod
    def __session(controller, login):
        controller.validated(login)
        return login

    def test__resource_attrs_vals_type(self, task_manager):
        from yasandbox.proxy import resource as resource_proxy
        task = yasandbox.manager.tests._create_task(task_manager)
        res_params = dict(
            resource_id=0,
            name='test resource',
            file_name='resource_filename',
            file_md5='',
            resource_type='OTHER_RESOURCE',
            task_id=task.id,
            owner='unittester',
            attrs={'a': '1', 'b': '2'}
        )
        res1 = resource_proxy.Resource(**res_params)
        res1._create()
        res2 = resource_proxy.Resource(**res_params)
        res2._create()

    def test__user_has_permission__user(self, user_controller, task_manager):
        author = self.__session(user_controller, 'permissions-test-author')
        other = self.__session(user_controller, 'permissions-test-owner')
        task = yasandbox.manager.tests._create_task(
            task_manager, owner=author)
        resource = yasandbox.manager.tests._create_resource(task_manager, task=task)
        assert resource.user_has_permission(author)
        assert not resource.user_has_permission(other)

    def test__user_has_permission__group(self, task_manager, user_controller, group_controller):
        author = self.__session(user_controller, 'permissions-test-author')
        fellow = self.__session(user_controller, 'permissions-test-fellow')
        group_controller.create(mapping.Group(name='TESTGROUP', users=[author, fellow]))
        task = yasandbox.manager.tests._create_task(
            task_manager, owner='TESTGROUP', author=author
        )
        resource = yasandbox.manager.tests._create_resource(task_manager, task=task)
        assert resource.user_has_permission(author)
        assert resource.user_has_permission(fellow)


class TestFSJournal:
    def test_basic(self, task_manager):
        import stat

        journal = common.fs.FSJournal()

        # Check its a singleton
        assert journal is common.fs.FSJournal()
        task = yasandbox.manager.tests._create_task(task_manager)
        path = py.path.local(task.abs_path())

        # Register root for future remove
        root = journal.mkroot(task.id, maker=common.fs.create_task_dir, args=(task.id,))
        assert root.state == journal.Directory.State.RONLY
        assert root == root.adddir(root.path)
        assert root == root.mkdir()
        assert path.check()
        assert root.state == journal.Directory.State.RONLY

        # Register 'abc/def' subdir
        subdir = ('abc', 'def')
        d = root.mkdir(os.path.join(*subdir))
        assert d.name == subdir[1]
        assert path.join(*subdir).check()
        assert d == root.mkdir(path.join(*subdir).strpath)

        # Check parent statuses
        assert d.state == journal.Directory.State.REMOVE
        assert root.state == journal.Directory.State.RONLY

        # Check intermediate 'abc' dir
        dp = root.adddir(subdir[0])
        assert dp.name == subdir[0]
        assert dp.state == journal.Directory.State.REMOVE

        # Check for check be relative
        pytest.raises(ValueError, root.mkdir, '/tmp/abc')
        pytest.raises(ValueError, d.mkdir, dp.path)

        # Register another 'abc/ghi' subdir
        subdir2 = (subdir[0], 'ghi')
        d2 = root.adddir(os.path.join(*subdir2), state=journal.Directory.State.RONLY)
        assert not path.join(*subdir2).check()
        assert d2.state == journal.Directory.State.RONLY

        # Check state is going through parent directories, but not affects neighbours
        assert d.state == journal.Directory.State.REMOVE
        assert dp.state == journal.Directory.State.RONLY
        assert dp._state == journal.Directory.State.REMOVE
        assert root.state == journal.Directory.State.RONLY

        # Register 'jkl/mno' subdir
        subdir3 = ('jkl', 'mno')
        d3 = root.mkdir(os.path.join(*subdir3))
        assert path.join(*subdir3).check()
        assert d3.state == journal.Directory.State.REMOVE
        dp2 = root.adddir(subdir3[0])
        assert dp2.state == journal.Directory.State.REMOVE

        # Check recursive state change
        d3.state = d3.State.KEEP
        assert dp.state == journal.Directory.State.RONLY
        assert dp2.state == journal.Directory.State.KEEP
        assert root.state == journal.Directory.State.KEEP

        # Check second makedir will not reset the state
        root.mkdir(os.path.join(*subdir3))
        assert d3.state == journal.Directory.State.KEEP
        root.mkdir(os.path.join(*subdir3), journal.Directory.State.RONLY)
        assert d3.state == journal.Directory.State.KEEP
        root.mkdir(os.path.join(*subdir3), journal.Directory.State.REMOVE)
        assert d3.state == journal.Directory.State.KEEP

        # Check for check be relative
        pytest.raises(ValueError, root.mkdir, '/tmp/abc')
        pytest.raises(ValueError, d.mkdir, dp.path)
        assert dp.is_relto(d)
        assert dp.is_relto(d2)
        assert not dp.is_relto(dp2)

        # Add leafs to removal
        subdir4 = 'pqr'
        d2.mkdir(subdir4)
        assert d2.state == journal.Directory.State.RONLY
        subdir5 = 'stu'
        d3.mkdir(subdir5)
        assert d3.state == journal.Directory.State.KEEP

        logger.debug('Result tree:')
        root.tree(logger.debug)

        # Commit check - it should do nothing actually
        journal.commit(task.id)
        assert journal._roots != {}
        assert path.join(*subdir).check()
        assert path.join(*(subdir2 + (subdir4,))).check()
        assert path.join(*(subdir3 + (subdir5,))).check()
        assert path.join(*subdir2).stat().mode & stat.S_IWUSR == stat.S_IWUSR
        assert path.join(subdir[0]).stat().mode & stat.S_IWUSR == stat.S_IWUSR
        assert path.join(*subdir3).stat().mode & stat.S_IWUSR == stat.S_IWUSR
        assert path.join(subdir3[0]).stat().mode & stat.S_IWUSR == stat.S_IWUSR
        assert path.stat().mode & stat.S_IWUSR == stat.S_IWUSR

        # This should set readonly - nothing to keep
        d3.state = d3.State.RONLY
        journal.commit(task.id)
        assert journal._roots == {}
        assert not path.join(*subdir).check()
        assert not path.join(*(subdir2 + (subdir4,))).check()
        assert not path.join(*(subdir3 + (subdir5,))).check()
        assert path.join(*subdir2).stat().mode & stat.S_IWUSR != stat.S_IWUSR
        assert path.join(subdir[0]).stat().mode & stat.S_IWUSR != stat.S_IWUSR
        assert path.join(*subdir3).stat().mode & stat.S_IWUSR != stat.S_IWUSR
        assert path.join(subdir3[0]).stat().mode & stat.S_IWUSR != stat.S_IWUSR
        assert path.stat().mode & stat.S_IWUSR != stat.S_IWUSR

        # Drop the rest
        root = journal.mkroot(task.id, maker=common.fs.create_task_dir, args=(task.id,))
        # Place write privileges on 'abc'
        dp = root.adddir(subdir[0])
        dp.mkdir()
        # .. and on 'ghi' subdir of 'abc'
        root.mkdir(os.path.join(*subdir2))
        root.adddir(os.path.join(*subdir3))
        journal.clear()

        assert dp.children == {}
        assert journal._roots == {}
        # The task's directory should exists and be empty
        assert path.check()
        assert not path.join(subdir[0]).check()
        assert not path.join(subdir[0]).check()
        assert path.stat().mode & stat.S_IWUSR != stat.S_IWUSR

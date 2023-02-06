from unittest.mock import MagicMock

import metrika.admin.python.zooface.recursive_deleter.tests.utils as utils
import pytest


class TestHelper:
    @pytest.fixture(autouse=True)
    def clear_db(self, db, pg_client):
        utils.execute_query(pg_client, 'DELETE FROM tasks')

    @pytest.fixture(autouse=True)
    def tree(self, helper):
        utils.create_tree(helper, {
            'test': {
                'qwe': {
                    'q': {'1': {}, '2': {}}
                },
                'asd': {
                    'a': {'1': {}}
                }
            }
        })

    @staticmethod
    def check_task(task, started=True, status='FINISHED', total=0, deleted=None):
        assert bool(task['started']) == started
        assert bool(task['finished']) == (status == 'FINISHED')
        assert task['status'] == status
        assert task['total'] == total
        assert task['deleted'] == total if deleted is None else deleted

    def test_no_tasks(self, helper):
        assert helper.process_tasks() is None

    @pytest.mark.parametrize('node, total, tree_after', [
        (
            '/qwe', 0,
            {
                'test': {
                    'qwe': {
                        'q': {'1': {}, '2': {}}
                    },
                    'asd': {
                        'a': {'1': {}}
                    }
                }
            }

        ),

        (
            '/test/qwe/q/1', 1,
            {
                'test': {
                    'qwe': {
                        'q': {'2': {}}
                    },
                    'asd': {
                        'a': {'1': {}}
                    }
                }
            }
        ),

        (
            '/test/qwe/q', 3,
            {
                'test': {
                    'qwe': {},
                    'asd': {
                        'a': {'1': {}}
                    }
                }
            }
        ),

        (
            '/test/asd/', 3,
            {
                'test': {
                    'qwe': {
                        'q': {'1': {}, '2': {}}
                    }
                }
            }
        ),

        (
            'test', 8, {}
        )
    ])
    def test_delete_recursive(self, pg_client, helper, node, total, tree_after):
        task_id = utils.insert_task(pg_client, node)
        helper.process_tasks()
        task = utils.get_task(pg_client, task_id)
        self.check_task(task, total=total)
        assert utils.dump_tree(helper, '/test') == tree_after

    def test_delete_flaky(self, pg_client, helper, patch_delete):
        task_id = utils.insert_task(pg_client, '/test')
        for i in range(7):
            with pytest.raises(Exception, match='Flaky he-he'):
                helper.process_tasks()

            task = utils.get_task(pg_client, task_id)
            self.check_task(task, started=True, status='ENQUEUED', total=8, deleted=i + 1)

        helper.process_tasks()
        task = utils.get_task(pg_client, task_id)
        self.check_task(task, started=True, status='FINISHED', total=8, deleted=8)
        assert utils.dump_tree(helper, '/test') == {}

    def test_update_deleted(self, pg_client, helper, patch_execute):
        helper.config.update_chunk = 3
        task_id = utils.insert_task(pg_client, '/test')
        helper.process_tasks()
        task = utils.get_task(pg_client, task_id)
        self.check_task(task, total=8)
        assert helper.api_client.update_task.values == [3, 6, 8, 8]

    def test_nodes_count_approx(self, helper, patch_api):
        helper.config.max_child_count = 5
        tree = {
            'childs': {
                str(i): {str(i): {}}
                for i in range(helper.config.max_child_count + 1)
            }
        }
        utils.create_tree(helper, tree)
        assert helper.nodes_count(helper.zk_client, '/childs', MagicMock()) == (1 + int(len(tree['childs']) * helper.APPROX_COEF), True)
        assert utils.dump_tree(helper, '/childs') == tree

    def test_nodes_delete_approx(self, pg_client, helper):
        task_id = utils.insert_task(pg_client, '/childs')
        task = utils.get_task(pg_client, task_id)
        helper.config.max_child_count = 5
        tree = {
            'childs': {
                str(i): {str(i): {}}
                for i in range(helper.config.max_child_count + 1)
            }
        }
        utils.create_tree(helper, tree)

        assert helper.nodes_count(helper.zk_client, '/childs', task)[1]
        helper.process_tasks()
        task = utils.get_task(pg_client, task_id)
        nodes = 1 + len(tree['childs']) * 2
        self.check_task(task, total=nodes)
        assert not task['approximately']

    def test_stopped_during_delete(self, pg_client, helper, patch_delete_cancel):
        task_id = utils.insert_task(pg_client, '/childs')
        childs = helper.config.delete_chunk * 2
        utils.create_tree(helper, {
            'childs': {i: {} for i in range(childs)}
        })

        helper.process_tasks()
        task = utils.get_task(pg_client, task_id)
        assert task['status'] == 'STOPPED'
        assert len(utils.dump_tree(helper, '/childs')['childs']) == childs - helper.config.delete_chunk

    def test_stopped_berfore_start(self, pg_client, helper):
        task_id = utils.insert_task(pg_client, '/test_stopping')
        tree = {
            'test_stopping': {str(i): {} for i in range(5)}
        }
        utils.create_tree(helper, tree)
        utils.cancel_task(pg_client, task_id)

        helper.process_tasks()
        task = utils.get_task(pg_client, task_id)
        assert task['status'] == 'STOPPED'
        assert utils.dump_tree(helper, '/test_stopping') == tree

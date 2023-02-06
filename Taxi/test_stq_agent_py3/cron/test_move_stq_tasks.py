#  pylint: disable=unused-variable, protected-access
import pytest

from stq_agent_py3.common import stq_config
from stq_agent_py3.common import stq_meta_data
from stq_agent_py3.common import stq_shards
from stq_agent_py3.generated.cron import run_cron
from test_stq_agent_py3 import util


@pytest.mark.fillstqdb(
    collections=[
        ('stq', 'dbstq', 'example_queue_0'),
        ('stq', 'dbstq', 'example_queue_1'),
        ('stq', 'dbstq', 'example_queue_2'),
    ],
)
@util.parametrize_data(
    __file__,
    'test_move_stq_tasks_expected_tasks.json',
    ('expected_tasks', 'expected_backup'),
)
@pytest.mark.now('2021-02-20 10:02:00')
async def test_move_stq_tasks(
        web_app_client, web_context, expected_backup, expected_tasks, patch,
):
    @patch('stq_agent_py3.tools.move_stq_tasks.get_backup_key')
    def get_backup_key(*args, **kwargs):
        return 'backup'

    await run_cron.main(['stq_agent_py3.crontasks.move_stq_tasks', '-t', '0'])
    stq_mongo = stq_shards.StqMongoWrapper(
        list(item[0] for item in expected_tasks), web_context.secdist,
    )

    for shard_info, tasks in expected_tasks:
        shard = stq_mongo.get_shard_collection(shard_info)
        docs = [doc['_id'] for doc in await shard.find({}).to_list(None)]
        assert (shard_info, sorted(docs)) == (shard_info, sorted(tasks))

    config = await stq_config.get_configs(
        web_context, queue_name='example_queue', need_meta_data=True,
    )
    serialized_config = config.changing_database_meta_data.serialize()
    assert serialized_config['backup_collections'] == expected_backup
    assert serialized_config.get('database_change_status') is None
    assert serialized_config.get('old_shards') is None
    assert serialized_config.get('moved_shards') is None

    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'example_queue',
            'dev_team': 'some_team',
            'tasks_type': 'all',
        },
    )
    assert response.status == 200


@pytest.mark.fillstqdb(collections=[('stq', 'dbstq', 'example_queue1_0')])
@util.parametrize_data(
    __file__,
    'test_move_stq_tasks_stop_cron.json',
    ('new_data', 'expected_backup', 'expected_tasks'),
)
@pytest.mark.now('2021-02-20 10:02:00')
async def test_stop_cron_because_of_database_returning(
        web_app_client,
        web_context,
        new_data,
        expected_backup,
        expected_tasks,
        patch,
):
    @patch('stq_agent_py3.tools.move_stq_tasks.get_backup_key')
    def get_backup_key(*args, **kwargs):
        return 'backup'

    @patch('stq_agent_py3.tools.move_stq_tasks._modify_queue_for_test')
    async def _modify_queue_for_test():
        await web_app_client.put('/queue/modify/', json=new_data)

    await run_cron.main(['stq_agent_py3.crontasks.move_stq_tasks', '-t', '0'])
    stq_mongo = stq_shards.StqMongoWrapper(
        list(item[0] for item in expected_tasks), web_context.secdist,
    )

    for shard_info, tasks in expected_tasks:
        shard = stq_mongo.get_shard_collection(shard_info)
        docs = [doc['_id'] for doc in await shard.find({}).to_list(None)]
        assert (shard_info, sorted(docs)) == (shard_info, sorted(tasks))

    config = await stq_config.get_configs(
        web_context, queue_name='example_queue1', need_meta_data=True,
    )
    serialized_config = config.changing_database_meta_data.serialize()
    assert (
        serialized_config.get('database_change_status')
        == stq_meta_data.CONFIG_CHANGED
    )
    assert serialized_config.get('old_shards') == {
        '1': {
            'collection': 'example_queue1_1',
            'connection_name': 'stq',
            'database': 'dbstq',
        },
    }
    assert serialized_config.get('moved_shards') is None
    assert serialized_config.get('backup_collections') == expected_backup

    response = await web_app_client.post(
        '/tasks/remove_all/',
        json={
            'queue_name': 'example_queue1',
            'dev_team': 'some_team',
            'tasks_type': 'all',
        },
    )
    assert response.status == 200


@pytest.mark.now('2021-02-20 10:00:30')
async def test_move_stq_tasks_if_not_ready(web_context):

    await run_cron.main(['stq_agent_py3.crontasks.move_stq_tasks', '-t', '0'])

    config = await stq_config.get_configs(
        web_context, queue_name='example_queue2', need_meta_data=True,
    )
    serialized_config = config.changing_database_meta_data.serialize()
    assert serialized_config.get('old_shards') == {
        '0': {
            'collection': 'example_queue1_0',
            'connection_name': 'stq',
            'database': 'dbstq',
        },
    }

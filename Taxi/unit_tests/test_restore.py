import unittest
from unittest import mock

from core.errors import AccessDenied
from suite.gp import GPMeta, GPTypes
from suite.s3 import S3Functions, S3BackupGPMeta
from task import restore


RESTORE_REQUEST_QUEUE = {
    "object_id": 298500,
    "s3_backup_id": 2489646,
    "force_restore": True,
    "metadata": True,
    "data": True,
    "partition_meta": "{\"start_dttm\": \"2021-10-01 00:00:00\", \"end_dttm\": \"2021-11-24 00:00:00\"}",
    "subpartition_meta": "{}",
    "database_name": "unittest_db",
    "queued_username": "unittest_user",
    "dependent": True,
    "schema_name_prefix": "unittest_user",
    "use_legacy_hashops": False,
    "skip_view": False,
}

GPMETA = {
    "type": GPTypes.TABLE,
    "partitions": []
}

BACKUP = {
    "data": True,
    "metadata": True
}


class TestGPMetaException(Exception):
    pass


class TestS3BackupException(Exception):
    pass


def base_task_init_mock(self, queue_name: str, process_uuid: str):
    self.pgaas_conn = mock.MagicMock()
    self.gp_conn = mock.MagicMock()


def restore_task_init_mock(restore_info):
    def _get_restore_information(self):
        self._timer_measurements = {}
        if not restore_info:
            return False

        for k, v in restore_info.items():
            setattr(self, f'_{k}', v)
        return True

    return _get_restore_information


def gp_meta_mock(attrs=None):
    if attrs is None:
        attrs = {}
    return mock.Mock(
        autospec=True,
        return_value=mock.Mock(spec=GPMeta, **{**GPMETA, **attrs})
    )


def backup_mock(attrs=None):
    if attrs is None:
        attrs = {}
    return mock.Mock(
        autospec=True,
        return_value=mock.Mock(spec=S3BackupGPMeta, **{**BACKUP, **attrs})
    )


@mock.patch('task.restore.BaseTask.__init__', base_task_init_mock)
@mock.patch('task.restore.S3Functions', mock.Mock(spec=S3Functions))
@mock.patch('task.restore.Restore._restore_data', return_value=None)
@mock.patch('task.restore.Restore._restore_metadata', return_value=None)
@mock.patch('task.restore.Restore._update_pgaas_restore_queue', return_value=None)
@mock.patch('task.restore.Restore._add_dependent_objects_to_restore_queue', return_value=None)
class TestRestoreProcess(unittest.TestCase):
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock())
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', backup_mock())
    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock(RESTORE_REQUEST_QUEUE))
    def test_full_case(self,
                       add_dependent_mock,
                       update_restore_queue_mock,
                       restore_metadata_mock,
                       restore_data_method):
        restore.Restore('restore_uuid', 'user_name')._process()

        update_restore_queue_mock.assert_called_once()
        restore_metadata_mock.assert_called_once()
        restore_data_method.assert_called_once()
        add_dependent_mock.assert_called_once()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock({**RESTORE_REQUEST_QUEUE, 'metadata': False}))
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock())
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', backup_mock())
    def test_no_metadata(self,
                         add_dependent_mock,
                         update_restore_queue_mock,
                         restore_metadata_mock,
                         restore_data_method):
        restore.Restore('restore_uuid', 'user_name')._process()

        update_restore_queue_mock.assert_called_once()
        restore_metadata_mock.assert_not_called()
        restore_data_method.assert_called_once()
        add_dependent_mock.assert_called_once()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock(RESTORE_REQUEST_QUEUE))
    @mock.patch('task.restore.get_gp_meta_by_id', mock.Mock(side_effect=TestGPMetaException))
    def test_no_gp_meta(self,
                        add_dependent_mock,
                        update_restore_queue_mock,
                        restore_metadata_mock,
                        restore_data_method):
        with self.assertRaises(TestGPMetaException):
            restore.Restore('restore_uuid', 'user_name')._process()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock(RESTORE_REQUEST_QUEUE))
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock())
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', mock.Mock(side_effect=TestS3BackupException))
    def test_no_backup(self,
                       add_dependent_mock,
                       update_restore_queue_mock,
                       restore_metadata_mock,
                       restore_data_method, ):
        with self.assertRaises(TestS3BackupException):
            restore.Restore('restore_uuid', 'user_name')._process()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock(RESTORE_REQUEST_QUEUE))
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock({'type': GPTypes.PARTITION}))
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', backup_mock())
    def test_restore_partition(self,
                               add_dependent_mock,
                               update_restore_queue_mock,
                               restore_metadata_mock,
                               restore_data_method):
        restore.Restore('restore_uuid', 'user_name')._process()
        update_restore_queue_mock.assert_called_once()
        restore_metadata_mock.assert_not_called()
        restore_data_method.assert_called_once()
        add_dependent_mock.assert_called_once()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock(RESTORE_REQUEST_QUEUE))
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock({'type': GPTypes.VIEW}))
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', backup_mock())
    def test_restore_view(self,
                          add_dependent_mock,
                          update_restore_queue_mock,
                          restore_metadata_mock,
                          restore_data_method):
        restore.Restore('restore_uuid', 'user_name')._process()

        update_restore_queue_mock.assert_called_once()
        restore_metadata_mock.assert_called_once()
        restore_data_method.assert_not_called()
        add_dependent_mock.assert_called_once()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock(RESTORE_REQUEST_QUEUE))
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock({'partitions': ['not_empty']}))
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', backup_mock())
    def test_skip_restore_for_existing_partition(self,
                          add_dependent_mock,
                          update_restore_queue_mock,
                          restore_metadata_mock,
                          restore_data_method):
        restore.Restore('restore_uuid', 'user_name')._process()

        update_restore_queue_mock.assert_called_once()
        restore_metadata_mock.assert_called_once()
        restore_data_method.assert_not_called()
        add_dependent_mock.assert_called_once()

    @mock.patch('task.restore.Restore._get_restore_information',
                restore_task_init_mock({**RESTORE_REQUEST_QUEUE, 'force_restore': False}))
    @mock.patch('task.restore.get_gp_meta_by_id', gp_meta_mock())
    @mock.patch('task.restore.get_s3_backup_gp_meta_by_id', backup_mock())
    @mock.patch('task.restore.Restore._check_table_or_partition_exists', mock.Mock(return_value=True))
    @mock.patch('task.restore.Restore._check_row_exists', mock.Mock(return_value=True))
    def test_force_restore_error(self,
                          add_dependent_mock,
                          update_restore_queue_mock,
                          restore_metadata_mock,
                          restore_data_method):
        with self.assertRaises(Exception) as e:
            restore.Restore('restore_uuid', 'user_name')._process()

        self.assertEqual(
            ('There are rows exists in the table or partition. Use force_restore to ignore rows',),
            e.exception.args
        )

        update_restore_queue_mock.assert_not_called()
        restore_metadata_mock.assert_not_called()
        restore_data_method.assert_not_called()
        add_dependent_mock.assert_not_called()



RESTORE_REQUEST_HTTP = dict(
    user_name='user_name',
    database_name='unittest',
    object_name='schema_name.object_name',
    metadata_flg='metadata_flg',
    data_flg='data_flg',
    force_restore_flg='force_restore_flg',
    from_database_name='unittest',

    dependent_flg='dependent_flg',
    partition_meta='partition_meta',
    subpartition_meta='subpartition_meta',
    parent_restore_uuid=None,
    skip_access_error=False,
    schema_name_prefix='schema_name_prefix',
    use_legacy_hashops_flg='use_legacy_hashops_flg',
    skip_view_flg='skip_view_flg'
)


class TestAlreadyInQueue(unittest.TestCase):
    @mock.patch('task.restore.PGaaSConnection')
    def test_already_in_queue(self, pgaas_mock):
        restore_request = dict(
            object_id='object_id',
            user_name='user_name',
            database_name='database_name',
            from_database_name='from_database_name',
            schema_name_prefix='schema_name_prefix'
        )

        restore_queue_response = (
            dict(restore_uuid='1'),
            dict(restore_uuid='2')
        )

        pgaas_mock.execute_and_get_dict_result.return_value = restore_queue_response
        self.assertEqual(
            restore.already_in_restore_queue(
                pgaas_mock,
                **restore_request
            ),
            restore_queue_response[-1]['restore_uuid']
        )

        pgaas_mock.execute_and_get_dict_result.return_value = ()
        self.assertIsNone(
            restore.already_in_restore_queue(
                pgaas_mock,
                **restore_request
            )
        )


PG_GET_OBJECT_INFORMATION_DATA = (
    {'object_id': 123, 'owner_name': 'owner_name', 's3_backup_id': 's3_backup_id'},)
PG_ADD_TO_RESTORE_QUEUE_DATA = (
    {'restore_uuid': 'restore_uuid'},)

DB_RESPONSES = (
    PG_GET_OBJECT_INFORMATION_DATA,
    PG_ADD_TO_RESTORE_QUEUE_DATA,
)


@mock.patch('task.restore.restore.apply_async', return_value=mock.MagicMock(return_value=None))
@mock.patch('task.restore.already_in_restore_queue', return_value=None)
class TestAddToRestoreQueue(unittest.TestCase):
    @mock.patch(
        'task.restore.PGaaSConnection',
        return_value=mock.MagicMock(
            **{'execute_and_get_dict_result.side_effect': DB_RESPONSES}))
    @mock.patch(
        'task.restore.get_permission_extra_parameter',
        return_value={'access-to-object-users': ['owner_name']}
    )
    def test_add(self, permission_mock, pgaas_mock, restore_queue_mock, celery_task_mock):
        self.assertEqual(
            'restore_uuid',
            restore.add_object_to_restore_queue(**RESTORE_REQUEST_HTTP))

        celery_task_mock.assert_called_once()
        self.assertEqual('restore_uuid', celery_task_mock.call_args[-1]['kwargs']['restore_uuid'])
        self.assertEqual('user_name', celery_task_mock.call_args[-1]['kwargs']['queued_username'])
        self.assertEqual('test_restore', celery_task_mock.call_args[-1]['queue'])

    @mock.patch('task.restore.PGaaSConnection',
                return_value=mock.MagicMock(**{'execute_and_get_dict_result.side_effect': DB_RESPONSES}))
    @mock.patch('task.restore.get_permission_extra_parameter', return_value={})
    def test_not_add(self, permission_mock, pgaas_mock, restore_queue_mock, celery_task_mock):
        with self.assertRaises(AccessDenied):
            restore.add_object_to_restore_queue(**RESTORE_REQUEST_HTTP)
        celery_task_mock.assert_not_called()

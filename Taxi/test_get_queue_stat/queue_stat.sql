INSERT INTO queue.restore (database_name, queued_username, restore_status, update_dttm,
                           restore_uuid, object_id, s3_backup_id,  partition_meta, subpartition_meta,  schema_name_prefix, process_message, force_restore_flg, metadata_flg, data_flg, dependent_flg, use_legacy_hashops_flg, restore_times, start_restore_dttm, end_restore_dttm, skip_view_flg)
                    VALUES ('butthead', 'unittest_user', null, now(),
                            'b3173a9f-2eb0-879d-0ca5-b43941dd27b1', 552171, 3443710, '{"start_dttm": "2022-06-01 00:00:00", "end_dttm": "2022-07-30 00:00:00"}', '{}', 'ae_vetrov', null, true, true, true, true, false, null, null, null, false);
INSERT INTO queue.restore (database_name, queued_username, restore_status, update_dttm,
                           restore_uuid, object_id, s3_backup_id,  partition_meta, subpartition_meta,  schema_name_prefix, process_message, force_restore_flg, metadata_flg, data_flg, dependent_flg, use_legacy_hashops_flg, restore_times, start_restore_dttm, end_restore_dttm, skip_view_flg)
                    VALUES ('butthead', 'unittest_user', 'success', now() - interval '1 minute',
                            'b3173a9f-2eb0-879d-0ca5-b43941dd27b2', 552171, 3443710, '{"start_dttm": "2022-06-01 00:00:00", "end_dttm": "2022-07-30 00:00:00"}', '{}', 'ae_vetrov', null, true, true, true, true, false, null, null, null, false);
INSERT INTO queue.restore (database_name, queued_username, restore_status, update_dttm,
                           restore_uuid, object_id, s3_backup_id,  partition_meta, subpartition_meta,  schema_name_prefix, process_message, force_restore_flg, metadata_flg, data_flg, dependent_flg, use_legacy_hashops_flg, restore_times, start_restore_dttm, end_restore_dttm, skip_view_flg)
                    VALUES ('ritchie', 'matseevski', null, now() - interval '1 minute',
                            'b3173a9f-2eb0-879d-0ca5-b43941dd27b3', 552171, 3443710, '{"start_dttm": "2022-06-01 00:00:00", "end_dttm": "2022-07-30 00:00:00"}', '{}', 'ae_vetrov', null, true, true, true, true, false, null, null, null, false);
INSERT INTO queue.restore (database_name, queued_username, restore_status, update_dttm,
                           restore_uuid, object_id, s3_backup_id,  partition_meta, subpartition_meta,  schema_name_prefix, process_message, force_restore_flg, metadata_flg, data_flg, dependent_flg, use_legacy_hashops_flg, restore_times, start_restore_dttm, end_restore_dttm, skip_view_flg)
                    VALUES ('ritchie', 'matseevski', 'error', now() - interval '1 minute',
                            'b3173a9f-2eb0-879d-0ca5-b43941dd27b4', 552171, 3443710, '{"start_dttm": "2022-06-01 00:00:00", "end_dttm": "2022-07-30 00:00:00"}', '{}', 'ae_vetrov', null, true, true, true, true, false, null, null, null, false);
INSERT INTO queue.restore (database_name, queued_username, restore_status, update_dttm,
                           restore_uuid, object_id, s3_backup_id,  partition_meta, subpartition_meta,  schema_name_prefix, process_message, force_restore_flg, metadata_flg, data_flg, dependent_flg, use_legacy_hashops_flg, restore_times, start_restore_dttm, end_restore_dttm, skip_view_flg)
                    VALUES ('ritchie', 'matseevski', 'error', now() - interval '1 minute',
                            'b3173a9f-2eb0-879d-0ca5-b43941dd27b5', 552171, 3443710, '{"start_dttm": "2022-06-01 00:00:00", "end_dttm": "2022-07-30 00:00:00"}', '{}', 'ae_vetrov', null, true, true, true, true, false, null, null, null, false);

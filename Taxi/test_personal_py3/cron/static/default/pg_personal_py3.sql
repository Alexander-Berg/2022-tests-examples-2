INSERT INTO personal_export.export_info (
    id,
    yandex_login,
    ticket,
    input_yt_table,
    output_table_ttl,
    need_duplicate_columns,
    show_export_status_column)
VALUES      (1, 'test_login', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 1,
             false, false),
            (2, 'test_login', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 1,
             false, true),
            (3, 'test_login', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 1,
             true, false),
            (4, 'test_login', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 1,
             true, true),
            (5, 'test_login_wrong_input_table', 'TESTTICKET-1',
             '//home/testsuite/wrong_path', 12,
             true, true),
            (6, 'test_value_to_id', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 12,
             true, true),
            (111, 'test_full_table', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 12,
             false, false),
            (222, 'test_full_duplicate_table', 'TESTTICKET-1',
             '//home/testsuite/yt_pd_input_table', 12,
             true, true)
;

INSERT INTO personal_export.export_info
            (id, yandex_login, ticket, input_yt_table, output_table_ttl,
            created_at, updated_at, status)
VALUES      (7, 'test_login_need_post_msg_status', 'TESTTICKET-2',
             '//home/testsuite/yt_pd_input_table', 1,
             now() - interval '2d', now() - interval '2d', 'need_post_msg')
;

INSERT INTO personal_export.export_columns_data (
    export_type,
    data_type,
    yt_column_name,
    export_id)
VALUES
    ('from_id_to_value', 'phones', 'phone_id', 1),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 1),
    ('from_id_to_value', 'phones', 'phone_id', 2),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 2),
    ('from_id_to_value', 'phones', 'phone_id', 3),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 3),
    ('from_id_to_value', 'phones', 'phone_id', 4),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 4),
    ('from_id_to_value', 'phones', 'phone_id', 5),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 5),
    ('from_value_to_id', 'phones', 'phone', 6),
    ('from_value_to_id', 'driver_licenses', 'driver_license', 6),
    ('from_id_to_value', 'phones', 'phone_id', 111),
    ('from_id_to_value', 'phones', 'other_phone_id', 111),
    ('from_value_to_id', 'phones', 'phone', 111),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 111),
    ('from_value_to_id', 'driver_licenses', 'driver_license', 111),
    ('from_id_to_value', 'phones', 'phone_id', 222),
    ('from_id_to_value', 'phones', 'other_phone_id', 222),
    ('from_value_to_id', 'phones', 'phone', 222),
    ('from_id_to_value', 'driver_licenses', 'driver_license_id', 222),
    ('from_value_to_id', 'driver_licenses', 'driver_license', 222)
;

INSERT INTO yt_export.last_synced_created_time
            (data_type, last_created)
VALUES ('phones', '2020-10-28T21:35:32.015000+03:00'),
       ('driver_licenses', '2020-10-28T21:35:32.015000+03:00'),
       ('identifications', '2020-10-28T21:35:32.015000+03:00')
;


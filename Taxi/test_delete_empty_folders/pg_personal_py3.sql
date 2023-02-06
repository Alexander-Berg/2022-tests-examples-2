INSERT INTO personal_export.export_info
            (yandex_login, ticket, input_yt_table, output_table_ttl,
            created_at, updated_at, status)
VALUES      ('test_login', 'TESTTICKET-2', '//home/testsuite/yt_pd_input_table', 1,
             now() - interval '2d', now() - interval '2d', 'finished'),
            ('test_login2', 'TESTTICKET-3', '//home/testsuite/yt_pd_input_table', 2,
             now() - interval '3d', now() - interval '3d', 'finished');

-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/compiled_rides
CREATE TABLE IF NOT EXISTS public.compiled_rides (
    history_event_id BIGSERIAL PRIMARY KEY,
    history_user_id text NOT NULL,
    history_originator_id text,
    history_action text NOT NULL,
    history_timestamp integer NOT NULL,
    history_comment text,
    session_id TEXT NOT NULL,
    object_id uuid,
    price integer NOT NULL,
    duration integer NOT NULL,
    start integer NOT NULL,
    finish integer NOT NULL,
    meta JSON,
    meta_proto TEXT,
    hard_proto TEXT
);

-- https://a.yandex-team.ru/arc/trunk/arcadia/drive/backend/tables/user
CREATE TABLE IF NOT EXISTS public."user" (
    first_name character varying(30) NOT NULL,
    last_name character varying(150) NOT NULL,
    address text,
    email character varying(254),
    date_joined timestamp with time zone NOT NULL,
    id uuid PRIMARY KEY,
    uid bigint,
    username character varying(64) NOT NULL,
    patronymic_name character varying(64) NOT NULL,
    phone character varying(128),
    status character varying(16) NOT NULL,
    registered_at timestamp with time zone,
    is_phone_verified boolean,
    is_email_verified boolean,
    passport_names_hash character varying(64),
    passport_number_hash character varying(64),
    driving_license_number_hash character varying(64),
    is_first_riding boolean DEFAULT true,
    driving_license_ds_revision character varying(64),
    passport_ds_revision character varying(64),
    registration_geo character varying(16),
    has_at_mark boolean,
    environment character varying(254)
);

CREATE TABLE IF NOT EXISTS scooters_misc.insurance_policies (
    policy_id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL UNIQUE,
    policy_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    data JSONB
);

TRUNCATE public.compiled_rides;
TRUNCATE public."user";
TRUNCATE scooters_misc.insurance_policies;
TRUNCATE scooters_misc.drive_tables_cursors;

INSERT INTO scooters_misc.drive_tables_cursors
    (drive_table, drive_cursor)
VALUES 
    ('insurance_writer:compiled_rides', 1)
ON CONFLICT DO NOTHING;

INSERT INTO public."user" (
        first_name,
        last_name,
        address,
        email,
        date_joined,
        id,
        uid,
        username,
        patronymic_name,
        phone,
        status
    )
VALUES 
    ('B', 'A', NULL, NULL, '2021-03-10T20:23:52.9', '7922cc9e-031f-4b5c-9aac-6ca5308ea886', NULL, 'test_username', 'C', NULL, 'active')
ON CONFLICT DO NOTHING;

INSERT INTO public.compiled_rides (
    history_event_id,
    history_user_id,
    history_action,
    history_timestamp,
    session_id,
    object_id,
    price,
    duration,
    start,
    finish,
    meta_proto,
    hard_proto
)
VALUES
    (1, '7922cc9e-031f-4b5c-9aac-6ca5308ea886', 'stub',  0, 'session_id_xx', '537d15b4-b54b-47fc-a9e1-acd274153c9d'::uuid, 0, 250, 0, 1624269600, NULL, NULL), -- will be skipped because of the table_cursor
    -- minutes standart insurance
    (2, '7922cc9e-031f-4b5c-9aac-6ca5308ea886', 'stub', 0, 'session_id_100', '537d15b4-b54b-47fc-a9e1-acd274153c9d'::uuid, 0, 250, 1624261600, 1624269600,
    'CqgBCAUQ2QEaOgj6EBoL0JIg0L/Rg9GC0LgiEG9sZF9zdGF0ZV9yaWRpbmcyDjMg0LzQuNC9IDM3INGBONkBRQAAAAAaRgiIJxor0KHRgtC+0LjQvNC+0YHRgtGMINCx0YDQvtC90LjRgNC+0LLQsNC90LjRjyIPYWNjZXB0YW5jZV9jb3N0RQAAAAAaGwiCOBoK0JjRgtC+0LPQviIFdG90YWxFAAAAACAAEl8KKgkAAAAA6d1LQBEAAACgkstCQB0AAAAAJQAAAAAoATCah86RBjiah86RBhIqCQAAAADp3UtAEQAAAKCSy0JAHQAAAAAlAAAAACgBMJqHzpEGOJqHzpEGHQAAAAAgASIkCPTpi5IGEhVvbGRfc3RhdGVfcmVzZXJ2YXRpb24YACCo7oodIh8I+emLkgYSEG9sZF9zdGF0ZV9yaWRpbmcYAyCp7oodIiQI0uuLkgYSFW9sZF9zdGF0ZV9yZXNlcnZhdGlvbhgDILLuih0iJAjS64uSBhIVb2xkX3N0YXRlX3Jlc2VydmF0aW9uGAEgs+6KHSog0JfQsNCx0YDQvtC90LjRgNC+0LLQsNGC0YwgW21za10wADj56YuSBkjZAQ==',
    'eJztV99rHFUUPndn0o5bqdutke2W2mmyiyUysHNnZmemWDO7bUqo4B9grev8uNdum+yEmYnmMY0IoQqFlWqpIvoia/Ehpg9dpIkh9ilCmY3QH4KgfbFGsT6o2CLi7G5TqikaUFgfdi58c+4935w5h3Phfjf+W4q7+e2r1Q2Jt76PMJ2xqK7akiIJuZziCLJiSQLVNUvIy0S1Lc3WRSz3ZUSJEk3VsWDbGhZkSh1Bz4mqIDrYziuSbDsqHshIOayZVMYCsfNEMFUHCyK1LEEhmMo5y5FMLGI+fDOcCT9qTIbz4VxYb71nw5nGVOM1/tCof+zwHjDO/4yGwSrGjQfgzpN+8CVz5Fi58kIpKI+S3YD7uQ9jW+56e90Rp+QHZkBKHvGJ96IZlN3KMBzdHC1WHNMLSi6lxPPmHuacxFU2dWMjDwYcfHdrFmDByJ5cHN+bfWPrrcFoOjmYjV/pfyKb8sTB7PDN54rZU88+Umw73u/nmxRY6DhANmimVnymlZq8L7vyysWnO57VfwqUbjAiq1Zo1/sn+D/k14UudKELXbgDw82jaKzQ6TTaAHfh3wTofB2dg28iRTGwsVKuEMsNBiAa69OBsI7xjypwlXkExmAC1RDMIKgjWETPx/fGe7irbBKSLOckIc1ykISDu7npx6LJrnivZfqkZNo2GYukn01KY17ZJr3Nhu4A4+2h5M62qJz+1NiyamxbNfjJr9ES4lZF4zLaZNpBySHUHB8JJmNwAt0/fBUlfNt1A+L5pdFyZTwg/lnE2qbnLKPtf/WU/CNuJEgr5ij5AsH1Nm8FZQoH9ilDqlQUdGW/LMiF3H5Bx0VZ0IckTda0QqGgqtMxdCYGi7E1v1tau3Q9ltz25KnP36l+VjR2Xf790i83vnzKWInBrzE0xUCVgTMM1BiYZR5tJiBMSDZWRE3XJA2LloVzomPKhMr0Y4YNzInyAoOWGJ46miOriiabeSqLeaJpmOp5XcqTnBQ57JCBrxhYYeBHBm4zcJqFsyzMsow37tdZlKwhridxDaX3cLcT6U1hlQ8/abzcmArrfYl7JHzZiZQ+3izx4YWwHs7xkso3jmvX0FCzTekDUavTj4fvRZ/NR+4L4XzjeGvjrN1PLftk30P39Mt2/aAdZzs3paXj4elWnHPhfF9P4AbmSMvJQ/p1FM9wPzXvSsn7Xy9SwNd+OLEjvpO71WKtqSDF8B80CRlu+bu/CcPws+tgIf5cxDrKiDj/B7APN5Y='),
    -- minutes full insurance
    (3, '7922cc9e-031f-4b5c-9aac-6ca5308ea886', 'stub', 0, 'session_id_101', '537d15b4-b54b-47fc-a9e1-acd274153c9d'::uuid, 0, 250, 1624261600, 1624269600,
    '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'),
    -- fix full insurance
    (4, '7922cc9e-031f-4b5c-9aac-6ca5308ea886', 'stub', 0, 'session_id_102', '537d15b4-b54b-47fc-a9e1-acd274153c9d'::uuid, 0, 250, 1624261600, 1624269600,
    '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'),
    -- no insurance (tariff_courier_msk)
    (5, '7922cc9e-031f-4b5c-9aac-6ca5308ea886', 'stub', 0, 'session_id_103', '537d15b4-b54b-47fc-a9e1-acd274153c9d'::uuid, 0, 250, 1624261600, 1624269600,
    'eJzjWs3IwS7wWEDKheM1o5TAhXkXtl3YcWHLhQ0X9gLprUqC+Tkp8cUliSWp8QWJRdmZeelGQkYKF/YAJfcqGBkqXGy8sPXCLoteRlcGIJCy5+iXkuK+MEnhwv6LzRebLuxQEkAYUJSZAtIvbGwMN8AMZsA1fogB0hy/pKW4LswA6t13YfOFfUqsJfkliTlgSQUGoXguLU4QU+Sht4MgkD6gfMXJQRYkonr2zBlbDUaDU5NfT2azWAMihcBqD/x5AFGbEHITTe2qZSC1C0CkrANbo70Co5IKx/GpIK2iSM5OLU4tKkssyczPk2BQ+NW4x05JnuMcWBWG5ySYFQ43AxUocDyeAVKAGXxAFQefgY34MBOXETcm77UDumTjMjwuYVZoOXiAoCpGhQ6gKq1oJyMnhQuLLmy42HBhx8UWhegLcy7sA4b8rgubLmzQUQDG9+6L/QoXdgHjrOFiz4WtQGX7LmzSUTDQNdQ1BMpvuLAJHCF7gCYAI/ViO1AJSPeOCztjDRgswIHhcY0/oJcRAEHo9lE=',
    'eJztV11oHFUUPndnreNW7GabymYD7ZhkQUIHZu7M3sxqSda1hVLBVx+KjHf+7LbZ3TA70eDTJi2aB6WQUI1BpPogpb7EbaNrbGLa+IMhyt0itfhkWhRMH+yLIHny7m4TpY1akBofMhe+uXPPd797LucwnBP5vE1cOHVjfFv0lzc4JrpSqk1TKYPKiufosucSImuKZ8melsLYM2zVSNOOrh6FaIQYmkxJWpN1z6JyWsWabHluyiDEwxbVu7tSuuoZFlZky1DTsm5wgkEVWyaq4xHqGbpCMT6cxVmJvcumamVWrZ2QDrO32FxtmM2wCpvaK7Hz7JPaSYnN1I7XyrVX2TSnzbHKXkmRVVnl9ilWqY3wpQtcYYQrvMIp9d1V9vGzj0GGvSwcBCsbyTwAt57Egy/S/mO5wvNmkMu7jwLuFK+GW9atu4r9jlkKaOCavlty/RdokCsWDsLRh/hiwaF+YBY9z/X95VbRiTrx8ultEmTg0M87kwDlvmTku859ybiv9t3+eVo0s8nd7zycbRq+OvBSX/LrpaXeZPa5H/clvxh+JsMNMP/fAyQn665B07WBbPL1Xz97epN8uZe3vAWt+5NQPvckn0lPbLpXW7AFW7AFW3AbAIfq/+T/DOvwbwQ2/x6bB+O8oujeVcgVXKsYmHk6ZA70D5ZMrGDcDXzcXUEJdzHuZTm5dsgRGIAhdAbBFIIqgkvo8Ug8EhadGMQamAiLEINDDYztaRaeowuZlrVJ29pEKi+jRSSuFZaX0XZqB6bjenSwPyiH0BiKBdTPeZ5pFwf9nOub+dKxsyhsU9+5jNpLdrEYuH7JzOcKg4FbMktHirw8LdC8+z2Ca03eCpIsolDH1T2saDomVlozdNdWFSdtWEpaSeujIZgMwaXQBoctbrR4LRRr65RPfdT5bTbzyFJRCLcuP5VZCcFvITQiwJgAkwKcEaAi7K47IA8Rm2gK1TBJuUSz0lgnnuLQHmtGCAd0KDcvoEVB6sEOVl2iG5TaOvV0ngg9lssbBVsjtmGkmAA/CLAiwE0BVgWYCMPZMFTCgj9YqoZR7H0k3h+9Hk3sF2+gRJS9zT7kITvPwznL39MdLX9U9QPUr1f/OIYlHuUqm5WwKvEYT7MZ4zV0oB6aRJ94MpHYzsYk9ilPFJ4HHdE/tQU5p75/p6atC5A1gSs7mgLt4mp7IsImGrl0js113BcUA9rfMEqQuIIiXeKX9b4rtnG/EQdpdfhCb2SP+E2DdcfxcUFaOM4Jknh9ok6484KccfGnhsTNN/9K4ur4bC/35IP3/sYTQTpxcf4fWUga5ayjOwyCsZJSUjzTsGL0/A56HYby')
ON CONFLICT DO NOTHING;

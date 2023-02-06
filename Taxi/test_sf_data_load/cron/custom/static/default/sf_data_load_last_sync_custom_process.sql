CREATE TABLE IF NOT EXISTS sf_data_load.last_sync_custom_process
(
    process_name varchar(128)
        primary key,
    last_sync  timestamp
);

INSERT INTO sf_data_load.last_sync_custom_process (process_name, last_sync)
VALUES
(
    'corp_api_sync_corp_clients',
    '2022-05-31 11:51:03.241760'
),
(
    'corp_yt_load_zapravki',
    '2022-06-28 01:05:00.00000'
)

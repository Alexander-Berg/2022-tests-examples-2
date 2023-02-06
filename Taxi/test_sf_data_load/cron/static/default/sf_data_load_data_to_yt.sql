DELETE FROM sf_data_load.load_to_yt;

INSERT INTO sf_data_load.load_to_yt
(
    sf_id,
    sf_org,
    sf_object,
    value,
    time_operation
)
VALUES
(
    'failed',
    'b2b',
    'Task',
    '{"OwnerId": "a"}',
    '2022-06-17 09:50:20.000000'
),
(
    '1',
    'b2b',
    'Task',
    '{"WhoId": "b"}',
    '2022-06-17 09:50:20.000000'
),
(
    '2',
    'b2b',
    'Task',
    '{"Type": "case"}',
    '2022-06-17 09:50:20.000000'
)

INSERT INTO distlocks.namespaces(name)
VALUES ('namespace1');

INSERT INTO distlocks.locks AS t (
    namespace_name,
    name,
    owner,
    expiration_time,
    fencing_token
) VALUES (
    'namespace1',
    'lock2',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '1 HOUR',
    nextval('distlocks.fencing_token_seq')
),
(
    'namespace1',
    'lock3',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '1 HOUR',
    nextval('distlocks.fencing_token_seq')
);

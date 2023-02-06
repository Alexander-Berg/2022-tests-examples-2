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
    'lock1',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '60 MINUTES',
    nextval('distlocks.fencing_token_seq')
),
(
    'namespace1',
    'lock2',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '30 MINUTES',
    nextval('distlocks.fencing_token_seq')
),
(
    'namespace1',
    'lock3',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' - INTERVAL '1 MINUTES',
    nextval('distlocks.fencing_token_seq')
),
(
    'namespace1',
    'lock4',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '5 MINUTES',
    nextval('distlocks.fencing_token_seq')
);

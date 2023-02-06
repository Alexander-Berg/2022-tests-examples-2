INSERT INTO distlocks.namespaces(name)
VALUES ('namespace1'), ('namespace2'), ('namespace3');

INSERT INTO distlocks.locks AS t (
    namespace_name,
    name,
    owner,
    expiration_time,
    fencing_token
) VALUES (
    'namespace2',
    'lock1',
    'owner1',
    CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '1 HOUR',
    nextval('distlocks.fencing_token_seq')
);

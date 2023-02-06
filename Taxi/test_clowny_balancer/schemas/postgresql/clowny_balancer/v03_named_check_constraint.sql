ALTER TABLE balancers.namespaces
    DROP CONSTRAINT namespaces_check,
    ADD CONSTRAINT shared_not_external_check CHECK ( NOT (is_shared AND is_external) )
;

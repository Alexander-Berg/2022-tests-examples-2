--- Health checks result table, may be written by any machine in cluster

CREATE TYPE api_proxy.health_status_overall AS ENUM (
    'ok',
    'warn',
    'crit'
);

CREATE TYPE api_proxy.health_status_method AS ENUM (
    'ok',
    'resource_not_available',
    'method_not_allowed',
    'check_not_supported',
    'invalid_implementation'
    );

CREATE TYPE api_proxy.health_status_tvm AS ENUM (
    'ok',
    'denied',
    'check_not_supported',
    'invalid_implementation'
    );


CREATE TABLE api_proxy.resource_health
(
    id              TEXT            NOT NULL,
    revision        INTEGER         NOT NULL,
    cluster_tvm     TEXT            NOT NULL,

    updated         TIMESTAMPTZ     NOT NULL    DEFAULT NOW(),

    /* result */
    hp_overall      api_proxy.health_status_overall NOT NULL,
    hp_method       api_proxy.health_status_method  NOT NULL,
    hp_tvm          api_proxy.health_status_tvm     NOT NULL,
    message         TEXT            NULL,

    /* diagnostic */
    test_url        TEXT            NOT NULL,
    link            TEXT            NOT NULL,
    span_id         TEXT            NOT NULL,

    PRIMARY KEY (id, revision, cluster_tvm),
    CONSTRAINT resource_health_id_rev_fkey FOREIGN KEY (id, revision)
        REFERENCES api_proxy.resources(id, revision)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX resource_hp_by_updated_index ON api_proxy.resource_health(updated);

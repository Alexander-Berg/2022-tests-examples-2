--- Define resource health check types

CREATE TYPE api_proxy.resource_hp_check_t_v1 AS (
    id              TEXT,
    revision        INTEGER,
    cluster_tvm     TEXT,

    updated         TIMESTAMPTZ,

    /* result */
    hp_overall      api_proxy.health_status_overall,
    hp_method       api_proxy.health_status_method,
    hp_tvm          api_proxy.health_status_tvm,
    message         TEXT,

    /* diagnostic */
    test_url        TEXT,
    link            TEXT,
    span_id         TEXT
);

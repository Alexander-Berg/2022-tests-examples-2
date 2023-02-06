CREATE SCHEMA united_dispatch;

CREATE TABLE IF NOT EXISTS united_dispatch.segments (
    id TEXT NOT NULL,
    waybill_building_version BIGINT NOT NULL,
    is_waybill_send BOOL NOT NULL DEFAULT FALSE,
    dispatch_revision BIGINT NOT NULL,
    taxi_classes TEXT[] NOT NULL,
    taxi_requirements JSONB NOT NULL DEFAULT '{}'::JSONB,
    special_requirements JSONB NOT NULL DEFAULT '{}'::JSONB,
    points JSONB[] NOT NULL DEFAULT '{}'::JSONB[], -- sorted by visit_order
    crutches JSONB,
    status TEXT NOT NULL,

    created_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (id)
);


CREATE TYPE united_dispatch.lookup_v1 AS(
   generation integer,
   version integer,
   wave integer
);

CREATE TYPE united_dispatch.lookup_flow AS ENUM (
    'taxi-dispatch',
    'united-dispatch'
);

CREATE TABLE IF NOT EXISTS united_dispatch.waybills (
    id TEXT NOT NULL,
    proposition_status TEXT NOT NULL DEFAULT 'new'::TEXT,
    waybill JSONB NOT NULL,
    candidate JSONB,
    created_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    external_resolution TEXT,
    revision BIGINT NOT NULL DEFAULT 1,
    lookup united_dispatch.lookup_v1 NOT NULL DEFAULT row(1, 1, 1)::united_dispatch.lookup_v1,
    proposition_builder_shard TEXT NOT NULL DEFAULT 'default'::TEXT,
    lookup_flow united_dispatch.lookup_flow NOT NULL DEFAULT 'taxi-dispatch'::united_dispatch.lookup_flow,
    previous_id TEXT,
    update_proposition_id TEXT,

    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS united_dispatch.rejected_candidates (
    delivery_id TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    rejections BIGINT NOT NULL DEFAULT 1,
    created_ts TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT now(),

    PRIMARY KEY (delivery_id, candidate_id)
);

CREATE TABLE IF NOT EXISTS united_dispatch.segment_executors (
    planner_type TEXT NOT NULL,
    segment_id TEXT NOT NULL,
    execution_order INT NOT NULL,

    planner_shard TEXT NOT NULL,
    status TEXT NOT NULL,

    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (planner_type, segment_id, execution_order)
);

ALTER TABLE united_dispatch.segment_executors
    ADD FOREIGN KEY (segment_id) REFERENCES united_dispatch.segments(id) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS united_dispatch.frozen_candidates (
    candidate_id TEXT NOT NULL,
    waybill_id TEXT NOT NULL,
    expiration_ts TIMESTAMPTZ NOT NULL,
    created_ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (candidate_id)
);

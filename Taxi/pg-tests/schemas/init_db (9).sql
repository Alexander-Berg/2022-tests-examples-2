CREATE SCHEMA IF NOT EXISTS eats_proactive_support;

-- orders
CREATE TABLE IF NOT EXISTS eats_proactive_support.orders
(
    order_nr TEXT NOT NULL,
    status TEXT NOT NULL,
    promised_at TIMESTAMPTZ NOT NULL,
    order_type TEXT NOT NULL,
    delivery_type TEXT NOT NULL,
    shipping_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(order_nr)
);

-- order_cancellations
CREATE TABLE IF NOT EXISTS eats_proactive_support.order_cancellations
(
    order_nr TEXT NOT NULL,
    cancellation_code TEXT NOT NULL,
    cancellation_caller TEXT NOT NULL,
    cancelled_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(order_nr)
);

-- problems
CREATE TABLE eats_proactive_support.problems
(
    id BIGSERIAL NOT NULL,
    order_nr TEXT NOT NULL,
    type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(id)
);

-- actions
CREATE TABLE eats_proactive_support.actions
(
    id BIGSERIAL NOT NULL,
    external_id TEXT,
    problem_id BIGINT NOT NULL,
    order_nr TEXT NOT NULL,
    type TEXT NOT NULL,
    payload JSONB,
    state TEXT NOT NULL,
    skipped_at TIMESTAMPTZ,
    skip_reason TEXT,
    performed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(id)
);

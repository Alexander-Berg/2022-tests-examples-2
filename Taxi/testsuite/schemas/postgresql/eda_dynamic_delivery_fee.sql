DROP SCHEMA IF EXISTS eda_dynamic_delivery_fee CASCADE;
CREATE SCHEMA eda_dynamic_delivery_fee;

CREATE TABLE eda_dynamic_delivery_fee.delivery_data
(
    brand_id           TEXT                     NOT NULL,
    region_id          TEXT                     NOT NULL,
    zone_type          TEXT                     NOT NULL,
    commission         DECIMAL(18, 4),
    fixed_commission   DECIMAL(18, 4),
    mean_check         DECIMAL(18, 4)           NOT NULL,
    rpo_commission     DECIMAL(18, 4)           NOT NULL,
    updated_at         TIMESTAMPTZ              NOT NULL DEFAULT NOW(),
    PRIMARY KEY(region_id, brand_id, zone_type)
);

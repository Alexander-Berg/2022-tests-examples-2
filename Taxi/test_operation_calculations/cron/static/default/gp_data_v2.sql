CREATE SCHEMA IF NOT EXISTS "taxi_cdm_operation_calculation";
CREATE TABLE IF NOT EXISTS taxi_cdm_operation_calculation.nmfg_pre_calculation
(
    count_orders                   integer,
    do_x_get_y_subs_fact           double precision,
    geo_subs_fact                  double precision,
    has_sticker                    boolean,
    has_lightbox                   boolean,
    is_shift_commission_equal_zero boolean,
    local_order_due_date           date,
    nmfg_subs_fact                 double precision,
    subs_fact                      double precision,
    subsidy_geo                    double precision,
    tariff_category                text,
    tariff_zone                    text,
    true_order_cost                double precision,
    unique_driver_id               text,
    tags                           character varying []
);

CREATE OR REPLACE FUNCTION taxi_cdm_operation_calculation.array_intersect(in_a VARCHAR[], in_b VARCHAR[])
RETURNS VARCHAR[] as $BODY$
DECLARE
    v_res varchar[];
BEGIN
    IF in_a IS NULL THEN
        RETURN in_b;
    ELSEIF in_b IS NULL THEN
        RETURN in_a;
    END IF;
    SELECT array_agg(intersected.elements) INTO v_res
    FROM (
        SELECT unnest(in_a) as elements
        INTERSECT
        SELECT unnest(in_b)
    ) AS intersected;
    RETURN v_res;
END;
$BODY$ LANGUAGE plpgsql;

DROP AGGREGATE IF EXISTS taxi_cdm_operation_calculation.array_intersect_agg(VARCHAR[]);
CREATE AGGREGATE taxi_cdm_operation_calculation.array_intersect_agg(VARCHAR[]) (
    sfunc = taxi_cdm_operation_calculation.array_intersect,
    stype = VARCHAR[]
);

INSERT INTO taxi_cdm_operation_calculation.nmfg_pre_calculation (count_orders,
                                                                 do_x_get_y_subs_fact,
                                                                 geo_subs_fact,
                                                                 has_sticker,
                                                                 has_lightbox,
                                                                 is_shift_commission_equal_zero,
                                                                 local_order_due_date,
                                                                 nmfg_subs_fact, subs_fact,
                                                                 subsidy_geo,
                                                                 tariff_category,
                                                                 tariff_zone,
                                                                 true_order_cost,
                                                                 unique_driver_id,
                                                                 tags)
VALUES (4, 0, 0, false, true, true, '2021-10-06', 0.856, 0.856, 0, 'econom', 'moscow', 32900,
        '5a33c19ce696290a9554faca','{b}'),
       (1, 0, 0, false, true, true, '2021-10-08', 0.856, 0.856, 0, 'econom', 'moscow', 79,
        '5a33c19ce696290a9554faca','{b}'),
       (10, 0, 0, true, true, true, '2021-10-01', 0, 0, 0, 'econom', 'moscow', 2350,
        '5a727d578ffdaf4b24592893','{a,c}'),
       (10, 0, 0, true, true, true, '2021-10-01', 0, 0, 0, 'econom', 'moscow', 2350,
        '5a727d578ffdaf4b2459289c','{}'),
       (2, 10, 0, false, true, true, '2021-10-02', 0, 0, 0, 'econom', 'moscow', 143,
        '5d919badc081365f0365380a','{}');


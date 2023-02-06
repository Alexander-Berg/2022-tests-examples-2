CREATE SCHEMA IF NOT EXISTS snb_eda;

CREATE TABLE snb_eda.rad_quality (
    brand_id bigint,
    place_id bigint,
    name character varying,
    address character varying,
    rating numeric,
    orders bigint,
    avg_check numeric,
    cancel_rating numeric(3,2),
    pict_share numeric(3,2),
    plus_flg boolean,
    dish_as_gift_flg boolean,
    discount_flg boolean,
    second_for_free_flg boolean,
    pickup_flg boolean,
    mercury_flg boolean
);

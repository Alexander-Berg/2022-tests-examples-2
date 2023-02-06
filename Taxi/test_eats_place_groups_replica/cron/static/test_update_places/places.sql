INSERT INTO place_groups(
    place_group_id,
    brand_id,
    parser_name,
    stock_reset_limit,
    dev_filter
)
VALUES
(
    'place_group_id1',
    'brand_id',
    'parser_name',
    1,
    '{"elem": 2}'::json
)
;

INSERT INTO places(
    place_id,
    place_group_id,
    brand_id,
    external_id
)
VALUES
(
    'place2',
    'place_group_id1',
    'brand_id',
    'external_place_id1'
)
;

CREATE TABLE IF NOT EXISTS public.drive_areas (
    area_id text NOT NULL,
    area_coords text NOT NULL,
    area_tags text,
    area_title text,
    area_index integer DEFAULT 0,
    area_type text,
    area_tooltip text,
    revision bigint NOT NULL,
    area_details json
);

INSERT INTO public.drive_areas (
    area_id,
    area_coords,
    area_tags,
    area_title,
    area_index,
    area_type,
    area_tooltip,
    revision,
    area_details
)
VALUES
(
    'slowdown_vko',
    '37.31652278 55.61690594 37.24384861 55.62337514 37.21526888 55.58338759 37.3001915 55.57020353 37.33693687 55.59009356 37.31652278 55.61690594 ',
    'test_tag_1, allow_drop_car, capacity_10',
    'parking_1',
    0,
    'cluster',
    'some tooltip',
    429,
    '{}'
),
(
    'test_123',
    '37.31 55.61 37.24 55.62 37.21 55.58 37.31 55.61 ', -- mind the trailing space
    'test_tag_2, allow_drop_car, test_tag_3',
    'parking_2',
    NULL, -- index
    'cluster', -- type
    NULL, -- tooptip
    1337, -- rev
    '{"kek": 1337}'  -- details
),
(
    'test_12345',
    '37.31 55.61 37.24 55.62 37.21 55.58 37.31 55.61 ', -- mind the trailing space
    'test_tag_2, allow_drop_car, capacity_bad',
    'parking_2',
    NULL, -- index
    'cluster', -- type
    NULL, -- tooptip
    1337, -- rev
    '{"kek": 1337}'  -- details
);

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
    'test_tag_1',
    'slowdown_vko',
    0,
    'ordinary',
    'some tooltip',
    429,
    '{"ololo": 123, "kek": 1337}'
),
(
    'test_other_polygon',
    '37.31 55.56 37.36 55.56 37.36 55.59 37.31 55.56 ',
    'test_tag_1',
    NULL,
    0,
    'ordinary',
    'some tooltip',
    429,
    '{"ololo": 123, "kek": 1337}'
),
(
    'test_123',
    '37.31 55.61 37.24 55.62 37.21 55.58 37.31 55.61 ', -- mind the trailing space
    'test_tag_2, test_tag_3',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    1337, -- rev
    NULL  -- details
),
(
    'invalid_two_points',
    '37.31 55.61 37.24 55.62 37.31 55.61 ',
    'test_tag_2, test_tag_3',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    1337, -- rev
    NULL  -- details
),
(
    'invalid_odd_tokens',
    '37.31 55.61 37.24 55.62 37.31 55.61 12.34 ',
    'test_tag_2, test_tag_3',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    1337, -- rev
    NULL  -- details
),
(
    'test_123',
    '37.31 55.61 37.24 55.62 37.21 55.58 37.31 55.61 ', -- mind the trailing space
    'no_matching_tags',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    1337, -- rev
    NULL  -- details
);

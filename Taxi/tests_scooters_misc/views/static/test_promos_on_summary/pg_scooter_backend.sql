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
    'spb_parking',
    '30.40764624 59.94553449 30.40457149 59.94593481 30.40029512 59.94551702 30.39163155 59.94118987 30.38208213 59.92995588 30.4091481 59.92938803 30.40764624 59.94553449 ', -- mind the trailing space
    'allow_drop_car, test_tag_1',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    713, -- rev
    NULL  -- details
),
(
    'scooter_parking_1001',
    '37.53638103 55.75515661 37.53930744 55.75827584 37.54395607 55.75908509 37.5457656 55.75610309 37.5435784 55.75299754 37.53923094 55.75185173 37.53638103 55.75515661 ', -- mind the trailing space
    'allow_drop_car, test_tag_1',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    731, -- rev
    NULL  -- details
),
(
    'parking_mamontov_1',
    '37.58857393 55.7347731 37.58957137 55.73403397 37.58753496 55.73304279 37.58645457 55.73380704 37.58857393 55.7347731 ', -- mind the trailing space
    'allow_drop_car, test_tag_1',
    NULL, -- title
    NULL, -- index
    NULL, -- type
    NULL, -- tooptip
    379, -- rev
    NULL  -- details
);

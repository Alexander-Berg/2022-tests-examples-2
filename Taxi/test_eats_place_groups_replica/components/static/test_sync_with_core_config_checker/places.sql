INSERT INTO place_groups(place_group_id, brand_id)
VALUES
('place_group_id1', 'brand_id1'),
('place_group_id2', 'brand_id2'),
('place_group_id3', 'brand_id3')
;

INSERT INTO places (place_id, place_group_id, brand_id, external_id)
VALUES
    ('place_id1', 'place_group_id1', 'brand_id1', 'external_place_id1'),
    ('place_id2', 'place_group_id2', 'brand_id2', 'external_place_id2'),
    ('place_id3', 'place_group_id3', 'brand_id3', 'external_place_id3')
;

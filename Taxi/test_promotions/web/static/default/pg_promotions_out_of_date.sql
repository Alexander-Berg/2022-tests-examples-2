INSERT INTO promotions.showcases (id, name, name_tsv, collection_blocks, screens, status, starts_at, ends_at)
VALUES (
     'published_upcoming_showcase_id',
     'published_upcoming_showcase_name',
     to_tsvector('published_upcoming_showcase_name'),
     ('{"blocks": [{"title": "key", "personalized_title": "personalized_key", "is_tanker_key": true, "collection_id": "collection_id_1"}]}')::jsonb,
     '{ANY_SCREEN}'::TEXT[],
     'published',
     '2029-05-22T16:51:09+0000',
     '2029-07-22T16:51:09+0000'
),(
     'published_expired_showcase_id',
     'published_expired_showcase_name',
     to_tsvector('published_expired_showcase_name'),
     ('{"blocks": [{"title": "key", "personalized_title": "personalized_key", "is_tanker_key": true, "collection_id": "collection_id_1"}]}')::jsonb,
     '{ANY_SCREEN}'::TEXT[],
     'published',
     '2019-05-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000'
)
;

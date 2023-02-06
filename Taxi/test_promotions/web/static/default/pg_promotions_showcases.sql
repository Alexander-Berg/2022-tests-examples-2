INSERT INTO promotions.showcases (id, name, name_tsv, collection_blocks, screens, status, starts_at, ends_at)
VALUES (
     'default_showcase_id',
     'default_showcase_name',
     to_tsvector('default_showcase_name'),
     ('{"blocks": [{"title": "key", "personalized_title": "personalized_key", "is_tanker_key": true, "collection_id": "default_collection_id"}]}')::jsonb,
     '{ANY_SCREEN}'::TEXT[],
     'created',
     NULL,
     NULL
), (
     'showcase_id_1',
     'showcase_name_1',
     to_tsvector('showcase_name_1'),
     ('{"blocks": [{"title": "key", "personalized_title": "personalized_key", "is_tanker_key": true, "collection_id": "default_collection_id"}]}')::jsonb,
     '{ANY_SCREEN}'::TEXT[],
     'created',
     NULL,
     NULL
), (
     'published_showcase_id',
     'published_showcase_name',
     to_tsvector('published_showcase_name'),
     ('{"blocks": [{"title": "key", "personalized_title": "personalized_key", "is_tanker_key": true, "collection_id": "collection_id_1"}]}')::jsonb,
     '{ANY_SCREEN}'::TEXT[],
     'published',
     '2021-05-22T16:51:09+0000',
     '2029-07-22T16:51:09+0000'
), (
     'showcase_with_untitled_collection_id',
     'showcase_with_untitled_collection_name',
     to_tsvector('showcase_with_untitled_collection_name'),
     ('{"blocks": [{"collection_id": "default_collection_id"}]}')::jsonb,
     '{ANY_SCREEN}'::TEXT[],
     'created',
     NULL,
     NULL
);

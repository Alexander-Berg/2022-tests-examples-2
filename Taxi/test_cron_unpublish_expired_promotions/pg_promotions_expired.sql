INSERT INTO promotions.promotions (
    id,
    revision,
    revision_history,
    name,
    name_tsv,
    promotion_type,
    created_at,
    updated_at,
    published_at,
    status,
    meta_tags,
    zones,
    screens,
    priority,
    starts_at,
    ends_at,
    experiment,
    has_yql_data,
    yql_data,
    pages,
    extra_fields) VALUES
(
     'id3_expired',
     null,
     null,
     'banner 3',
     to_tsvector('banner 3'),
     'card',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY['tag5', 'tag6']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     'promotions_test_publish',
     false,
     null,
     ('{"pages": []}')::jsonb,
     null
),
(
     'eda_expired',
     'revision',
     ('{
         "data": [
             {
                 "revision": "some_revision",
                 "created_at": "2019-07-22T16:51:09+0000"
             }
         ]
     }')::jsonb,
     'eda_banner_published',
     to_tsvector('eda_banner_published'),
     'eda_banner',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     ARRAY[]::TEXT[],
     ARRAY[]::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     'eda_exp',
     false,
     null,
     ('{"pages": []}')::jsonb,
     null
),
(
     'grocery_expired',
     'revision',
     ('{
         "data": [
             {
                 "revision": "some_revision",
                 "created_at": "2019-07-22T16:51:09+0000"
             }
         ]
     }')::jsonb,
     'grocery_informer_published',
     to_tsvector('grocery_informer_published'),
     'grocery_informer',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'published',
     null,
     ARRAY[]::TEXT[],
     ARRAY[]::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     'grocery_exp',
     false,
     null,
     ('{"pages": []}')::jsonb,
     null
);

INSERT INTO promotions.showcases (id, name, name_tsv, collection_blocks, status, starts_at, ends_at)
VALUES (
     'expired_showcase_id',
     'expired_showcase_name',
     to_tsvector('expired_showcase_name'),
     ('{"blocks": []}')::jsonb,
     'published',
     '2019-05-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000'
);

INSERT INTO promotions.promo_on_map
VALUES (
     'expired_promo_on_map_id',
     'expired_promo_on_map_name',
     to_tsvector('expired_promo_on_map_name'),
     1,
     'image_tag2',
     ('{"deeplink": "deeplink", "promotion_id": "promotion_id"}')::jsonb,
     ('{"id": "bubble_id", "hide_after_tap": true, "max_per_session": 1, "max_per_user": 10, "components": [{"type":"text", "value":"text on bubble", "font_style": "bold", "has_tanker_key": true}]}')::jsonb,
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:57:09+0000',
     '2019-07-22T16:52:09+0000',
     'published',
     '2019-07-23T00:00:00+0000',
     '2019-07-24T00:00:00+0000',
     'experiment_name',
     1000,
     TRUE
);

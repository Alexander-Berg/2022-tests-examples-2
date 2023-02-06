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
     'eda_banner_id',
     null,
     null,
     'Eda Banner',
     to_tsvector('Eda Banner'),
     'eda_banner',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'created',
     ARRAY['tag1', 'tag2']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     3,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp1',
     false,
     null,
     ('{"pages": [
        {
           "images": [
              {
                "url": "https://eda.yandex/image1.jpg",
                "theme": "light",
                "platform": "web"
              },
              {
                "url": "https://eda.yandex/image2.jpg",
                "theme": "dark",
                "platform": "web"
              },
              {
                "url": "https://eda.yandex/image3.jpg",
                "theme": "light",
                "platform": "mobile"
              },
              {
                "url": "https://eda.yandex/image4.jpg",
                "theme": "dark",
                "platform": "mobile"
              }
            ]
        }
     ]}')::jsonb,
     ('{
        "description": "Test banner",
        "banner_type": "info",
        "url": "https://eda.yandex/image1.jpg",
        "app_url": "https://eda.yandex/image1.jpg",
        "feeds_admin_id": "100"
     }')::jsonb
),

(
     'story_id',
     null,
     null,
    'story 1',
     to_tsvector('story 1'),
     'story',
     '2019-07-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     null,
     'created',
     ARRAY['tag77', 'tag88']::TEXT[],
     ARRAY['moscow', 'abakan']::TEXT[],
     ARRAY['main']::TEXT[],
     1,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'exp_fs',
     false,
     null,
     ('{"pages": [
            {
                "title": {"content": "title3", "color": "ff00ee", "type": "large"},
                "alt_title": {"content": "alt_title3", "color": "aaeedd"},
                "text": {"content": "text3", "color": "eaeaea"},
                "is_foldable": true,
                "widgets": {
                    "close_button": {"color": "fefefe"},
                    "menu_button": {"color": "fafafa"},
                    "pager": {"color_on": "affafe", "color_off": "ff0011"},
                    "action_buttons": [
                        {"color": "feafea", "text": "action button", "text_color": "ffffff", "deeplink": "deeplink"},
                        {"color": "feafea", "text": "action button", "text_color": "ffffff",
                         "action": {"payload": {"content": "", "need_authorization": false}, "type": "screenshare"}}
                    ]
                },
                "layout": {"id": "layout_id"}
            }
       ]}'
     )::jsonb,
     ('{
         "mark_read_after_tap": true,
         "meta_type": "promo_stories",
         "is_tapable": true,
         "min_pages_amount": 4,
         "preview": {
             "title": {"content": "Title!", "color": "ffffff"}
         },
         "feeds_admin_id": "100"
     }')::jsonb
);

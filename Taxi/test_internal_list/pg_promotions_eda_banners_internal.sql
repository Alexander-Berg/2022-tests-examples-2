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
     'eda_banner1',
     'published_ok',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "published_ok"
             }
         ]
     }')::jsonb,
     'Eda Banner',
     to_tsvector('Eda Banner'),
     'eda_banner',
     '2019-07-22T16:51:09+0000',
     '2019-07-23T16:51:09+0000',
     '2019-07-24T16:51:09+0000',
     'published',
     NULL,
     ARRAY['all']::TEXT[],
     ARRAY['main']::TEXT[],
     4,
     '2019-05-22T16:51:09+0000',
     '2022-07-22T16:51:09+0000',
     'eda_experiment',
     false,
     NULL,
     ('{"pages": [
        {
          "images": [
            {
              "url": "https://eda.yandex/light.png",
              "theme": "light",
              "platform": "web"
            },
            {
              "url": "https://eda.yandex/dark.png",
              "theme": "dark",
              "platform": "mobile"
            }
          ],
          "shortcuts": [
            {
              "url": "https://eda.yandex/shortcut_light.png",
              "theme": "light",
              "platform": "web"
            },
            {
              "url": "https://eda.yandex/shortcut_dark.png",
              "theme": "dark",
              "platform": "mobile"
            }
          ]
        }
       ]}'
     )::jsonb,
     ('{
         "banner_id": 10101,
         "banner_type": "info",
         "collection_slug": "https://mcdonalds.ru/banner.png",
         "region_id": 123,
         "description": "Some info banner",
         "url": "https://ya.ru",
         "app_url": "https://ya.ru/mobile",
         "geojson": [[37.58079528808594, 55.91458189198758], [37.49290466308594, 55.90034110284034], [37.3919677734375, 55.870688097921345]]
     }')::jsonb
),
(
     'eda_banner2',
     'published_ok',
     ('{
         "data": [
             {
                 "created_at": "2019-07-22T16:51:09+0000",
                 "revision": "published_ok"
             }
         ]
     }')::jsonb,
     'Eda Banner2',
     to_tsvector('Eda Banner2'),
     'eda_banner',
     '2018-07-22T16:51:09+0000',
     '2018-07-23T16:51:09+0000',
     '2018-07-24T16:51:09+0000',
     'published',
     NULL,
     ARRAY['all']::TEXT[],
     ARRAY['main']::TEXT[],
     4,
     '2019-05-22T16:51:09+0000',
     '2019-07-22T16:51:09+0000',
     'eda_experiment',
     false,
     NULL,
     ('{"pages": [
        {
          "images": [
            {
              "url": "https://eda.yandex/light.png",
              "theme": "light",
              "platform": "web"
            },
            {
              "url": "https://eda.yandex/dark.png",
              "theme": "dark",
              "platform": "mobile"
            }
          ],
          "shortcuts": [
            {
              "url": "https://eda.yandex/shortcut_light.png",
              "theme": "light",
              "platform": "web"
            },
            {
              "url": "https://eda.yandex/shortcut_dark.png",
              "theme": "dark",
              "platform": "mobile"
            }
          ]
        }
       ]}'
     )::jsonb,
     ('{
         "banner_id": 10102,
         "banner_type": "info",
         "collection_slug": "https://mcdonalds.ru/banner.png",
         "region_id": 123,
         "description": "Some info banner",
         "url": "https://ya.ru",
         "app_url": "https://ya.ru/mobile",
         "geojson": [[37.58079528808594, 55.91458189198758], [37.49290466308594, 55.90034110284034], [37.3919677734375, 55.870688097921345]]
     }')::jsonb
);

insert into eats_places_description.zen_articles
    (brand_id, place_id, title, url, priority, published_at, description, author_avatar_url, created_at)
values
    (333, null, 'title_1', 'url', 0, now(), 'descr', 'a_a_url', now()),
    (333, null, 'title_2', 'url', 1, now(), 'descr', 'a_a_url', now()),
    (444, null, 'title_3', 'url', 0, now() - interval '1 hour',
     'descr', 'a_a_url', now()),
    (444, null, 'title_4', 'url', 0, now(), 'descr', 'a_a_url', now()),
    (555, null, 'title_5', 'url', 0, now(), 'descr', 'a_a_url',
     now() - interval '1 hour'),
    (555, null, 'title_6', 'url', 0, now(), 'descr', 'a_a_url', now()),
    (666, null, 'title_7', 'url', 0, now(), 'descr', 'a_a_url', now()),
    (666, null, 'title_8', 'url', 0, now(), 'descr', 'a_a_url', now());

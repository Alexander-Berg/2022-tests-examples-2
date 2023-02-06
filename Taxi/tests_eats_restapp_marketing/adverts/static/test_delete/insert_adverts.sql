INSERT INTO eats_restapp_marketing.advert (id, updated_at, place_id, averagecpc, campaign_id, group_id, ad_id,
                                           content_id, banner_id, is_active, error, passport_id, weekly_spend_limit,
                                           status, reason_status, started_at, suspended_at, campaign_type,
                                           strategy_type, created_at)
VALUES (1114, '2021-07-29 07:18:02.583061 +00:00', 329210, 5000000, 59633949, 4482853598, 10353448896, 1356710,
        72057604391376832, true, null, 111111, null, null, null, '2021-07-29 07:18:02.618373 +00:00', null, 'CPM',
        'average_cpc', '2021-05-23 08:35:16.788372 +00:00'),
       (3913, '2021-07-30 07:08:14.175893 +00:00', 403354, 15000000, 62034246, 4570457393, 10909254740, 2183565,
        72057604947182676, true, null, 111112, null, null, null, '2021-07-30 07:08:14.200301 +00:00', null, 'CPM',
        'average_cpc', '2021-07-10 13:48:31.781907 +00:00');

insert into eats_restapp_marketing.advert_for_create (id, created_at, creation_started, token_id, advert_id, averagecpc)
values (2235, '2021-09-03 07:34:12.222473 +00:00', true, 26304, 1114, 5000000),
       (2455, '2021-09-04 18:05:46.484564 +00:00', true, 65724, 3913, 15000000);



INSERT INTO eats_restapp_marketing.keywords (id, keyword_id, advert_id)
VALUES (15522, 33412370545, 1114),
       (15523, 33412370546, 1114),
       (15524, 33412370547, 1114),
       (15525, 33412370548, 1114),
       (15557, 33415818574, 1114),
       (15558, 33415818575, 3913),
       (15559, 33415818576, 3913),
       (15560, 33415818577, 3913);

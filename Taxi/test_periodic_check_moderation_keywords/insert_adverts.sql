INSERT INTO eats_restapp_marketing.advert (id, place_id, averagecpc, campaign_id, group_id, ad_id,
                                           content_id, banner_id, is_active, error, passport_id, weekly_spend_limit,
                                           status, reason_status, started_at, suspended_at, campaign_type,
                                           strategy_type)
VALUES (1114, 329210, 5000000, 59633949, 4482853598, 10353448896, 1356710,
        72057604391376832, true, null, 111111, null, null, null, '2021-07-29 07:18:02.618373 +00:00', null, 'CPM',
        'average_cpc'),
       (3913, 403354, 15000000, 59633949, 4570457393, 10909254740, 2183565,
        72057604947182676, true, null, 111112, null, null, null, '2021-07-30 07:08:14.200301 +00:00', null, 'CPM',
        'average_cpc'),
       (1111, 333330, 5000000, 59633948, 4482853598, 10353448896, 1356710,
        72057604391376832, true, null, 1229582676, null, null, null, '2021-07-29 07:18:02.618373 +00:00', null, 'CPM',
        'average_cpc'),
       (2222, 444444, 15000000, 59633948, 4570457393, 10909254740, 2183565,
        72057604947182676, true, null, 1229582676, null, null, null, '2021-07-30 07:08:14.200301 +00:00', null, 'CPM',
        'average_cpc');


INSERT INTO eats_restapp_marketing.keywords (
	keyword_id, keyword,	advert_id,	status,		state,			place_id,	inner_campaign_id)
VALUES
	(1,			NULL,		1114,		'draft',	'on',			NULL,		NULL),
	(2, 		NULL, 		3913, 		'rejected', 'on',			NULL, 		NULL),
	(3, 		NULL, 		1111, 		'unknown',	'off',			NULL, 		NULL),
	(4, 		NULL, 		2222, 		'draft',	'suspended',	NULL, 		NULL),
	(5, 		NULL, 		2222, 		'unknown',	'on',			NULL, 		NULL),
	(6, 		NULL, 		2222, 		'rejected', 'off',			NULL, 		NULL),
	(7, 		NULL, 		2222, 		'unknown',	'suspended',	NULL, 		NULL),
	(8, 		NULL, 		NULL, 		'draft',	'suspended',	1,			'1'),
	(9, 		NULL, 		NULL, 		'unknown',	'suspended', 	2, 			'1'),
	(10,		NULL, 		NULL, 		'unknown',	'suspended', 	4, 			'4');


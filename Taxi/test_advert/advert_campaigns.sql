INSERT INTO eats_restapp_marketing.advert (
	id,
	updated_at,
	place_id,
	campaign_id,
	group_id,
	ad_id,
	banner_id,
	is_active,
	passport_id,
	averagecpc
) VALUES
	(1, NOW(), 53468, 399264, 4, 5, 1, false, 1229582676, 10),
    (
		2,
		cast('2015-05-01 11:25:00 america/caracas' as TIMESTAMPTZ),
		3965, 399265, 4, NULL, NULL, false, 1229582678, 10
	),
    (3, NOW(), 2464, 399266, 4, 5, 1, true, 1229582676, 10),
    (4, NOW(), 2465, 399267, 4, 5, NULL, false, NULL, 10),
    (5, NOW(), 18536, 399268, 5, 6, 2, false, 1229582676, 10);

INSERT INTO eats_restapp_marketing.advert_for_create (
	advert_id,
	token_id,
	averagecpc
)
VALUES
(5, 1, 25000000);

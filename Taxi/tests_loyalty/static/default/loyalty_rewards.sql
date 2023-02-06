-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */

INSERT INTO loyalty.rewards
(
  id,
  zone,
  status,
  reward,
  title_key,
  description_key,
  navigate_type,
  can_be_locked,
  lock_reasons,
  updated,
  created
)
VALUES
(
  'bb331ff042b68d75d0bd708488fb4711',
  'moscow',
  'bronze',
  'bank',
  'loyalty.reward.title_bank',
  'loyalty.reward.description_bank',
  'navigate_loyalty_bank_cards',
  false,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4712',
  'moscow',
  'silver',
  'bank',
  'loyalty.reward.title_bank',
  'loyalty.reward.description_bank',
  'navigate_loyalty_bank_cards',
  false,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4714',
  'moscow',
  'silver',
  'reposition',
  'loyalty.reward.title_reposition',
  'loyalty.reward.description_reposition',
  'navigate_loyalty_info',
  true,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4715',
  'moscow',
  'gold',
  'point_b',
  'loyalty.reward.title_point_b',
  'loyalty.reward.description_point_b',
  'navigate_loyalty_info',
  false,
  (null, ARRAY['bad_driver'])::loyalty.lock_reasons_t,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4713',
  'moscow',
  'gold',
  'dispatch',
  'loyalty.reward.title_dispatch',
  'loyalty.reward.description_dispatch',
  'navigate_loyalty_info',
  true,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4716',
  'moscow',
  'platinum',
  'point_b',
  'loyalty.reward.title_point_b',
  'loyalty.reward.description_point_b',
  'navigate_loyalty_info',
  true,
  (90, null)::loyalty.lock_reasons_t,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4717',
  'minsk',
  'bronze',
  'bank',
  'loyalty.reward.title_bank',
  'loyalty.reward.description_bank',
  'navigate_loyalty_bank_cards',
  false,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
)

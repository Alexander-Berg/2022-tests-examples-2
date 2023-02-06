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
  'bb331ff042b68d75d0bd708488fb4712',
  'moscow',
  'gold',
  'point_b',
  'loyalty.reward.title_point_b',
  'loyalty.reward.description_point_b',
  'navigate_loyalty_info',
  false,
  (NULL, ARRAY['bad_driver'])::loyalty.lock_reasons_t,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4713',
  'moscow',
  'gold',
  'recall',
  'loyalty.reward.title_recall',
  'loyalty.reward.description_recall',
  'navigate_loyalty_info',
  false,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4714',
  'moscow',
  'platinum',
  'point_b',
  'loyalty.reward.title_point_b',
  'loyalty.reward.description_point_b',
  'navigate_loyalty_info',
  true,
  (90, NULL)::loyalty.lock_reasons_t,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
),
(
  'bb331ff042b68d75d0bd708488fb4715',
  'moscow',
  'platinum',
  'recall',
  'loyalty.reward.title_recall',
  'loyalty.reward.description_recall',
  'navigate_loyalty_info',
  false,
  null,
  '2019-04-10 10:00:00.000000',
  '2019-04-10 10:00:00.000000'
)

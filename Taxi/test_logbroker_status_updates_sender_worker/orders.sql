INSERT INTO fleet.logbroker_status_updates_sender_state
(last_sent_seq_no)
VALUES (0);

INSERT INTO fleet.park_order (
  park_id,
  id,
  number,
  last_order_alias_id,
  preorder_request_id,
  status,
  tariff_class,
  personal_phone_id,
  forced_fixprice,
  address_from,
  addresses_to,
  geopoint_from,
  geopoints_to,
  created_at,
  booked_at,
  client_booked_at,
  driving_at,
  ended_at,
  duration_estimate,
  is_creator,
  event_index,
  last_contractor_park_id,
  last_contractor_id,
  last_contractor_car_id,
  record_created_at,
  record_updated_at,
  update_seq_no) 
VALUES (
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '1a0d128040eddf478dee60080d95ed7c',
  1917,
  '8febe5dd8c76d0feae134134055ecaa3',
  '7e190048-c339-4e7b-b1cc-c86dd1d8021b',
  'assigned',
  'business',
  '8b96d0d2f4f4459289e2da41a9b31cbd',
  null,
  'Platz der Republik, 1',
  '{Washingtonplatz, 1}',
  '{13.37513900000000000,52.51862300000000000}',
  '{{13.36930500000000000,52.52506600000000000}}',
  '2022-02-25 15:02:36.114000 +00:00',
  '2022-02-27 14:42:52.669000 +00:00',
  '2022-02-27 14:50:35.898000 +00:00',
  '2022-02-27 14:32:01.907000 +00:00',
  '2022-02-27 14:47:05.500000 +00:00',
  '0 years 0 mons 0 days 0 hours 3 mins 32.0 secs',
  true,
  9,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'cec9ebb1209a6adfe87088ff4b75714e',
  '1330db0845d085f77d26cc5c1f5f2805',
  '2022-02-25 15:02:55.649218 +00:00',
  '2022-02-27 14:47:06.485102 +00:00',
  1
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '7bc879bda461259b8e9a50449bf14fca',
  1918,
  '2ab3eff459cd2076a0d6212c73c38f34',
  '5f81d6e8-7afe-473e-82d1-7bba683216b6',
  'completed',
  'econom',
  '8b96d0d2f4f4459289e2da41a9b31cbd',
  null,
  'Danziger Straße, 77',
  '{Brunnenstraße, 163}',
  '{13.42547400000000000,52.53920400000000000}',
  '{{13.39797400000000000,52.53421800000000000}}',
  '2022-02-25 15:26:46.093000 +00:00',
  '2022-02-26 15:22:11.979000 +00:00',
  '2022-02-26 15:31:11.890000 +00:00',
  '2022-02-26 15:12:17.990000 +00:00',
  '2022-02-26 15:34:14.925000 +00:00',
  '0 years 0 mons 0 days 0 hours 4 mins 27.0 secs',
  true,
  9,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'a4ed7d0698ddff55ec80c9898eb1697a',
  '701cd26c15815d10cbbc02e365c7a4b7',
  '2022-02-25 15:26:47.886261 +00:00',
  '2022-02-26 15:34:16.575599 +00:00',
  10
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '82ced154f4ed113cb45b79c9258a7f74',
  1919,
  '3d1f3293a87815b6b0cb78f35bf4244a',
  '5f81d6e8-7afe-473e-82d1-7bba683216b6',
  'completed',
  'econom',
  '6b6664b6deb24e059ead33c180f0c958',
  null,
  'Danziger Straße, 77',
  '{Brunnenstraße, 163}',
  '{13.42547400000000000,52.53920400000000000}',
  '{{13.39797400000000000,52.53421800000000000}}',
  '2022-02-25 15:29:30.310000 +00:00',
  '2022-02-26 15:22:55.504000 +00:00',
  '2022-02-26 15:31:11.890000 +00:00',
  '2022-02-26 15:12:17.640000 +00:00',
  '2022-02-26 15:33:38.424000 +00:00',
  '0 years 0 mons 0 days 0 hours 4 mins 27.0 secs',
  true,
  9,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '67a288c7265f372e26bde693535b56f1',
  '44cca7e7b7dfbefda4c0269e2d78380e',
  '2022-02-25 15:29:45.716047 +00:00',
  '2022-02-26 15:33:39.431528 +00:00',
  9
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '3998d7c8ed411d49bf1d19f35b1735d4',
  1921,
  '479ad104ccbe11c1bb3a18692a2f204d',
  '5f81d6e8-7afe-473e-82d1-7bba683216b6',
  'completed',
  'econom',
  '6b6664b6deb24e059ead33c180f0c958',
  null,
  'Danziger Straße, 77',
  '{Brunnenstraße, 163}',
  '{13.42547400000000000,52.53920400000000000}',
  '{{13.39797400000000000,52.53421800000000000}}',
  '2022-02-25 17:08:55.680000 +00:00',
  '2022-02-26 15:23:04.142000 +00:00',
  '2022-02-26 15:31:11.890000 +00:00',
  '2022-02-26 15:12:16.217000 +00:00',
  '2022-02-26 15:32:09.684000 +00:00',
  '0 years 0 mons 0 days 0 hours 4 mins 27.0 secs',
  true,
  9,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '1229b050a50827bc9e1e340cc941b455',
  '271a4e82630f1b130e42d4d1690b081b',
  '2022-02-25 17:09:05.297881 +00:00',
  '2022-02-26 15:32:11.749231 +00:00',
  8
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '5c4d8a5bf62bcaa58b0d03de8e2c7bb3',
  1922,
  'fce18665627ecc87acfc8292f026dc0f',
  '5f81d6e8-7afe-473e-82d1-7bba683216b6',
  'completed',
  'econom',
  '6b6664b6deb24e059ead33c180f0c958',
  null,
  'Danziger Straße, 77',
  '{Brunnenstraße, 163}',
  '{13.42547400000000000,52.53920400000000000}',
  '{{13.39797400000000000,52.53421800000000000}}',
  '2022-02-25 17:10:47.610000 +00:00',
  '2022-02-26 15:24:56.606000 +00:00',
  '2022-02-26 15:31:11.890000 +00:00',
  '2022-02-26 15:12:18.466000 +00:00',
  '2022-02-26 15:30:03.487000 +00:00',
  '0 years 0 mons 0 days 0 hours 4 mins 27.0 secs',
  true,
  9,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'aa25b6beb9823d73d16cb5fb4344340d',
  'eaa2a259c585335fd2928e7e8a7302c6',
  '2022-02-25 17:10:56.356697 +00:00',
  '2022-02-26 15:30:06.032047 +00:00',
  7
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '6d78eb5520d6cc01b5eae78c4d238243',
  1916,
  'c45c38ddef95c98b8db457b1a50893a8',
  '4b4418a1-b2f4-4a0c-aabe-e98f24af95de',
  'completed',
  'business',
  '8b96d0d2f4f4459289e2da41a9b31cbd',
  null,
  'Platz der Republik, 1',
  '{Washingtonplatz, 1}',
  '{13.37513900000000000,52.51862300000000000}',
  '{{13.36930500000000000,52.52506600000000000}}',
  '2022-02-25 14:45:35.018000 +00:00',
  '2022-02-26 14:35:44.378000 +00:00',
  '2022-02-26 14:50:03.911000 +00:00',
  '2022-02-26 14:30:16.701000 +00:00',
  '2022-02-26 14:39:33.404000 +00:00',
  '0 years 0 mons 0 days 0 hours 3 mins 32.0 secs',
  true,
  9,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'cec9ebb1209a6adfe87088ff4b75714e',
  '1330db0845d085f77d26cc5c1f5f2805',
  '2022-02-25 14:45:38.179017 +00:00',
  '2022-02-26 14:39:34.889832 +00:00',
  6
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '4972987590a9c7dc9ae6de57f81c79d3',
  1920,
  null,
  null,
  'expired',
  'econom',
  '4b9ba1dddd56419585000f54316e2468',
  null,
  'Seestrasse',
  '{Seestraße, 41}',
  '{13.34253500000000000,52.54176700000000000}',
  '{{13.68315300000000000,52.43871300000000000}}',
  '2022-02-25 16:05:34.647000 +00:00',
  '2022-02-25 16:11:09.083000 +00:00',
  '2022-02-25 16:15:35.736000 +00:00',
  '2022-02-25 16:05:43.935000 +00:00',
  '2022-02-25 17:11:09.088000 +00:00',
  '0 years 0 mons 0 days 0 hours 46 mins 42.0 secs',
  true,
  8,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'cec9ebb1209a6adfe87088ff4b75714e',
  '1330db0845d085f77d26cc5c1f5f2805',
  '2022-02-25 16:05:36.727798 +00:00',
  '2022-02-25 17:11:10.384139 +00:00',
  5
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '10eada445af2288c9d75742fee1c50c8',
  1915,
  '991e4d4399b22390b1e4a3cf56925100',
  null,
  'completed',
  'econom',
  'b9352c28a3664c7dba4e591efadc53e2',
  null,
  'Washingtonplatz, 1',
  '{Unter den Linden, 80}',
  '{13.36930500000000000,52.52506600000000000}',
  '{{13.38009300000000000,52.51645700000000000}}',
  '2022-02-25 14:07:40.961000 +00:00',
  '2022-02-25 14:10:43.132000 +00:00',
  '2022-02-25 14:17:41.824000 +00:00',
  '2022-02-25 14:07:46.722000 +00:00',
  '2022-02-25 14:11:52.884000 +00:00',
  '0 years 0 mons 0 days 0 hours 4 mins 57.0 secs',
  true,
  8,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'a47a433ff29517cd988022d72cb729c9',
  '517a0b5d367e7e5879a9b985b6b43926',
  '2022-02-25 14:07:42.621612 +00:00',
  '2022-02-25 14:11:53.775094 +00:00',
  4
),(
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  '1ba9a26ae45c2fcabfa11aee9dfd3813',
  1914,
  '25a10a0e13e9241590bce2895050187b',
  null,
  'completed',
  'econom',
  'ff6766e0b5ec47eeb7a90e2441b58cb6',
  null,
  'Unter den Linden, 80',
  '{Washingtonplatz, 1}',
  '{13.38009300000000000,52.51645700000000000}',
  '{{13.36930500000000000,52.52506600000000000}}',
  '2022-02-25 13:28:38.458000 +00:00',
  '2022-02-25 13:32:00.828000 +00:00',
  '2022-02-25 13:38:39.204000 +00:00',
  '2022-02-25 13:29:04.974000 +00:00',
  '2022-02-25 13:45:20.359000 +00:00',
  '0 years 0 mons 0 days 0 hours 6 mins 19.0 secs',
  true,
  8,
  'c5cdea22ad6b4e4da8f3fdbd4bddc2e7',
  'a47a433ff29517cd988022d72cb729c9',
  '517a0b5d367e7e5879a9b985b6b43926',
  '2022-02-25 13:28:40.199447 +00:00',
  '2022-02-25 13:45:21.754505 +00:00',
  3
),(
  '7f74df331eb04ad78bc2ff25ff88a8f2',
  'f7cf24e6b13dde30b3b272f7a2c8478f',
  43,
  '9f9235affe1fdce287f4ac1ba8bd051a',
  null,
  'completed',
  'econom',
  '8b96d0d2f4f4459289e2da41a9b31cbd',
  null,
  'Lomonosovsky Avenue, 29к3',
  '{Michurinsky Avenue, 34}',
  '{37.51448100000000000,55.70512400000000000}',
  '{{37.49876400000000000,55.69816600000000000}}',
  '2022-02-24 10:09:06.852000 +00:00',
  '2022-02-25 09:51:06.484000 +00:00',
  null,
  '2022-02-25 09:50:13.889000 +00:00',
  '2022-02-25 09:56:31.191000 +00:00',
  null,
  false,
  9,
  '7f74df331eb04ad78bc2ff25ff88a8f2',
  'b8960e6325cc4780b9479a63fd7af46d',
  'c63355ff0b1d4f5f99e458a890ff13bb',
  '2022-02-25 09:50:29.801422 +00:00',
  '2022-02-25 10:12:00.923500 +00:00',
  2
);